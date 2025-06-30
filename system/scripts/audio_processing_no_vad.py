#!/usr/bin/env python3
"""
Audio Processing Pipeline WITHOUT VAD (Voice Activity Detection)
This version skips VAD to avoid CUDA errors and ensure stable processing
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from tqdm import tqdm

# Импорты из модуля audio
try:
    audio_module_path = Path(__file__).parent / 'audio'
    sys.path.append(str(audio_module_path))
    
    from audio import (
        GPUMemoryManager, ModelManager,
        process_audio_file_optimized, parallel_audio_processing_optimized,
        process_multiple_files_parallel_optimized,
        clean_audio_with_demucs_optimized, 
        diarize_with_pyannote_optimized,
        split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized,
        get_mp3_duration, setup_logging, copy_results_to_output_optimized,
        get_optimal_workers, setup_gpu_optimization, 
        MAX_WORKERS, GPU_MEMORY_LIMIT, BATCH_SIZE
    )
    from config import get_token, token_exists
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Audio Processing Pipeline WITHOUT VAD")
    parser.add_argument('--input', '-i', help='Path to audio file (mp3/wav) or folder with files')
    parser.add_argument('--output', '-o', help='Folder for saving results')
    parser.add_argument('--mode', type=str, default='multithreaded', choices=['single', 'multithreaded'],
                        help='Processing mode: single (sequential) or multithreaded (parallel, recommended)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    # Pre-configured optimal parameters WITHOUT VAD
    if args.mode == 'multithreaded':
        # Multi-threaded mode - optimized for speed
        chunk_duration = 600  # 10 minutes
        min_speaker_segment = 0.1  # 0.1 seconds (no limit)
        steps = ['split', 'denoise', 'diar']  # NO VAD
        split_method = 'smart_multithreaded'  # New smart splitter
        use_gpu = True
        force_cpu_vad = True  # Force CPU for VAD stability
        parallel = True
        workers = None  # Auto-determined
    else:
        # Single-threaded mode - optimized for stability
        chunk_duration = 600  # 10 minutes
        min_speaker_segment = 0.1  # 0.1 seconds (no limit)
        steps = ['split', 'denoise', 'diar']  # NO VAD
        split_method = 'word_boundary'  # More stable for single-threaded
        use_gpu = True
        force_cpu_vad = True  # Force CPU for stability
        parallel = False
        workers = 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Starting audio processing pipeline WITHOUT VAD ===")
    
    # Setup optimization for RTX 5080
    print("\n" + "="*60)
    print("AUDIO PROCESSING WITHOUT VAD (NO SILENCE REMOVAL)")
    print("="*60)
    
    # GPU setup
    gpu_available = setup_gpu_optimization()
    if gpu_available:
        print("✓ GPU optimization applied")
    else:
        print("⚠ GPU not available, using CPU")
        use_gpu = False
        force_cpu_vad = True
    
    # Determine optimal number of processes for multithreaded mode
    if args.mode == 'multithreaded':
        optimal_workers = get_optimal_workers()
        if workers is None:
            workers = optimal_workers
        else:
            workers = min(workers, optimal_workers)
        print(f"✓ Multi-threaded mode: {workers} parallel processes")
    else:
        workers = 1
        print("✓ Single-threaded mode: sequential processing")
    
    # Show mode information
    print(f"✓ Processing mode: {args.mode}")
    print(f"✓ VAD (silence removal): DISABLED (to avoid CUDA errors)")
    if args.mode == 'multithreaded':
        print(f"  - Smart multithreaded splitting with GPU acceleration")
        print(f"  - Parallel processing for maximum speed")
        print(f"  - Demucs denoising on GPU")
        print(f"  - Diarization on GPU")
    else:
        print(f"  - Word boundary splitting for stability")
        print(f"  - Sequential processing for reliability")
        print(f"  - Demucs denoising on GPU")
        print(f"  - Diarization on GPU")
    
    # Interactive mode or get parameters
    if args.interactive or not args.input or not args.output:
        print("\n" + "="*60)
        print("AUDIO PROCESSING WITHOUT VAD")
        print("="*60)
        
        # Get input file/folder
        if not args.input:
            print("\nEnter path to audio file or folder with audio files:")
            print("Examples:")
            print("  - audio.mp3")
            print("  - C:\\path\\to\\audio.mp3")
            print("  - audio_folder")
            args.input = input("Input file/folder: ").strip().strip('"')
        
        # Get output folder
        if not args.output:
            print("\nEnter folder for saving results:")
            print("Examples:")
            print("  - results")
            print("  - C:\\path\\to\\results")
            args.output = input("Output folder: ").strip().strip('"')
        
        # Show current settings
        print(f"\nCurrent settings ({args.mode} mode):")
        print(f"  - Chunk duration: {chunk_duration} sec (10 minutes)")
        print(f"  - Minimum speaker segment: {min_speaker_segment} sec (no limit)")
        print(f"  - Splitting method: {split_method}")
        print(f"  - Processing stages: {', '.join(steps)} (NO VAD)")
        print(f"  - GPU acceleration: {'Yes' if use_gpu else 'No'}")
        print(f"  - VAD device: DISABLED")
        print(f"  - Parallel processing: {'Yes' if parallel else 'No'}")
        print(f"  - Number of processes: {workers}")
        
        # Ask to change mode
        print(f"\nCurrent mode: {args.mode}")
        print("  single - Sequential processing (stable, slower)")
        print("  multithreaded - Parallel processing (fast, recommended)")
        change_mode = input(f"Change mode? (y/n, default n): ").strip().lower()
        if change_mode in ['y', 'yes', 'da']:
            new_mode = input("Enter mode (single/multithreaded): ").strip().lower()
            if new_mode in ['single', 'multithreaded']:
                args.mode = new_mode
                # Update parameters based on new mode
                if args.mode == 'multithreaded':
                    split_method = 'smart_multithreaded'
                    use_gpu = True
                    force_cpu_vad = True
                    parallel = True
                    workers = get_optimal_workers()
                else:
                    split_method = 'word_boundary'
                    use_gpu = True
                    force_cpu_vad = True
                    parallel = False
                    workers = 1
                
                print(f"\nUpdated settings ({args.mode} mode):")
                print(f"  - Splitting method: {split_method}")
                print(f"  - GPU acceleration: {'Yes' if use_gpu else 'No'}")
                print(f"  - VAD device: DISABLED")
                print(f"  - Parallel processing: {'Yes' if parallel else 'No'}")
                print(f"  - Number of processes: {workers}")
        
        print(f"\nStarting processing with parameters:")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")
        print(f"  Mode: {args.mode}")
        print(f"  Splitting: {split_method}")
        print(f"  GPU: {'Yes' if use_gpu else 'No'}")
        print(f"  Parallel: {'Yes' if parallel else 'No'}")
        print(f"  VAD: DISABLED (no silence removal)")
        
        confirm = input("\nContinue? (y/n, default y): ").strip().lower()
        if confirm in ['n', 'no', 'net']:
            print("Processing cancelled.")
            return

    logger.info(f"Input parameters: {vars(args)}")
    logger.info(f"Mode: {args.mode}, Split method: {split_method}, GPU: {use_gpu}, Parallel: {parallel}")

    input_path = Path(args.input)
    output_dir = Path(args.output)

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
    
    if parallel and len(files) > 1:
        # Многопоточная обработка
        print(f"\nStarting multithreaded processing for {len(files)} files...")
        logger.info("Using multithreaded processing with speaker organization")
        
        organized_speakers = process_multiple_files_parallel_optimized(
            files, output_dir, steps, chunk_duration,
            min_speaker_segment, split_method, use_gpu, logger
        )
        
        # Показываем результаты
        print(f"\nMultithreaded processing completed!")
        print(f"Total speakers found: {len(organized_speakers)}")
        
        for speaker_name, speaker_data in organized_speakers.items():
            print(f"  Speaker {speaker_name}: {len(speaker_data['files'])} audio files")
            print(f"    Folder: {speaker_data['folder']}")
        
    else:
        # Однопоточная обработка
        print(f"\nStarting single-threaded processing...")
        logger.info("Using single-threaded processing with speaker organization")
        
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
                        min_speaker_segment, split_method, use_gpu,
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
            print(f"\nSingle-threaded processing completed!")
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
    print("\nNOTE: VAD (silence removal) was DISABLED to avoid CUDA errors")
    print("Audio files contain original silence segments")
    
    # Show performance statistics
    if parallel and len(files) > 1:
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  - Files processed: {len(files)}")
        print(f"  - Time per file: {total_time/len(files):.1f} seconds")
        print(f"  - Speedup from parallelization: ~{workers}x")
        print(f"  - GPU used: {'Yes' if gpu_available else 'No'}")
        print(f"  - Mode: Multithreaded with smart splitting")
        print(f"  - VAD: DISABLED (no silence removal)")
        print(f"  - Diarization: Locked (single thread)")
    else:
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  - Files processed: {len(files)}")
        print(f"  - Total time: {total_time/60:.1f} minutes")
        print(f"  - GPU used: {'Yes' if gpu_available else 'No'}")
        print(f"  - Mode: Single-threaded for stability")
        print(f"  - VAD: DISABLED (no silence removal)")
        print(f"  - Diarization: Sequential")

if __name__ == "__main__":
    main() 