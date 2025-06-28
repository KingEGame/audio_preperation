"""
Утилиты и вспомогательные функции для обработки аудио
"""

import os
import subprocess
import logging
import time
import shutil
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

def get_mp3_duration(file_path):
    """
    Получает длительность MP3 файла используя ffprobe.
    :param file_path: Путь к MP3 файлу.
    :return: Строка с длительностью в формате HH:MM:SS.
    """
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ], capture_output=True, text=True, check=True)
        
        duration_seconds = float(result.stdout.strip())
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except subprocess.CalledProcessError:
        print(f"Error getting file duration: {file_path}")
        return "00:00:00"

def setup_logging(log_level=logging.INFO):
    """
    Настраивает логирование с временными метками и форматированием.
    :param log_level: Уровень логирования.
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('audio_processing.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def copy_results_to_output_optimized(processed_parts, output_dir, file_stem, logger):
    """
    Оптимизированное копирование результатов в выходную папку
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_files = []
    speaker_counter = 1
    
    for part_results in processed_parts:
        if part_results:
            for result_file in part_results:
                if Path(result_file).exists():
                    if 'speaker_' in Path(result_file).name:
                        new_name = f"{file_stem}_speaker_{speaker_counter:04d}.wav"
                        new_path = output_dir / new_name
                        shutil.copy2(result_file, new_path)
                        all_files.append(str(new_path))
                        speaker_counter += 1
                    else:
                        new_name = f"{file_stem}_{Path(result_file).stem}.wav"
                        new_path = output_dir / new_name
                        shutil.copy2(result_file, new_path)
                        all_files.append(str(new_path))
    
    logger.info(f"Copied {len(all_files)} files for {file_stem}")
    return all_files

def parallel_audio_processing_optimized(audio_files, output_dir, steps, chunk_duration, 
                                      min_segment_duration, split_method, use_gpu, logger):
    """
    Оптимизированная параллельная обработка с лучшим управлением ресурсами
    """
    from .config import get_optimal_workers
    from .processors import process_audio_file_optimized
    
    optimal_workers = get_optimal_workers()
    logger.info(f"Using {optimal_workers} parallel processes")
    
    all_results = []
    
    # Обрабатываем файлы с улучшенной параллелизацией
    with ProcessPoolExecutor(max_workers=optimal_workers) as executor:
        futures = []
        
        for audio_file in audio_files:
            future = executor.submit(
                process_audio_file_optimized,
                audio_file, output_dir, steps, chunk_duration,
                min_segment_duration, split_method, use_gpu, logger
            )
            futures.append(future)
        
        # Собираем результаты с прогресс-баром
        with tqdm(total=len(futures), desc="Processing files", unit="file") as pbar:
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=7200)  # 2 часа таймаут
                    all_results.append(result)
                except Exception as e:
                    logger.error(f"Error in parallel processing: {e}")
                    all_results.append(None)
                finally:
                    pbar.update(1)
    
    return all_results