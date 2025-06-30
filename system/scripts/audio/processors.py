"""
Основные процессоры для обработки аудио файлов
"""

import tempfile
from pathlib import Path
from tqdm import tqdm
import multiprocessing
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
import shutil

from .managers import GPUMemoryManager, ModelManager
from .stages import clean_audio_with_demucs_optimized, diarize_with_pyannote_optimized
from .splitters import split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized, split_audio_smart_multithreaded_optimized
from .utils import copy_results_to_output_optimized
from .config import GPU_MEMORY_LIMIT

# Глобальная блокировка для диаризации
DIARIZATION_LOCK = threading.Lock()

def process_audio_file_optimized(audio_file, output_dir, steps, chunk_duration, 
                                min_segment_duration, split_method, use_gpu, logger, denoise_mode='enhanced'):
    """
    Оптимизированная обработка одного аудио файла с улучшенным управлением ресурсами
    """
    gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
    model_manager = ModelManager(gpu_manager)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            current = Path(audio_file)
            
            # Создаем временные папки для этого файла
            file_temp_dir = temp_path / current.stem
            file_temp_dir.mkdir(exist_ok=True)
            
            # Мониторим начальную память
            gpu_manager.monitor_memory(logger)
            
            # 1. Разбивка по времени
            if 'split' in steps:
                logger.info(f"Splitting file: {current.name}")
                try:
                    if split_method == 'smart_multithreaded':
                        whisper_model = model_manager.get_whisper_model("base")
                        parts = split_audio_smart_multithreaded_optimized(
                            str(current), file_temp_dir / 'parts', 
                            max_duration_sec=chunk_duration, 
                            whisper_model=whisper_model, 
                            max_workers=4,  # Оптимальное количество потоков
                            logger=logger
                        )
                    elif split_method == 'word_boundary':
                        whisper_model = model_manager.get_whisper_model("base")
                        parts = split_audio_at_word_boundary_optimized(
                            str(current), file_temp_dir / 'parts', 
                            max_duration_sec=chunk_duration, 
                            whisper_model=whisper_model, 
                            logger=logger
                        )
                    else:
                        parts = split_audio_by_duration_optimized(
                            str(current), file_temp_dir / 'parts', 
                            max_duration_sec=chunk_duration, 
                            logger=logger
                        )
                except Exception as e:
                    logger.error(f"Splitting error: {e}")
                    parts = split_audio_by_duration_optimized(
                        str(current), file_temp_dir / 'parts', 
                        max_duration_sec=chunk_duration, 
                        logger=logger
                    )
            else:
                parts = [str(current)]
            
            # Проверяем что части созданы
            if not parts:
                raise ValueError("Failed to create file parts")
            
            logger.info(f"Created {len(parts)} parts for processing")
            
            # Обрабатываем части с улучшенным управлением памятью
            processed_parts = process_parts_optimized(
                parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager, denoise_mode
            )
            
            # Копируем результаты в выходную папку
            final_results = copy_results_to_output_optimized(
                processed_parts, output_dir, current.stem, logger
            )
            
            # Финальная очистка
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
            
            return final_results
            
    except Exception as e:
        logger.error(f"Error processing file {audio_file.name}: {e}")
        return None

def process_parts_optimized(parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager, denoise_mode):
    """
    Оптимизированная обработка частей аудио с лучшим управлением ресурсами
    """
    processed_parts = []
    
    # Обрабатываем части последовательно с управлением памятью
    for idx, part in enumerate(parts):
        try:
            logger.info(f"Processing part {idx+1}/{len(parts)}")
            
            # Проверяем память перед обработкой
            if not gpu_manager.check_memory(required_gb=1.5):
                logger.warning("Low GPU memory, forcing cleanup")
                gpu_manager.cleanup(force=True)
            
            result = process_single_part_optimized(
                part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager, denoise_mode
            )
            processed_parts.append(result)
            
            # Мониторим память после каждой части
            gpu_manager.monitor_memory(logger)
            
        except Exception as e:
            logger.error(f"Error processing part {idx+1}: {e}")
            processed_parts.append([part])  # Возвращаем оригинальную часть
    
    return processed_parts

def process_single_part_optimized(part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager, denoise_mode):
    """
    Оптимизированная обработка одной части аудио
    """
    part_path = Path(part)
    logger.info(f"Processing part {idx+1}: {part_path.name}")
    
    try:
        current = part_path
        
        # Проверяем существование файла
        if not current.exists():
            logger.error(f"File part not found: {current}")
            return [str(current)]
        
        # 2. Удаление шумов
        if 'denoise' in steps:
            try:
                logger.info(f"Denoising part {idx+1}")
                cleaned = clean_audio_with_demucs_optimized(
                    str(current), file_temp_dir / 'cleaned', model_manager, gpu_manager, logger, mode=denoise_mode
                )
            except Exception as e:
                logger.error(f"Error denoising part {idx+1}: {e}")
                cleaned = str(current)
        else:
            cleaned = str(current)
        
        # 3. Диаризация (пропускаем VAD)
        if 'diar' in steps:
            try:
                logger.info(f"Diarization part {idx+1}")
                diarized = diarize_with_pyannote_optimized(
                    cleaned, file_temp_dir / 'diarized', model_manager=model_manager, 
                    gpu_manager=gpu_manager, logger=logger
                )
            except Exception as e:
                logger.error(f"Error diarization part {idx+1}: {e}")
                diarized = cleaned
        else:
            diarized = cleaned
        
        return [diarized]
        
    except Exception as e:
        logger.error(f"Error processing part {idx+1}: {e}")
        return [str(part_path)]

def process_chunk_with_metadata(chunk_path, chunk_info, steps, use_gpu, logger, 
                               model_manager, gpu_manager, temp_dir, denoise_mode='enhanced'):
    """
    Обработка одного чанка с метаданными и многопоточностью
    """
    chunk_path = Path(chunk_path)
    logger.info(f"Processing chunk: {chunk_path.name} with info: {chunk_info}")
    
    try:
        current = chunk_path
        
        # 1. Деноизинг (многопоточный)
        if 'denoise' in steps:
            logger.info(f"Denoising chunk {chunk_info.get('chunk_number', 'unknown')}")
            cleaned = clean_audio_with_demucs_optimized(
                str(current), temp_dir / 'cleaned', model_manager, gpu_manager, logger, mode=denoise_mode
            )
        else:
            cleaned = str(current)
        
        # 2. Диаризация (пропускаем VAD)
        if 'diar' in steps:
            logger.info(f"Diarization chunk {chunk_info.get('chunk_number', 'unknown')}")
            diarized = diarize_with_pyannote_optimized(
                cleaned, temp_dir / 'diarized', chunk_info=chunk_info,
                model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
            )
        else:
            diarized = cleaned
        
        return diarized
        
    except Exception as e:
        logger.error(f"Error processing chunk {chunk_info.get('chunk_number', 'unknown')}: {e}")
        return str(chunk_path)

def process_file_multithreaded_optimized(audio_file, output_dir, steps, chunk_duration,
                                        min_speaker_segment, split_method, use_gpu,
                                        logger, model_manager, gpu_manager):
    """
    Оптимизированная многопоточная обработка одного файла
    """
    audio_file = Path(audio_file)
    output_dir = Path(output_dir)
    
    # Создаем временную папку для этого файла
    temp_dir = output_dir / f"temp_{audio_file.stem}_{int(time.time())}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Разбиение на части
        if 'split' in steps:
            logger.info(f"Splitting file: {audio_file.name}")
            parts = split_audio_by_duration_optimized(
                str(audio_file), temp_dir, chunk_duration, split_method, logger
            )
        else:
            parts = [str(audio_file)]
        
        logger.info(f"File split into {len(parts)} parts")
        
        # 2. Обработка частей
        processed_parts = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for idx, part in enumerate(parts):
                chunk_info = {
                    'chunk_number': idx + 1,
                    'start_time': idx * chunk_duration,
                    'end_time': (idx + 1) * chunk_duration,
                    'duration': chunk_duration,
                    'file_name': f"part_{idx + 1}.wav"
                }
                
                future = executor.submit(
                    process_chunk_with_metadata,
                    part, chunk_info, steps, use_gpu, logger,
                    model_manager, gpu_manager, temp_dir
                )
                futures.append(future)
            
            # Собираем результаты
            for future in as_completed(futures):
                try:
                    result = future.result()
                    processed_parts.append(result)
                except Exception as e:
                    logger.error(f"Error in processing part: {e}")
        
        # 3. Организация результатов по спикерам
        organized_speakers = {}
        
        for part in processed_parts:
            if isinstance(part, str) and Path(part).exists():
                # Если это файл диаризации, организуем по спикерам
                if 'diarized' in part and Path(part).parent.name == 'diarized':
                    # Ищем папки спикеров в папке diarized
                    speaker_folders = [d for d in Path(part).parent.iterdir() if d.is_dir() and d.name.startswith('speaker_')]
                    
                    for speaker_folder in speaker_folders:
                        speaker_name = speaker_folder.name
                        if speaker_name not in organized_speakers:
                            organized_speakers[speaker_name] = {
                                'files': [],
                                'metadata': [],
                                'folder': speaker_folder
                            }
                        
                        # Добавляем файлы спикера
                        audio_files = list(speaker_folder.glob('*.wav'))
                        organized_speakers[speaker_name]['files'].extend(audio_files)
                        
                        # Добавляем метаданные
                        metadata_files = list(speaker_folder.glob('metadata_*.txt'))
                        organized_speakers[speaker_name]['metadata'].extend(metadata_files)
                else:
                    # Если это обычный файл, добавляем в общий список
                    if 'general' not in organized_speakers:
                        organized_speakers['general'] = {
                            'files': [],
                            'metadata': [],
                            'folder': Path(part).parent
                        }
                    organized_speakers['general']['files'].append(Path(part))
        
        # Также проверяем папку diarized напрямую, если она существует
        diarized_dir = temp_dir / 'diarized'
        if diarized_dir.exists():
            speaker_folders = [d for d in diarized_dir.iterdir() if d.is_dir() and d.name.startswith('speaker_')]
            
            for speaker_folder in speaker_folders:
                speaker_name = speaker_folder.name
                if speaker_name not in organized_speakers:
                    organized_speakers[speaker_name] = {
                        'files': [],
                        'metadata': [],
                        'folder': speaker_folder
                    }
                
                # Добавляем файлы спикера
                audio_files = list(speaker_folder.glob('*.wav'))
                organized_speakers[speaker_name]['files'].extend(audio_files)
                
                # Добавляем метаданные
                metadata_files = list(speaker_folder.glob('metadata_*.txt'))
                organized_speakers[speaker_name]['metadata'].extend(metadata_files)
        
        # 4. Копируем результаты в выходную папку
        logger.info("Copying results to output directory...")
        copied_speakers = {}
        
        for speaker_name, speaker_data in organized_speakers.items():
            # Создаем папку для спикера в выходной директории
            speaker_output_dir = output_dir / speaker_name
            speaker_output_dir.mkdir(parents=True, exist_ok=True)
            
            copied_speakers[speaker_name] = {
                'files': [],
                'metadata': [],
                'folder': speaker_output_dir
            }
            
            # Копируем аудио файлы
            for audio_file in speaker_data['files']:
                if audio_file.exists():
                    new_name = f"{audio_file.stem}_{int(time.time())}.wav"
                    new_path = speaker_output_dir / new_name
                    shutil.copy2(audio_file, new_path)
                    copied_speakers[speaker_name]['files'].append(new_path)
                    logger.info(f"Copied: {audio_file.name} -> {new_name}")
            
            # Копируем метаданные
            for metadata_file in speaker_data['metadata']:
                if metadata_file.exists():
                    new_name = f"metadata_{speaker_name}_{int(time.time())}.txt"
                    new_path = speaker_output_dir / new_name
                    shutil.copy2(metadata_file, new_path)
                    copied_speakers[speaker_name]['metadata'].append(new_path)
                    logger.info(f"Copied metadata: {metadata_file.name} -> {new_name}")
        
        logger.info(f"Copied results for {len(copied_speakers)} speakers to {output_dir}")
        return copied_speakers
        
    finally:
        # Очищаем временные файлы
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def process_multiple_files_parallel_optimized(files, output_dir, steps, chunk_duration,
                                            min_speaker_segment, split_method, use_gpu, logger):
    """
    Параллельная обработка нескольких файлов с организацией по спикерам
    """
    all_organized_speakers = {}
    
    # Инициализируем менеджеры один раз и передаем во все потоки
    gpu_manager = GPUMemoryManager()
    model_manager = ModelManager(gpu_manager)
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        for audio_file in files:
            future = executor.submit(
                process_file_multithreaded_optimized,
                audio_file, output_dir, steps, chunk_duration,
                min_speaker_segment, split_method, use_gpu, logger, model_manager, gpu_manager
            )
            futures.append(future)
        
        # Собираем результаты
        for future in as_completed(futures):
            try:
                file_speakers = future.result()
                
                # Объединяем результаты по спикерам
                for speaker_name, speaker_data in file_speakers.items():
                    if speaker_name not in all_organized_speakers:
                        all_organized_speakers[speaker_name] = speaker_data
                    else:
                        # Добавляем файлы к существующему спикеру
                        all_organized_speakers[speaker_name]['files'].extend(speaker_data['files'])
                        all_organized_speakers[speaker_name]['metadata'].extend(speaker_data['metadata'])
                        
            except Exception as e:
                logger.error(f"Error processing file: {e}")
    
    # Очистка менеджеров после завершения всех задач
    model_manager.cleanup_models()
    gpu_manager.cleanup(force=True)
    
    return all_organized_speakers