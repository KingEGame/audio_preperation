"""
Основные процессоры для обработки аудио файлов
"""

import tempfile
from pathlib import Path
from tqdm import tqdm

from .managers import GPUMemoryManager, ModelManager
from .stages import clean_audio_with_demucs_optimized, remove_silence_with_silero_optimized, diarize_with_pyannote_optimized
from .splitters import split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized
from .utils import copy_results_to_output_optimized
from .config import GPU_MEMORY_LIMIT

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
                    if split_method == 'word_boundary':
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
                part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager
            )
            processed_parts.append(result)
            
            # Мониторим память после каждой части
            gpu_manager.monitor_memory(logger)
            
        except Exception as e:
            logger.error(f"Error processing part {idx+1}: {e}")
            processed_parts.append([part])  # Возвращаем оригинальную часть
    
    return processed_parts

def process_single_part_optimized(part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager):
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
                    cleaned, use_gpu=use_gpu, model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
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
                    min_segment_duration=1.5, model_manager=model_manager, gpu_manager=gpu_manager, logger=logger
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