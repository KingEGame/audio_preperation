#!/usr/bin/env python3
"""
Optimized Audio Processing Pipeline with Advanced GPU Management
Stages: splitting, denoising, silence removal, diarization
Optimized for RTX 5080, 32GB RAM, R5 5600X

IMPROVEMENTS:
- Advanced GPU memory management with automatic cleanup
- Model caching and reuse across processes
- Improved multiprocessing with proper resource management
- Better error handling and recovery
- Optimized processing pipeline with memory monitoring
- Modular architecture using /audio package
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from tqdm import tqdm

# Импорты из нового модуля /audio
try:
    # Добавляем путь к модулю audio
    audio_module_path = Path(__file__).parent / 'audio'
    sys.path.append(str(audio_module_path))
    
    # Импортируем все необходимые функции из модуля audio
    from audio import (
        GPUMemoryManager, ModelManager,
        process_audio_file_optimized, parallel_audio_processing_optimized,
        process_multiple_files_parallel_optimized,
        clean_audio_with_demucs_optimized, remove_silence_with_silero_optimized, 
        diarize_with_pyannote_optimized,
        split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized,
        get_mp3_duration, setup_logging, copy_results_to_output_optimized,
        get_optimal_workers, setup_gpu_optimization, 
        MAX_WORKERS, GPU_MEMORY_LIMIT, BATCH_SIZE
    )
    # Импорт функций конфигурации
    from config import get_token, token_exists
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed")
    print(f"Audio module path: {audio_module_path}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Optimized Audio Processing Pipeline: splitting, denoising, silence removal, diarization with speaker separation.")
    parser.add_argument('--input', '-i', help='Path to audio file (mp3/wav) or folder with files')
    parser.add_argument('--output', '-o', help='Folder for saving results')
    parser.add_argument('--chunk_duration', type=int, default=600, help='Maximum chunk duration (seconds), default 600 (10 minutes)')
    parser.add_argument('--min_speaker_segment', type=float, default=0.1, help='Minimum speaker segment duration (seconds), default 0.1 (use 0 for no limit)')
    parser.add_argument('--no_duration_limit', action='store_true', help='Disable minimum duration limit for speaker segments')
    parser.add_argument('--steps', nargs='+', default=['split','denoise','vad', 'diar'],
                        help='Processing stages: split, denoise, vad, diar')
    parser.add_argument('--split_method', type=str, default='word_boundary', choices=['simple', 'word_boundary'],
                        help='Splitting method: simple or word_boundary')
    parser.add_argument('--use_gpu', action='store_true', help='Use GPU for VAD (default CPU for stability)')
    parser.add_argument('--force_cpu_vad', action='store_true', help='Force CPU usage for VAD (for compatibility)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode with parameter prompts')
    parser.add_argument('--parallel', action='store_true', default=True, help='Use parallel processing (enabled by default)')
    parser.add_argument('--workers', type=int, help='Number of worker processes (auto-determined)')
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Starting optimized audio processing pipeline ===")
    
    # Setup optimization for RTX 5080
    print("\n" + "="*60)
    print("OPTIMIZATION FOR RTX 5080 + R5 5600X + 32GB RAM")
    print("="*60)
    
    # GPU setup
    gpu_available = setup_gpu_optimization()
    if gpu_available:
        print("✓ GPU optimization applied")
        args.use_gpu = True  # Automatically enable GPU
    else:
        print("⚠ GPU not available, using CPU")
    
    # VAD GPU usage logic
    if args.force_cpu_vad:
        print("⚠ VAD forced to use CPU for compatibility")
        args.use_gpu = False
    elif gpu_available:
        print("✓ VAD will attempt GPU usage with CPU fallback")
    else:
        print("⚠ VAD using CPU (GPU not available)")
    
    # Determine optimal number of processes
    optimal_workers = get_optimal_workers()
    if args.workers:
        optimal_workers = min(args.workers, optimal_workers)
    
    print(f"✓ Optimal number of processes: {optimal_workers}")
    print(f"✓ Parallel parts processing: {'Enabled' if args.parallel else 'Disabled'}")
    
    # Interactive mode or get parameters
    if args.interactive or not args.input or not args.output:
        print("\n" + "="*60)
        print("AUDIO PROCESSING PIPELINE (OPTIMIZED)")
        print("="*60)
        
        # Get input file/folder
        if not args.input:
            print("\nEnter path to audio file or folder with audio files:")
            print("Examples:")
            print("  - audio.mp3")
            print("  - C:\\path\\to\\audio.mp3")
            print("  - audio_folder")
            print("  - C:\\path\\to\\audio_folder")
            args.input = input("Input file/folder: ").strip().strip('"')
        
        # Get output folder
        if not args.output:
            print("\nEnter folder for saving results:")
            print("Examples:")
            print("  - results")
            print("  - C:\\path\\to\\results")
            args.output = input("Output folder: ").strip().strip('"')
        
        # Additional settings
        print(f"\nCurrent settings:")
        print(f"  - Chunk duration: {args.chunk_duration} sec")
        print(f"  - Minimum speaker segment duration: {args.min_speaker_segment} sec")
        print(f"  - No duration limit: {'Yes' if args.no_duration_limit else 'No'}")
        print(f"  - Splitting method: {args.split_method}")
        print(f"  - Stages: {', '.join(args.steps)}")
        print(f"  - Parallel parts processing: {'Enabled' if args.parallel else 'Disabled'}")
        print(f"  - Number of processes: {optimal_workers}")
        print(f"  - GPU: {'Enabled' if gpu_available else 'Disabled'}")
        
        change_settings = input("\nChange settings? (y/n, default n): ").strip().lower()
        if change_settings in ['y', 'yes', 'da']:
            # Chunk duration
            new_duration = input(f"Chunk duration in seconds (default {args.chunk_duration}): ").strip()
            if new_duration and new_duration.isdigit():
                args.chunk_duration = int(new_duration)
            
            # Minimum speaker segment duration
            new_min_segment = input(f"Minimum speaker segment duration in seconds (default {args.min_speaker_segment}, use 0 for no limit): ").strip()
            if new_min_segment and new_min_segment.replace('.', '').isdigit():
                args.min_speaker_segment = float(new_min_segment)
            
            # No duration limit
            no_limit_choice = input("Disable minimum duration limit? (y/n, default n): ").strip().lower()
            args.no_duration_limit = no_limit_choice in ['y', 'yes', 'da']
            
            # Splitting method
            print("\nSplitting method:")
            print("  simple - simple time-based splitting")
            print("  word_boundary - splitting at word boundaries (recommended)")
            new_method = input(f"Method (default {args.split_method}): ").strip()
            if new_method in ['simple', 'word_boundary']:
                args.split_method = new_method
            
            # Processing stages
            print("\nProcessing stages:")
            print("  split - split into chunks")
            print("  denoise - noise removal (Demucs)")
            print("  vad - silence removal (Silero VAD)")
            print("  diar - speaker diarization (PyAnnote)")
            new_steps = input(f"Stages separated by space (default {' '.join(args.steps)}): ").strip()
            if new_steps:
                args.steps = new_steps.split()
            
            # Parallel parts processing
            parallel_choice = input("Use parallel parts processing? (y/n, default y): ").strip().lower()
            args.parallel = parallel_choice not in ['n', 'no', 'net']
            
            # Number of processes
            new_workers = input(f"Number of processes for parts (default {optimal_workers}): ").strip()
            if new_workers and new_workers.isdigit():
                optimal_workers = min(int(new_workers), optimal_workers)
        
        print(f"\nStarting processing with parameters:")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")
        print(f"  Chunk duration: {args.chunk_duration} sec")
        print(f"  Minimum speaker segment duration: {args.min_speaker_segment} sec")
        print(f"  No duration limit: {'Yes' if args.no_duration_limit else 'No'}")
        print(f"  Splitting method: {args.split_method}")
        print(f"  Stages: {', '.join(args.steps)}")
        print(f"  Parallel parts processing: {'Yes' if args.parallel else 'No'}")
        print(f"  Number of processes: {optimal_workers}")
        print(f"  GPU: {'Yes' if gpu_available else 'No'}")
        
        confirm = input("\nContinue? (y/n, default y): ").strip().lower()
        if confirm in ['n', 'no', 'net']:
            print("Processing cancelled.")
            return

    logger.info(f"Input parameters: {vars(args)}")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    chunk_duration = args.chunk_duration
    steps = args.steps
    split_method = args.split_method

    # Check input file/folder existence
    if not input_path.exists():
        logger.error(f"Input file/folder not found: {input_path}")
        print(f"\nERROR: File or folder '{input_path}' does not exist!")
        print("Check the path and try again.")
        return

    # Check diarization token if diarization is requested
    if 'diar' in steps:
        if not token_exists():
            print(f"\n{'='*60}")
            print("DIARIZATION TOKEN NOT FOUND")
            print(f"{'='*60}")
            print("Diarization requires a HuggingFace token.")
            print()
            print("Options:")
            print("1. Setup diarization now (recommended)")
            print("2. Continue without diarization")
            print("3. Cancel processing")
            print()
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                print("\nSetting up diarization...")
                import subprocess
                try:
                    subprocess.run(["system\\fixes\\quick_diarization_fix.bat"], check=True)
                    print("Diarization setup completed!")
                except subprocess.CalledProcessError:
                    print("Diarization setup failed. Continuing without diarization.")
                    steps = [s for s in steps if s != 'diar']
                    print(f"Updated steps: {', '.join(steps)}")
            elif choice == "2":
                print("Continuing without diarization...")
                steps = [s for s in steps if s != 'diar']
                print(f"Updated steps: {', '.join(steps)}")
            else:
                print("Processing cancelled.")
                return
        else:
            token = get_token()
            if not token:
                print(f"\n{'='*60}")
                print("DIARIZATION TOKEN IS EMPTY")
                print(f"{'='*60}")
                print("The token file exists but is empty.")
                print()
                print("Options:")
                print("1. Setup diarization now (recommended)")
                print("2. Continue without diarization")
                print("3. Cancel processing")
                print()
                choice = input("Enter choice (1-3): ").strip()
                
                if choice == "1":
                    print("\nSetting up diarization...")
                    import subprocess
                    try:
                        subprocess.run(["system\\fixes\\quick_diarization_fix.bat"], check=True)
                        print("Diarization setup completed!")
                    except subprocess.CalledProcessError:
                        print("Diarization setup failed. Continuing without diarization.")
                        steps = [s for s in steps if s != 'diar']
                        print(f"Updated steps: {', '.join(steps)}")
                elif choice == "2":
                    print("Continuing without diarization...")
                    steps = [s for s in steps if s != 'diar']
                    print(f"Updated steps: {', '.join(steps)}")
                else:
                    print("Processing cancelled.")
                    return

    files = []
    if input_path.is_file():
        files = [input_path]
        logger.info(f"Processing single file: {input_path}")
        print(f"\nFound file: {input_path}")
    elif input_path.is_dir():
        files = list(input_path.glob('*.mp3')) + list(input_path.glob('*.wav'))
        logger.info(f"Found {len(files)} files in folder: {input_path}")
        print(f"\nFound {len(files)} audio files in folder: {input_path}")
        if not files:
            print("No audio files (.mp3 or .wav) found in folder")
            return
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")
    else:
        logger.error(f"File or folder not found: {input_path}")
        return

    # Create output folder
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nResults will be saved in: {output_dir}")

    # Start timing
    start_time = time.time()
    
    if args.parallel and len(files) > 1:
        # Новая многопоточная обработка с организацией по спикерам
        print(f"\nStarting new multithreaded processing for {len(files)} files...")
        logger.info("Using new multithreaded processing with speaker organization")
        
        organized_speakers = process_multiple_files_parallel_optimized(
            files, output_dir, steps, chunk_duration,
            args.min_speaker_segment if not args.no_duration_limit else 0.0, 
            split_method, args.use_gpu, args.force_cpu_vad, logger
        )
        
        # Показываем результаты
        print(f"\nMultithreaded processing completed!")
        print(f"Total speakers found: {len(organized_speakers)}")
        
        for speaker_name, speaker_data in organized_speakers.items():
            print(f"  Speaker {speaker_name}: {len(speaker_data['files'])} audio files")
            print(f"    Folder: {speaker_data['folder']}")
        
    else:
        # Обработка одного файла с новой архитектурой
        print(f"\nStarting single file processing...")
        logger.info("Using single file processing with speaker organization")
        
        # Инициализируем менеджеры
        gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
        model_manager = ModelManager(gpu_manager)
        
        try:
            # Обрабатываем файлы
            print(f"\nStarting processing of {len(files)} files...")
            all_organized_speakers = {}
            
            with tqdm(total=len(files), desc="Processing files", unit="file") as pbar_files:
                for audio in files:
                    logger.info(f"\n=== Processing file: {audio} ===")
                    print(f"\n{'='*50}")
                    print(f"Processing: {audio.name}")
                    print(f"{'='*50}")
                    
                    # Используем новую функцию для одного файла
                    from audio.processors import process_file_multithreaded_optimized
                    organized_speakers = process_file_multithreaded_optimized(
                        audio, output_dir, steps, chunk_duration,
                        args.min_speaker_segment if not args.no_duration_limit else 0.0, 
                        split_method, args.use_gpu, args.force_cpu_vad,
                        logger, model_manager, gpu_manager
                    )
                    
                    # Объединяем результаты
                    for speaker_name, speaker_data in organized_speakers.items():
                        if speaker_name not in all_organized_speakers:
                            all_organized_speakers[speaker_name] = speaker_data
                        else:
                            # Добавляем файлы к существующему спикеру
                            all_organized_speakers[speaker_name]['files'].extend(speaker_data['files'])
                            all_organized_speakers[speaker_name]['metadata'].extend(speaker_data['metadata'])
                    
                    pbar_files.update(1)
            
            # Показываем результаты
            print(f"\nSingle file processing completed!")
            print(f"Total speakers found: {len(all_organized_speakers)}")
            
            for speaker_name, speaker_data in all_organized_speakers.items():
                print(f"  Speaker {speaker_name}: {len(speaker_data['files'])} audio files")
                print(f"    Folder: {speaker_data['folder']}")
            
        finally:
            # Очистка менеджеров
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
    
    # Calculate execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info("=== Processing completed ===")
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETED!")
    print(f"{'='*60}")
    print(f"Total execution time: {total_time/60:.1f} minutes")
    print(f"Results saved in: {output_dir}")
    print("\nResults structure:")
    
    # Show what was created
    if output_dir.exists():
        # Show speaker folders if diarization was performed
        if 'diar' in steps:
            speaker_folders = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('speaker_')]
            if speaker_folders:
                print(f"  speaker_* folders ({len(speaker_folders)} folders)")
                for speaker_folder in speaker_folders:
                    audio_files = list(speaker_folder.glob('*.wav'))
                    metadata_files = list(speaker_folder.glob('metadata_*.txt'))
                    info_files = list(speaker_folder.glob('*_info.txt'))
                    
                    print(f"    - {speaker_folder.name}:")
                    print(f"      Audio files: {len(audio_files)}")
                    print(f"      Metadata files: {len(metadata_files)}")
                    print(f"      Info files: {len(info_files)}")
                    
                    # Показываем первые несколько аудиофайлов
                    for audio_file in audio_files[:3]:
                        try:
                            duration_str = get_mp3_duration(str(audio_file))
                            print(f"        {audio_file.name}: {duration_str}")
                        except:
                            print(f"        {audio_file.name}")
                    
                    if len(audio_files) > 3:
                        print(f"        ... and {len(audio_files) - 3} more files")
    
    print(f"\nProcessing log saved in: audio_processing.log")
    print(f"Temporary files automatically deleted")
    
    # Show performance statistics
    if args.parallel and len(files) > 1:
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  - Files processed: {len(files)}")
        print(f"  - Time per file: {total_time/len(files):.1f} seconds")
        print(f"  - Speedup from parallelization: ~{optimal_workers}x")
        print(f"  - GPU used: {'Yes' if gpu_available else 'No'}")
        print(f"  - Logic: New multithreaded processing with speaker organization")
        print(f"  - Threads per file: 4 (max)")
        print(f"  - Diarization: Locked (single thread)")
    else:
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  - Files processed: {len(files)}")
        print(f"  - Total time: {total_time/60:.1f} minutes")
        print(f"  - GPU used: {'Yes' if gpu_available else 'No'}")
        print(f"  - Logic: Single file processing with speaker organization")
        print(f"  - Threads per file: 4 (max)")
        print(f"  - Diarization: Locked (single thread)")

if __name__ == "__main__":
    main() 