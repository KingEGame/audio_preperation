"""
Функции для разбивки аудио файлов на части
"""

import os
import sys
import math
import subprocess
import threading
import time
from pathlib import Path
import whisper
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import get_mp3_duration

# Add the scripts directory to path for imports
scripts_dir = Path(__file__).parent
sys.path.append(str(scripts_dir))

# Global locks for thread safety
WHISPER_MODEL_LOCK = threading.Lock()
SPLIT_COORDINATION_LOCK = threading.Lock()

# Global storage for boundary analysis results
BOUNDARY_RESULTS = {}

def get_central_temp_dir():
    """Получить центральную временную папку в корне проекта"""
    project_root = Path(__file__).parent.parent.parent.parent
    central_temp = project_root / "temp"
    central_temp.mkdir(exist_ok=True)
    return central_temp

def split_audio_by_duration_optimized(input_audio, temp_dir, max_duration_sec=600, 
                                    output_prefix="part_", logger=None):
    """
    Оптимизированная разбивка аудио по длительности
    """
    os.makedirs(temp_dir, exist_ok=True)
    
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    
    if total_seconds <= max_duration_sec:
        output_file = Path(temp_dir) / f"{output_prefix}1.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [str(output_file)]
    
    num_parts = math.ceil(total_seconds / max_duration_sec)
    parts = []
    
    for i in range(num_parts):
        start_time = i * max_duration_sec
        end_time = min((i + 1) * max_duration_sec, total_seconds)
        
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-ss", str(start_time), "-t", str(end_time - start_time),
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        parts.append(str(output_file))
    
    return parts

def analyze_boundary_segment(input_audio, segment_start, segment_end, segment_id, whisper_model, temp_dir, logger=None):
    """
    Анализирует сегмент для поиска границ предложений (выполняется в отдельном потоке)
    """
    try:
        # Создаем уникальную временную папку для каждого потока ВНУТРИ переданной temp_dir
        temp_dir = Path(temp_dir)
        segment_temp_dir = temp_dir / f"temp_analysis_{segment_id}"
        segment_temp_dir.mkdir(exist_ok=True)
        temp_file = segment_temp_dir / f"temp_analysis_{segment_id}.wav"
        
        # Извлекаем сегмент для анализа
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(segment_start), "-t", str(segment_end - segment_start),
            str(temp_file), "-y"
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if not temp_file.exists():
            logger.warning(f"Failed to create temp file for segment {segment_id}")
            return None
        
        # Транскрибируем с помощью Whisper с блокировкой
        boundaries = []
        try:
            with WHISPER_MODEL_LOCK:  # Блокируем доступ к модели
                result = whisper_model.transcribe(str(temp_file), language="ru")
                
                # Ищем лучшие границы предложений
                for segment in result["segments"]:
                    # Конвертируем время относительно исходного файла
                    absolute_start = segment_start + segment["start"]
                    absolute_end = segment_start + segment["end"]
                    boundaries.append({
                        'start': absolute_start,
                        'end': absolute_end,
                        'text': segment["text"].strip()
                    })
        except Exception as e:
            logger.error(f"Whisper transcription error for segment {segment_id}: {e}")
            # Возвращаем пустой список границ в случае ошибки
            boundaries = []
        
        # Удаляем временный файл
        try:
            temp_file.unlink()
        except:
            pass
        
        # Очищаем временную папку
        try:
            import shutil
            shutil.rmtree(segment_temp_dir)
        except:
            pass
        
        # Сохраняем результат в глобальный словарь
        with SPLIT_COORDINATION_LOCK:
            BOUNDARY_RESULTS[segment_id] = {
                'boundaries': boundaries,
                'segment_start': segment_start,
                'segment_end': segment_end
            }
        
        logger.info(f"✓ Analyzed segment {segment_id}: found {len(boundaries)} boundaries")
        return boundaries
        
    except Exception as e:
        logger.error(f"Error analyzing segment {segment_id}: {e}")
        # Сохраняем пустой результат в случае ошибки
        with SPLIT_COORDINATION_LOCK:
            BOUNDARY_RESULTS[segment_id] = {
                'boundaries': [],
                'segment_start': segment_start,
                'segment_end': segment_end
            }
        return None

def find_best_split_point(boundaries, target_time, search_window=30):
    """
    Находит лучшую точку разбивки в окне поиска
    """
    if not boundaries:
        return target_time
    
    # Ищем границы в окне поиска
    window_start = max(0, target_time - search_window)
    window_end = target_time + search_window
    
    best_boundary = target_time
    min_distance = float('inf')
    
    for boundary in boundaries:
        # Проверяем конец предложения (более естественная точка разбивки)
        boundary_end = boundary['end']
        
        if window_start <= boundary_end <= window_end:
            distance = abs(boundary_end - target_time)
            if distance < min_distance:
                min_distance = distance
                best_boundary = boundary_end
    
    return best_boundary

def split_audio_smart_multithreaded_optimized(input_audio, temp_dir, max_duration_sec=600, 
                                            output_prefix="part_", whisper_model=None, 
                                            analysis_window=30, max_workers=4, logger=None):
    """
    Умная многопоточная разбивка аудио с анализом границ предложений на GPU
    
    Алгоритм:
    1. Разбиваем на 10-минутные отрезки
    2. Анализируем последние 30 секунд каждого отрезка в многопотоке на GPU
    3. Находим границы предложений
    4. Координируем между потоками - следующий начинается там, где закончился предыдущий
    5. Копируем и обрезаем только нужные части
    """
    if logger is None:
        import logging
        logger = logging.getLogger(__name__)
    
    os.makedirs(temp_dir, exist_ok=True)
    
    # Получаем длительность файла
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    
    logger.info(f"Smart multithreaded splitting: {total_seconds}s total, {max_duration_sec}s chunks")
    
    if total_seconds <= max_duration_sec:
        output_file = Path(temp_dir) / f"{output_prefix}1.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [str(output_file)]
    
    # Загружаем Whisper модель если не передана
    if whisper_model is None:
        logger.info("Loading Whisper model for smart splitting...")
        with WHISPER_MODEL_LOCK:
            whisper_model = whisper.load_model("base")
            if torch.cuda.is_available():
                whisper_model = whisper_model.to("cuda")
                logger.info("✓ Whisper model moved to GPU")
    
    # Вычисляем количество частей
    num_parts = math.ceil(total_seconds / max_duration_sec)
    logger.info(f"Will create {num_parts} parts with smart boundaries")
    
    # Очищаем глобальные результаты
    global BOUNDARY_RESULTS
    BOUNDARY_RESULTS.clear()
    
    # Этап 1: Многопоточный анализ границ
    logger.info("Stage 1: Analyzing sentence boundaries in parallel...")
    
    # Уменьшаем количество потоков для стабильности
    safe_max_workers = min(max_workers, 2)  # Максимум 2 потока для стабильности
    
    with ThreadPoolExecutor(max_workers=safe_max_workers) as executor:
        futures = []
        
        for i in range(num_parts):
            # Вычисляем границы для анализа
            chunk_start = i * max_duration_sec
            chunk_end = min((i + 1) * max_duration_sec, total_seconds)
            
            # Анализируем последние 30 секунд каждого чанка
            analysis_start = max(0, chunk_end - analysis_window)
            analysis_end = chunk_end
            
            # Запускаем анализ в отдельном потоке
            future = executor.submit(
                analyze_boundary_segment,
                input_audio, analysis_start, analysis_end, i, whisper_model, temp_dir, logger
            )
            futures.append((future, i))
        
        # Ждем завершения всех анализов
        for future, segment_id in futures:
            try:
                future.result(timeout=300)  # 5 минут таймаут на сегмент
            except Exception as e:
                logger.error(f"Failed to analyze segment {segment_id}: {e}")
                # Устанавливаем пустой результат для неудачного сегмента
                with SPLIT_COORDINATION_LOCK:
                    BOUNDARY_RESULTS[segment_id] = {
                        'boundaries': [],
                        'segment_start': segment_id * max_duration_sec,
                        'segment_end': min((segment_id + 1) * max_duration_sec, total_seconds)
                    }
    
    # Этап 2: Координация и создание финальных частей
    logger.info("Stage 2: Coordinating boundaries and creating final parts...")
    
    parts = []
    current_start = 0
    
    for i in range(num_parts):
        # Получаем результаты анализа
        segment_data = BOUNDARY_RESULTS.get(i, {})
        boundaries = segment_data.get('boundaries', [])
        
        # Вычисляем целевую точку разбивки
        target_time = (i + 1) * max_duration_sec
        
        # Находим лучшую границу
        best_split_point = find_best_split_point(boundaries, target_time, analysis_window)
        
        # Ограничиваем границы файла
        best_split_point = max(current_start, min(best_split_point, total_seconds))
        
        logger.info(f"Part {i+1}: {current_start:.1f}s -> {best_split_point:.1f}s "
                   f"(target: {target_time:.1f}s, found: {len(boundaries)} boundaries)")
        
        # Создаем финальную часть
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        
        if not output_file.exists():
            part_duration = best_split_point - current_start
            
            if part_duration > 0:
                command = [
                    "ffmpeg", "-i", input_audio,
                    "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                    "-ss", str(current_start), "-t", str(part_duration),
                    str(output_file), "-y"
                ]
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if output_file.exists():
                    parts.append(str(output_file))
                    logger.info(f"✓ Created part {i+1}: {output_file.name} ({part_duration:.1f}s)")
                else:
                    logger.error(f"Failed to create part {i+1}")
            else:
                logger.warning(f"Part {i+1} has zero duration, skipping")
        
        # Обновляем начальную точку для следующей части
        current_start = best_split_point
    
    # Очищаем временные файлы
    temp_analysis_dir = Path(temp_dir) / "temp_analysis"
    if temp_analysis_dir.exists():
        import shutil
        shutil.rmtree(temp_analysis_dir)
    
    logger.info(f"Smart splitting completed: {len(parts)} parts created")
    return parts

def split_audio_at_word_boundary_optimized(input_audio, temp_dir, max_duration_sec=600, 
                                         output_prefix="part_", whisper_model=None, logger=None):
    """
    Оптимизированная разбивка аудио по границам слов
    """
    os.makedirs(temp_dir, exist_ok=True)
    
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    
    if total_seconds <= max_duration_sec:
        output_file = Path(temp_dir) / f"{output_prefix}1.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [str(output_file)]
    
    if whisper_model is None:
        whisper_model = whisper.load_model("base")
    
    num_parts = math.ceil(total_seconds / max_duration_sec)
    parts = []
    
    for i in range(num_parts):
        start_time = i * max_duration_sec
        end_time = min((i + 1) * max_duration_sec, total_seconds)
        
        # Анализируем окрестности точки разбивки
        analysis_start = max(0, start_time - 30)
        analysis_end = min(total_seconds, end_time + 30)
        
        # Создаем временный файл для анализа ВНУТРИ temp_dir
        temp_file = Path(temp_dir) / f"temp_analysis_{i}.wav"
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(analysis_start), "-t", str(analysis_end - analysis_start),
            str(temp_file), "-y"
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Транскрибируем для поиска границ слов
        result = whisper_model.transcribe(str(temp_file), language="ru")
        
        # Ищем лучшую границу слова
        target_time = start_time - analysis_start
        best_boundary = target_time
        min_distance = float('inf')
        
        for segment in result["segments"]:
            segment_end = segment["end"]
            distance = abs(segment_end - target_time)
            if distance < min_distance:
                min_distance = distance
                best_boundary = segment_end
        
        # Удаляем временный файл
        try:
            temp_file.unlink()
        except:
            pass
        
        # Вычисляем реальное время разбивки
        actual_split_time = analysis_start + best_boundary
        
        # Создаем финальную часть
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        if not output_file.exists():
            if i == num_parts - 1:
                # Последняя часть - до конца файла
                part_duration = total_seconds - actual_split_time
            else:
                part_duration = max_duration_sec
            
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-ss", str(actual_split_time), "-t", str(part_duration),
                str(output_file), "-y"
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        parts.append(str(output_file))
    
    return parts