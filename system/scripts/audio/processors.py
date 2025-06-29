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

from .managers import GPUMemoryManager, ModelManager
from .stages import clean_audio_with_demucs_optimized, remove_silence_with_silero_optimized, diarize_with_pyannote_optimized
from .splitters import split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized, split_audio_smart_multithreaded_optimized
from .utils import copy_results_to_output_optimized
from .config import GPU_MEMORY_LIMIT

# Глобальная блокировка для диаризации
DIARIZATION_LOCK = threading.Lock()

def process_audio_file_optimized(audio_file, output_dir, steps, chunk_duration, 
                                min_segment_duration, split_method, use_gpu, logger):
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
                parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager
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

def process_parts_optimized(parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager):
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
                part, idx, file_temp_dir, steps, use_gpu, False, logger, model_manager, gpu_manager
            )
            processed_parts.append(result)
            
            # Мониторим память после каждой части
            gpu_manager.monitor_memory(logger)
            
        except Exception as e:
            logger.error(f"Error processing part {idx+1}: {e}")
            processed_parts.append([part])  # Возвращаем оригинальную часть
    
    return processed_parts

def process_single_part_optimized(part, idx, file_temp_dir, steps, use_gpu, force_cpu_vad, logger, model_manager, gpu_manager):
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
                    str(current), file_temp_dir / 'cleaned', model_manager, gpu_manager, logger
                )
            except Exception as e:
                logger.error(f"Error denoising part {idx+1}: {e}")
                cleaned = str(current)
        else:
            cleaned = str(current)
        
        # 3. Удаление тишины
        if 'vad' in steps:
            try:
                logger.info(f"Silence removal part {idx+1}")
                no_silence = remove_silence_with_silero_optimized(
                    cleaned, use_gpu=use_gpu, force_cpu_vad=force_cpu_vad,
                    model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
                )
            except Exception as e:
                logger.error(f"Error silence removal part {idx+1}: {e}")
                no_silence = cleaned
        else:
            no_silence = cleaned
        
        # 4. Диаризация
        if 'diar' in steps:
            try:
                logger.info(f"Diarization part {idx+1}")
                diarized_files = diarize_with_pyannote_optimized(
                    no_silence, file_temp_dir / 'diarized', 
                    min_segment_duration=0.1, model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
                )
                return diarized_files if isinstance(diarized_files, list) else [diarized_files]
            except Exception as e:
                logger.error(f"Error diarization part {idx+1}: {e}")
                return [no_silence]
        else:
            return [no_silence]
            
    except Exception as e:
        logger.error(f"Critical error processing part {idx+1}: {e}")
        return [str(part_path)]

def process_chunk_with_metadata(chunk_path, chunk_info, steps, use_gpu, force_cpu_vad, logger, 
                               model_manager, gpu_manager, temp_dir):
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
                str(current), temp_dir / 'cleaned', model_manager, gpu_manager, logger
            )
        else:
            cleaned = str(current)
        
        # 2. Удаление тишины (многопоточный)
        if 'vad' in steps:
            logger.info(f"Silence removal chunk {chunk_info.get('chunk_number', 'unknown')}")
            no_silence = remove_silence_with_silero_optimized(
                cleaned, use_gpu=use_gpu, force_cpu_vad=force_cpu_vad,
                model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
            )
        else:
            no_silence = cleaned
        
        # 3. Диаризация (с блокировкой)
        if 'diar' in steps:
            logger.info(f"Diarization chunk {chunk_info.get('chunk_number', 'unknown')}")
            
            try:
                # Блокируем доступ к диаризации
                with DIARIZATION_LOCK:
                    logger.info(f"Acquired diarization lock for chunk {chunk_info.get('chunk_number', 'unknown')}")
                    diarized_files = diarize_with_pyannote_optimized(
                        no_silence, temp_dir / 'diarized', 
                        min_segment_duration=0.1, chunk_info=chunk_info,
                        model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
                    )
                    logger.info(f"Released diarization lock for chunk {chunk_info.get('chunk_number', 'unknown')}")
                
                # Проверяем результат диаризации
                if isinstance(diarized_files, list) and len(diarized_files) > 0:
                    return diarized_files
                else:
                    logger.warning(f"Diarization returned no files for chunk {chunk_info.get('chunk_number', 'unknown')}, using processed file")
                    return [no_silence]
                    
            except Exception as e:
                logger.error(f"Error during diarization for chunk {chunk_info.get('chunk_number', 'unknown')}: {e}")
                logger.warning(f"Using processed file without speaker separation for chunk {chunk_info.get('chunk_number', 'unknown')}")
                return [no_silence]
        else:
            return [no_silence]
            
    except Exception as e:
        logger.error(f"Critical error processing chunk {chunk_info.get('chunk_number', 'unknown')}: {e}")
        return [str(chunk_path)]

def process_file_multithreaded_optimized(audio_file, output_dir, steps, chunk_duration,
                                       min_speaker_segment, split_method, use_gpu, force_cpu_vad,
                                       logger, model_manager, gpu_manager):
    """
    Многопоточная обработка одного файла с организацией по спикерам
    """
    audio_file = Path(audio_file)
    logger.info(f"Starting multithreaded processing of file: {audio_file}")
    
    # Создаем временную папку для этого файла
    temp_dir = Path(f"temp_{audio_file.stem}_{int(time.time())}")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        current = audio_file
        
        # 1. Разделение на чанки (многопоточное)
        if 'split' in steps:
            logger.info("Stage 1: Audio splitting (multithreaded)")
            if split_method == 'smart_multithreaded':
                parts = split_audio_smart_multithreaded_optimized(
                    str(current), temp_dir / 'chunks', 
                    max_duration_sec=chunk_duration, 
                    whisper_model=model_manager.get_whisper_model("base") if model_manager else None,
                    max_workers=4,  # Оптимальное количество потоков
                    logger=logger
                )
            elif split_method == 'word_boundary':
                parts = split_audio_at_word_boundary_optimized(
                    str(current), temp_dir / 'chunks', 
                    max_duration_sec=chunk_duration, 
                    whisper_model=model_manager.get_whisper_model("base") if model_manager else None,
                    logger=logger
                )
            else:
                parts = split_audio_by_duration_optimized(
                    str(current), temp_dir / 'chunks', 
                    max_duration_sec=chunk_duration, logger=logger
                )
            logger.info(f"Created {len(parts)} chunks")
        else:
            parts = [str(current)]
        
        # Создаем информацию о чанках
        chunk_infos = []
        for i, part in enumerate(parts):
            chunk_path = Path(part)
            # Получаем длительность чанка
            try:
                from .utils import get_mp3_duration
                duration_str = get_mp3_duration(str(chunk_path))
                time_parts = duration_str.split(":")
                duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
            except:
                duration = 0
            
            chunk_info = {
                'chunk_number': i + 1,
                'start_time': i * chunk_duration,
                'end_time': (i + 1) * chunk_duration,
                'duration': duration,
                'file_name': chunk_path.name
            }
            chunk_infos.append(chunk_info)
        
        # 2. Многопоточная обработка чанков
        logger.info(f"Stage 2-4: Processing {len(parts)} chunks with multithreading")
        
        # Используем ThreadPoolExecutor для I/O операций
        max_workers = min(4, len(parts))  # Максимум 4 потока
        speaker_folders = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Создаем задачи для обработки чанков
            future_to_chunk = {}
            for i, (part, chunk_info) in enumerate(zip(parts, chunk_infos)):
                future = executor.submit(
                    process_chunk_with_metadata,
                    part, chunk_info, steps, use_gpu, force_cpu_vad, logger,
                    model_manager, gpu_manager, temp_dir
                )
                future_to_chunk[future] = chunk_info
            
            # Обрабатываем результаты
            for future in as_completed(future_to_chunk):
                chunk_info = future_to_chunk[future]
                try:
                    result_files = future.result()
                    logger.info(f"Completed processing chunk {chunk_info['chunk_number']}")
                    
                    # Собираем папки спикеров
                    for result_file in result_files:
                        result_path = Path(result_file)
                        if result_path.exists() and 'speaker_' in result_path.parent.name:
                            speaker_folders.append(str(result_path.parent))
                            
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_info['chunk_number']}: {e}")
        
        # 3. Организация файлов по спикерам
        if 'diar' in steps and speaker_folders:
            logger.info("Stage 5: Organizing speakers to output")
            try:
                from .stages import organize_speakers_to_output
                organized_speakers = organize_speakers_to_output(speaker_folders, output_dir, logger)
                logger.info(f"Organized {len(organized_speakers)} speakers")
                return organized_speakers
            except Exception as e:
                logger.error(f"Error organizing speakers: {e}")
                logger.warning("Returning empty speaker organization")
                return {}
        else:
            if 'diar' in steps:
                logger.warning("No speaker folders found after diarization")
                logger.info("This may be due to:")
                logger.info("1. No speech detected in audio")
                logger.info("2. Diarization token issues")
                logger.info("3. Model access problems")
            else:
                logger.info("Diarization stage not requested")
            return {}
            
    finally:
        # Очистка временных файлов
        try:
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Could not clean up temporary directory {temp_dir}: {e}")

def process_multiple_files_parallel_optimized(files, output_dir, steps, chunk_duration,
                                            min_speaker_segment, split_method, use_gpu, force_cpu_vad, logger):
    """
    Параллельная обработка нескольких файлов с многопоточностью
    """
    logger.info(f"Starting parallel processing of {len(files)} files")
    
    # Инициализируем менеджеры
    from .managers import GPUMemoryManager, ModelManager
    gpu_manager = GPUMemoryManager()
    model_manager = ModelManager(gpu_manager)
    
    try:
        # Используем ThreadPoolExecutor для совместимости с менеджерами
        max_workers = min(4, len(files))  # Максимум 4 потока
        all_organized_speakers = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Создаем задачи для обработки файлов
            future_to_file = {}
            for file_path in files:
                future = executor.submit(
                    process_file_multithreaded_optimized,
                    file_path, output_dir, steps, chunk_duration,
                    min_speaker_segment, split_method, use_gpu, force_cpu_vad, logger,
                    model_manager, gpu_manager
                )
                future_to_file[future] = file_path
            
            # Обрабатываем результаты
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    organized_speakers = future.result()
                    logger.info(f"Completed processing file: {Path(file_path).name}")
                    
                    # Объединяем результаты
                    for speaker_name, speaker_data in organized_speakers.items():
                        if speaker_name not in all_organized_speakers:
                            all_organized_speakers[speaker_name] = speaker_data
                        else:
                            # Добавляем файлы к существующему спикеру
                            all_organized_speakers[speaker_name]['files'].extend(speaker_data['files'])
                            all_organized_speakers[speaker_name]['metadata'].extend(speaker_data['metadata'])
                            
                except Exception as e:
                    logger.error(f"Error processing file {Path(file_path).name}: {e}")
        
        logger.info(f"Completed parallel processing. Total speakers: {len(all_organized_speakers)}")
        return all_organized_speakers
        
    finally:
        # Очистка менеджеров
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)