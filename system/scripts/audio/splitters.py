"""
Функции для разбивки аудио файлов на части
"""

import os
import math
import subprocess
from pathlib import Path
import whisper
from .utils import get_mp3_duration

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
        
        # Создаем временный файл для анализа
        temp_file = Path(temp_dir) / f"temp_analysis_{i}.wav"
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(analysis_start), "-t", str(analysis_end - analysis_start),
            str(temp_file)
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
        temp_file.unlink()
        
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
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        parts.append(str(output_file))
    
    return parts