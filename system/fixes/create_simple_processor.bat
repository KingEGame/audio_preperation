@echo off
echo Creating simplified audio processing script...

(
echo #!/usr/bin/env python3
echo """
echo Simplified Audio Processing Pipeline with 2 Modes
echo - Single-threaded: Sequential processing ^(stable, slower^)
echo - Multi-threaded: Parallel processing ^(fast, recommended^)
echo.
echo Optimized for RTX 5080, 32GB RAM, R5 5600X
echo """
echo.
echo import os
echo import sys
echo import argparse
echo import logging
echo import time
echo from pathlib import Path
echo from tqdm import tqdm
echo.
echo # Импорты из модуля audio
echo try:
echo     audio_module_path = Path^(__file__^).parent / 'audio'
echo     sys.path.append^(str^(audio_module_path^)^)
echo.    
echo     from audio import ^(
echo         GPUMemoryManager, ModelManager,
echo         process_audio_file_optimized, parallel_audio_processing_optimized,
echo         process_multiple_files_parallel_optimized,
echo         clean_audio_with_demucs_optimized, remove_silence_with_silero_optimized, 
echo         diarize_with_pyannote_optimized,
echo         split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized,
echo         get_mp3_duration, setup_logging, copy_results_to_output_optimized,
echo         get_optimal_workers, setup_gpu_optimization, 
echo         MAX_WORKERS, GPU_MEMORY_LIMIT, BATCH_SIZE
echo     ^)
echo     from config import get_token, token_exists
echo except ImportError as e:
echo     print^(f"Import error: {e}"^)
echo     print^("Make sure all dependencies are installed"^)
echo     sys.exit^(1^)
echo.
echo def main^(^):
echo     parser = argparse.ArgumentParser^(description="Simplified Audio Processing Pipeline with 2 modes"^)
echo     parser.add_argument^('--input', '-i', help='Path to audio file ^(mp3/wav^) or folder with files'^)
echo     parser.add_argument^('--output', '-o', help='Folder for saving results'^)
echo     parser.add_argument^('--mode', type=str, default='multithreaded', choices=['single', 'multithreaded'],
echo                         help='Processing mode: single ^(sequential^) or multithreaded ^(parallel, recommended^)'^)
echo     parser.add_argument^('--verbose', '-v', action='store_true', help='Verbose logging'^)
echo     parser.add_argument^('--interactive', action='store_true', help='Interactive mode'^)
echo     args = parser.parse_args^(^)
echo.
echo     # Pre-configured optimal parameters
echo     if args.mode == 'multithreaded':
echo         # Multi-threaded mode - optimized for speed
echo         chunk_duration = 600  # 10 minutes
echo         min_speaker_segment = 0.1  # 0.1 seconds ^(no limit^)
echo         steps = ['split', 'denoise', 'vad', 'diar']
echo         split_method = 'smart_multithreaded'  # New smart splitter
echo         use_gpu = True
echo         force_cpu_vad = False
echo         parallel = True
echo         workers = get_optimal_workers^(^)
echo     else:
echo         # Single-threaded mode - optimized for stability
echo         chunk_duration = 600  # 10 minutes
echo         min_speaker_segment = 0.1  # 0.1 seconds ^(no limit^)
echo         steps = ['split', 'denoise', 'vad', 'diar']
echo         split_method = 'word_boundary'  # More stable for single-threaded
echo         use_gpu = True
echo         force_cpu_vad = True  # Force CPU for stability
echo         parallel = False
echo         workers = 1
echo.
echo     # Setup logging
echo     log_level = logging.DEBUG if args.verbose else logging.INFO
echo     logger = setup_logging^(log_level^)
echo.    
echo     logger.info^("=== Starting simplified audio processing pipeline ==="^)
echo.    
echo     # Setup optimization for RTX 5080
echo     print^("\n" + "="*60^)
echo     print^("OPTIMIZATION FOR RTX 5080 + R5 5600X + 32GB RAM"^)
echo     print^("="*60^)
echo.    
echo     # GPU setup
echo     gpu_available = setup_gpu_optimization^(^)
echo     if gpu_available:
echo         print^("✓ GPU optimization applied"^)
echo     else:
echo         print^("⚠ GPU not available, using CPU"^)
echo         use_gpu = False
echo         force_cpu_vad = True
echo.    
echo     # Show mode information
echo     print^(f"✓ Processing mode: {args.mode}"^)
echo     if args.mode == 'multithreaded':
echo         print^(f"  - Smart multithreaded splitting with GPU acceleration"^)
echo         print^(f"  - Parallel processing for maximum speed"^)
echo         print^(f"  - GPU VAD enabled"^)
echo         print^(f"  - {workers} parallel processes"^)
echo     else:
echo         print^(f"  - Word boundary splitting for stability"^)
echo         print^(f"  - Sequential processing for reliability"^)
echo         print^(f"  - CPU VAD for compatibility"^)
echo.    
echo     # Interactive mode or get parameters
echo     if args.interactive or not args.input or not args.output:
echo         print^("\n" + "="*60^)
echo         print^("AUDIO PROCESSING PIPELINE ^(SIMPLIFIED^)"^)
echo         print^("="*60^)
echo.        
echo         # Get input file/folder
echo         if not args.input:
echo             print^("\nEnter path to audio file or folder with audio files:"^)
echo             print^("Examples:"^)
echo             print^("  - audio.mp3"^)
echo             print^("  - C:\\path\\to\\audio.mp3"^)
echo             print^("  - audio_folder"^)
echo             print^("  - C:\\path\\to\\audio_folder"^)
echo             args.input = input^("Input file/folder: "^).strip^(^).strip^('"'^)
echo.        
echo         # Get output folder
echo         if not args.output:
echo             print^("\nEnter folder for saving results:"^)
echo             print^("Examples:"^)
echo             print^("  - results"^)
echo             print^("  - C:\\path\\to\\results"^)
echo             args.output = input^("Output folder: "^).strip^(^).strip^('"'^)
echo.        
echo         # Show current settings
echo         print^(f"\nCurrent settings ^({args.mode} mode^):"^)
echo         print^(f"  - Chunk duration: {chunk_duration} sec ^(10 minutes^)"^)
echo         print^(f"  - Minimum speaker segment: {min_speaker_segment} sec ^(no limit^)"^)
echo         print^(f"  - Splitting method: {split_method}"^)
echo         print^(f"  - Processing stages: {', '.join^(steps^)}"^)
echo         print^(f"  - GPU acceleration: {'Yes' if use_gpu else 'No'}"^)
echo         print^(f"  - VAD device: {'CPU' if force_cpu_vad else 'GPU'}"^)
echo         print^(f"  - Parallel processing: {'Yes' if parallel else 'No'}"^)
echo         print^(f"  - Number of processes: {workers}"^)
echo.        
echo         # Ask to change mode
echo         print^(f"\nCurrent mode: {args.mode}"^)
echo         print^("  single - Sequential processing ^(stable, slower^)"^)
echo         print^("  multithreaded - Parallel processing ^(fast, recommended^)"^)
echo         change_mode = input^(f"Change mode? ^(y/n, default n^): "^).strip^(^).lower^(^)
echo         if change_mode in ['y', 'yes', 'da']:
echo             new_mode = input^("Enter mode ^(single/multithreaded^): "^).strip^(^).lower^(^)
echo             if new_mode in ['single', 'multithreaded']:
echo                 args.mode = new_mode
echo                 # Update parameters based on new mode
echo                 if args.mode == 'multithreaded':
echo                     split_method = 'smart_multithreaded'
echo                     use_gpu = True
echo                     force_cpu_vad = False
echo                     parallel = True
echo                     workers = get_optimal_workers^(^)
echo                 else:
echo                     split_method = 'word_boundary'
echo                     use_gpu = True
echo                     force_cpu_vad = True
echo                     parallel = False
echo                     workers = 1
echo.                
echo                 print^(f"\nUpdated settings ^({args.mode} mode^):"^)
echo                 print^(f"  - Splitting method: {split_method}"^)
echo                 print^(f"  - GPU acceleration: {'Yes' if use_gpu else 'No'}"^)
echo                 print^(f"  - VAD device: {'CPU' if force_cpu_vad else 'GPU'}"^)
echo                 print^(f"  - Parallel processing: {'Yes' if parallel else 'No'}"^)
echo                 print^(f"  - Number of processes: {workers}"^)
echo.        
echo         print^(f"\nStarting processing with parameters:"^)
echo         print^(f"  Input: {args.input}"^)
echo         print^(f"  Output: {args.output}"^)
echo         print^(f"  Mode: {args.mode}"^)
echo         print^(f"  Splitting: {split_method}"^)
echo         print^(f"  GPU: {'Yes' if use_gpu else 'No'}"^)
echo         print^(f"  Parallel: {'Yes' if parallel else 'No'}"^)
echo.        
echo         confirm = input^("\nContinue? ^(y/n, default y^): "^).strip^(^).lower^(^)
echo         if confirm in ['n', 'no', 'net']:
echo             print^("Processing cancelled."^)
echo             return
echo.
echo     logger.info^(f"Input parameters: {vars^(args^)}"^)
echo     logger.info^(f"Mode: {args.mode}, Split method: {split_method}, GPU: {use_gpu}, Parallel: {parallel}"^)
echo.
echo     input_path = Path^(args.input^)
echo     output_dir = Path^(args.output^)
echo.
echo     # Check input file/folder existence
echo     if not input_path.exists^(^):
echo         logger.error^(f"Input file/folder not found: {input_path}"^)
echo         print^(f"\nERROR: File or folder '{input_path}' does not exist!"^)
echo         print^("Check the path and try again."^)
echo         return
echo.
echo     # Check diarization token if diarization is requested
echo     if 'diar' in steps:
echo         if not token_exists^(^):
echo             print^(f"\n{'='*60}"^)
echo             print^("DIARIZATION TOKEN NOT FOUND"^)
echo             print^(f"{'='*60}"^)
echo             print^("Diarization requires a HuggingFace token."^)
echo             print^(^)
echo             print^("Options:"^)
echo             print^("1. Setup diarization now ^(recommended^)"^)
echo             print^("2. Continue without diarization"^)
echo             print^("3. Cancel processing"^)
echo             print^(^)
echo             choice = input^("Enter choice ^(1-3^): "^).strip^(^)
echo.            
echo             if choice == "1":
echo                 print^("\nSetting up diarization..."^)
echo                 import subprocess
echo                 try:
echo                     subprocess.run^(["system\\fixes\\quick_diarization_fix.bat"], check=True^)
echo                     print^("Diarization setup completed!"^)
echo                 except subprocess.CalledProcessError:
echo                     print^("Diarization setup failed. Continuing without diarization."^)
echo                     steps = [s for s in steps if s != 'diar']
echo                     print^(f"Updated steps: {', '.join^(steps^)}"^)
echo             elif choice == "2":
echo                 print^("Continuing without diarization..."^)
echo                 steps = [s for s in steps if s != 'diar']
echo                 print^(f"Updated steps: {', '.join^(steps^)}"^)
echo             else:
echo                 print^("Processing cancelled."^)
echo                 return
echo         else:
echo             token = get_token^(^)
echo             if not token:
echo                 print^(f"\n{'='*60}"^)
echo                 print^("DIARIZATION TOKEN IS EMPTY"^)
echo                 print^(f"{'='*60}"^)
echo                 print^("The token file exists but is empty."^)
echo                 print^(^)
echo                 print^("Options:"^)
echo                 print^("1. Setup diarization now ^(recommended^)"^)
echo                 print^("2. Continue without diarization"^)
echo                 print^("3. Cancel processing"^)
echo                 print^(^)
echo                 choice = input^("Enter choice ^(1-3^): "^).strip^(^)
echo.                
echo                 if choice == "1":
echo                     print^("\nSetting up diarization..."^)
echo                     import subprocess
echo                     try:
echo                         subprocess.run^(["system\\fixes\\quick_diarization_fix.bat"], check=True^)
echo                         print^("Diarization setup completed!"^)
echo                     except subprocess.CalledProcessError:
echo                         print^("Diarization setup failed. Continuing without diarization."^)
echo                         steps = [s for s in steps if s != 'diar']
echo                         print^(f"Updated steps: {', '.join^(steps^)}"^)
echo                 elif choice == "2":
echo                     print^("Continuing without diarization..."^)
echo                     steps = [s for s in steps if s != 'diar']
echo                     print^(f"Updated steps: {', '.join^(steps^)}"^)
echo                 else:
echo                     print^("Processing cancelled."^)
echo                     return
echo.
echo     files = []
echo     if input_path.is_file^(^):
echo         files = [input_path]
echo         logger.info^(f"Processing single file: {input_path}"^)
echo         print^(f"\nFound file: {input_path}"^)
echo     elif input_path.is_dir^(^):
echo         files = list^(input_path.glob^('*.mp3'^)^) + list^(input_path.glob^('*.wav'^)^)
echo         logger.info^(f"Found {len^(files^)} files in folder: {input_path}"^)
echo         print^(f"\nFound {len^(files^)} audio files in folder: {input_path}"^)
echo         if not files:
echo             print^("No audio files ^(.mp3 or .wav^) found in folder"^)
echo             return
echo         for i, file in enumerate^(files, 1^):
echo             print^(f"  {i}. {file.name}"^)
echo     else:
echo         logger.error^(f"File or folder not found: {input_path}"^)
echo         return
echo.
echo     # Create output folder
echo     output_dir.mkdir^(parents=True, exist_ok=True^)
echo     print^(f"\nResults will be saved in: {output_dir}"^)
echo.
echo     # Start timing
echo     start_time = time.time^(^)
echo.    
echo     if parallel and len^(files^) ^> 1:
echo         # Многопоточная обработка
echo         print^(f"\nStarting multithreaded processing for {len^(files^)} files..."^)
echo         logger.info^("Using multithreaded processing with speaker organization"^)
echo.        
echo         organized_speakers = process_multiple_files_parallel_optimized^(
echo             files, output_dir, steps, chunk_duration,
echo             min_speaker_segment, split_method, use_gpu, force_cpu_vad, logger
echo         ^)
echo.        
echo         # Показываем результаты
echo         print^(f"\nMultithreaded processing completed!"^)
echo         print^(f"Total speakers found: {len^(organized_speakers^)}"^)
echo.        
echo         for speaker_name, speaker_data in organized_speakers.items^(^):
echo             print^(f"  Speaker {speaker_name}: {len^(speaker_data['files']^)} audio files"^)
echo             print^(f"    Folder: {speaker_data['folder']}"^)
echo.        
echo     else:
echo         # Однопоточная обработка
echo         print^(f"\nStarting single-threaded processing..."^)
echo         logger.info^("Using single-threaded processing with speaker organization"^)
echo.        
echo         # Инициализируем менеджеры
echo         gpu_manager = GPUMemoryManager^(GPU_MEMORY_LIMIT^)
echo         model_manager = ModelManager^(gpu_manager^)
echo.        
echo         try:
echo             # Обрабатываем файлы
echo             print^(f"\nStarting processing of {len^(files^)} files..."^)
echo             all_organized_speakers = {}
echo.            
echo             with tqdm^(total=len^(files^), desc="Processing files", unit="file"^) as pbar_files:
echo                 for audio in files:
echo                     logger.info^(f"\n=== Processing file: {audio} ==="^)
echo                     print^(f"\n{'='*50}"^)
echo                     print^(f"Processing: {audio.name}"^)
echo                     print^(f"{'='*50}"^)
echo.                    
echo                     # Используем новую функцию для одного файла
echo                     from audio.processors import process_file_multithreaded_optimized
echo                     organized_speakers = process_file_multithreaded_optimized^(
echo                         audio, output_dir, steps, chunk_duration,
echo                         min_speaker_segment, split_method, use_gpu, force_cpu_vad,
echo                         logger, model_manager, gpu_manager
echo                     ^)
echo.                    
echo                     # Объединяем результаты
echo                     for speaker_name, speaker_data in organized_speakers.items^(^):
echo                         if speaker_name not in all_organized_speakers:
echo                             all_organized_speakers[speaker_name] = speaker_data
echo                         else:
echo                             # Добавляем файлы к существующему спикеру
echo                             all_organized_speakers[speaker_name]['files'].extend^(speaker_data['files']^)
echo                             all_organized_speakers[speaker_name]['metadata'].extend^(speaker_data['metadata']^)
echo.                    
echo                     pbar_files.update^(1^)
echo.            
echo             # Показываем результаты
echo             print^(f"\nSingle-threaded processing completed!"^)
echo             print^(f"Total speakers found: {len^(all_organized_speakers^)}"^)
echo.            
echo             for speaker_name, speaker_data in all_organized_speakers.items^(^):
echo                 print^(f"  Speaker {speaker_name}: {len^(speaker_data['files']^)} audio files"^)
echo                 print^(f"    Folder: {speaker_data['folder']}"^)
echo.            
echo         finally:
echo             # Очистка менеджеров
echo             model_manager.cleanup_models^(^)
echo             gpu_manager.cleanup^(force=True^)
echo.    
echo     # Calculate execution time
echo     end_time = time.time^(^)
echo     total_time = end_time - start_time
echo.    
echo     logger.info^("=== Processing completed ==="^)
echo     print^(f"\n{'='*60}"^)
echo     print^("PROCESSING COMPLETED!"^)
echo     print^(f"{'='*60}"^)
echo     print^(f"Total execution time: {total_time/60:.1f} minutes"^)
echo     print^(f"Results saved in: {output_dir}"^)
echo     print^("\nResults structure:"^)
echo.    
echo     # Show what was created
echo     if output_dir.exists^(^):
echo         # Show speaker folders if diarization was performed
echo         if 'diar' in steps:
echo             speaker_folders = [d for d in output_dir.iterdir^(^) if d.is_dir^(^) and d.name.startswith^('speaker_'^)]
echo             if speaker_folders:
echo                 print^(f"  speaker_* folders ^({len^(speaker_folders^)} folders^)"^)
echo                 for speaker_folder in speaker_folders:
echo                     audio_files = list^(speaker_folder.glob^('*.wav'^)^)
echo                     metadata_files = list^(speaker_folder.glob^('metadata_*.txt'^)^)
echo                     info_files = list^(speaker_folder.glob^('*_info.txt'^)^)
echo.                    
echo                     print^(f"    - {speaker_folder.name}:"^)
echo                     print^(f"      Audio files: {len^(audio_files^)}"^)
echo                     print^(f"      Metadata files: {len^(metadata_files^)}"^)
echo                     print^(f"      Info files: {len^(info_files^)}"^)
echo.                    
echo                     # Показываем первые несколько аудиофайлов
echo                     for audio_file in audio_files[:3]:
echo                         try:
echo                             duration_str = get_mp3_duration^(str^(audio_file^)^)
echo                             print^(f"        {audio_file.name}: {duration_str}"^)
echo                         except:
echo                             print^(f"        {audio_file.name}"^)
echo.                    
echo                     if len^(audio_files^) ^> 3:
echo                         print^(f"        ... and {len^(audio_files^) - 3} more files"^)
echo.    
echo     print^(f"\nProcessing log saved in: audio_processing.log"^)
echo     print^(f"Temporary files automatically deleted"^)
echo.    
echo     # Show performance statistics
echo     if parallel and len^(files^) ^> 1:
echo         print^(f"\nPERFORMANCE STATISTICS:"^)
echo         print^(f"  - Files processed: {len^(files^)}"^)
echo         print^(f"  - Time per file: {total_time/len^(files^):.1f} seconds"^)
echo         print^(f"  - Speedup from parallelization: ~{workers}x"^)
echo         print^(f"  - GPU used: {'Yes' if gpu_available else 'No'}"^)
echo         print^(f"  - Mode: Multithreaded with smart splitting"^)
echo         print^(f"  - Threads per file: 4 ^(max^)"^)
echo         print^(f"  - Diarization: Locked ^(single thread^)"^)
echo     else:
echo         print^(f"\nPERFORMANCE STATISTICS:"^)
echo         print^(f"  - Files processed: {len^(files^)}"^)
echo         print^(f"  - Total time: {total_time/60:.1f} minutes"^)
echo         print^(f"  - GPU used: {'Yes' if gpu_available else 'No'}"^)
echo         print^(f"  - Mode: Single-threaded for stability"^)
echo         print^(f"  - VAD: CPU ^(for compatibility^)"^)
echo         print^(f"  - Diarization: Sequential"^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > ..\scripts\audio_processing_simple.py

echo Simplified audio processing script created successfully!
echo.
echo Usage:
echo   python audio_processing_simple.py --input audio.mp3 --output results
echo   python audio_processing_simple.py --input audio.mp3 --output results --mode single
echo   python audio_processing_simple.py --interactive
echo.
pause 