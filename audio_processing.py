#!/usr/bin/env python3
"""
Аудио-процессинг пайплайн с поддержкой GPU
Этапы: нарезка, шумоподавление, удаление тишины, диаризация
"""

import os
import sys
import subprocess
import argparse
import logging
import tempfile
import math
from pathlib import Path
from tqdm import tqdm

# Импорты для обработки аудио
try:
    import torch
    import torchaudio
    import whisper
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    from demucs.audio import AudioFile
    from huggingface_hub import HfApi
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что установлены все зависимости")
    sys.exit(1)

def get_mp3_duration(file_path):
    """
    Получает длительность MP3 файла с помощью ffprobe.
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
        print(f"Ошибка при получении длительности файла: {file_path}")
        return "00:00:00"

def convert_to_wav(input_audio, output_dir, output_prefix="part_", num_parts=1):
    """
    Конвертирует аудиофайл в WAV формат с помощью ffmpeg.
    :param input_audio: Путь к входному аудиофайлу.
    :param output_dir: Папка для сохранения WAV файлов.
    :param output_prefix: Префикс для выходных файлов.
    :param num_parts: Количество частей для разделения.
    :return: Список путей к созданным WAV файлам.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Получаем длительность файла
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # Если нужно только одна часть
    if num_parts == 1:
        output_file = os.path.join(output_dir, f"{output_prefix}1.wav")
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            output_file
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [output_file]
    
    # Разделяем на части
    part_duration = total_seconds / num_parts
    wav_files = []
    
    for i in range(num_parts):
        start_time = i * part_duration
        output_file = os.path.join(output_dir, f"{output_prefix}{i + 1}.wav")
        
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(start_time), "-t", str(part_duration),
            output_file
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wav_files.append(output_file)
    
    return wav_files

def clean_audio_with_demucs(input_audio, temp_dir, logger=None):
    """
    Удаляет фоновый шум и музыку с помощью Demucs.
    :param input_audio: Путь к входному аудиофайлу.
    :param temp_dir: Временная папка для сохранения результатов.
    :param logger: Логгер для записи сообщений.
    :return: Путь к очищенному аудиофайлу.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Определяем путь для файла vocals
    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    vocals_file = temp_dir / f"{Path(input_audio).stem}_vocals.wav"

    # Если файл уже существует, возвращаем его
    if vocals_file.exists():
        logger.info(f"Файл уже существует: {vocals_file}")
        return str(vocals_file)

    # Используем GPU если доступен, иначе CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Используем устройство: {device}")
    
    # Загрузка предобученной модели
    logger.info("Загрузка модели Demucs...")
    with tqdm(total=1, desc="Загрузка модели Demucs", unit="модель") as pbar:
        model = get_model("htdemucs")   # Используйте 'htdemucs', 'mdx_extra_q', и т.д.
        model.to(device)  # Перемещаем модель на GPU/CPU
        pbar.update(1)
    logger.info(f"Модель загружена и перемещена на устройство: {device}")

    # Чтение аудиофайла
    logger.info(f"Чтение аудиофайла: {input_audio}")
    with tqdm(total=1, desc="Загрузка аудио", unit="файл") as pbar:
        wav = AudioFile(input_audio).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
        wav = wav.unsqueeze(0).to(device)  # Перемещаем тензор на устройство
        pbar.update(1)
    logger.info(f"Аудиофайл успешно загружен. Размер тензора: {wav.shape}")

    # Очищаем кэш GPU если используем CUDA
    if device.type == "cuda":
        torch.cuda.empty_cache()
        logger.info("Кэш GPU очищен.")
        logger.info(f"Занято памяти на GPU: {torch.cuda.memory_allocated() / 1024 ** 3:.2f} ГБ")
        logger.info(f"Свободно памяти на GPU: {torch.cuda.memory_reserved() / 1024 ** 3:.2f} ГБ")

    # Применение модели
    logger.info("Применение модели для разделения аудио...")
    
    with tqdm(total=1, desc="Разделение аудио", unit="операция") as pbar:
        if device.type == "cuda":
            with torch.amp.autocast(device_type='cuda'):
                sources = apply_model(model, wav, device=device)
        else:
            sources = apply_model(model, wav, device=device)
        pbar.update(1)
    logger.info("Разделение аудио завершено.")

    for i, source in enumerate(model.sources):
        # Сохраняем аудио с использованием torchaudio
        torchaudio.save(str(vocals_file), sources[0, i].cpu(), model.samplerate)
        logger.info(f"Сохранено: {vocals_file}")

    if not vocals_file.exists():
        raise FileNotFoundError("Файл с вокалом (vocals) не был создан.")

    # Возвращаем только файл с вокалом
    return vocals_file

def split_audio_by_duration(input_audio, temp_dir, max_duration_sec=600, output_prefix="part_", logger=None):
    """
    Нарезает аудиофайл на куски по max_duration_sec секунд.
    :param input_audio: Путь к входному аудиофайлу.
    :param temp_dir: Временная папка для сохранения частей.
    :param max_duration_sec: Максимальная длительность куска в секундах.
    :param output_prefix: Префикс для выходных файлов.
    :param logger: Логгер для записи сообщений.
    :return: Список путей к созданным файлам.
    """
    import math
    os.makedirs(temp_dir, exist_ok=True)
    
    # Получаем длительность файла
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # Если файл короче max_duration_sec, возвращаем его как есть
    if total_seconds <= max_duration_sec:
        output_file = Path(temp_dir) / f"{output_prefix}1.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Файл короче {max_duration_sec} секунд, сохранён как: {output_file}")
        return [str(output_file)]
    
    num_parts = math.ceil(total_seconds / max_duration_sec)
    parts = []
    
    for i in range(num_parts):
        start_time = i * max_duration_sec
        end_time = min((i + 1) * max_duration_sec, total_seconds)
        
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        if output_file.exists():
            print(f"Часть {i + 1} уже существует: {output_file}, пропускаем.")
        else:
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-ss", str(start_time), "-t", str(end_time - start_time),
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Часть {i + 1} сохранена: {output_file}")
        
        parts.append(str(output_file))
    
    print("Нарезка завершена.")
    return parts

def remove_silence_with_silero(input_wav, output_wav=None, min_speech_duration_ms=250, min_silence_duration_ms=400, window_size_samples=1536, sample_rate=16000, use_gpu=False, logger=None):
    """
    Удаляет тишину из аудиофайла с помощью Silero VAD.
    :param input_wav: Путь к входному WAV файлу.
    :param output_wav: Путь для сохранения файла без тишины (если None, создается автоматически).
    :param min_speech_duration_ms: Минимальная длительность речевого сегмента в миллисекундах.
    :param min_silence_duration_ms: Минимальная длительность тишины в миллисекундах.
    :param window_size_samples: Размер окна для анализа в сэмплах.
    :param sample_rate: Частота дискретизации.
    :param use_gpu: Использовать ли GPU (по умолчанию False для стабильности).
    :param logger: Логгер для записи сообщений.
    :return: Путь к файлу без тишины.
    """
    import torch
    import torchaudio
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        import silero_vad
    except ImportError:
        logger.info("Устанавливаем silero-vad...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "silero-vad==5.1.2"])
            import silero_vad
            logger.info("✓ silero-vad установлен успешно")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка установки silero-vad: {e}")
            logger.info("Возвращаем исходный файл без удаления тишины")
            return input_wav
    
    if output_wav is None:
        output_wav = str(Path(input_wav).with_name(Path(input_wav).stem + "_nosilence.wav"))
    
    logger.info(f"Начинаем удаление тишины из файла: {input_wav}")
    
    # Используем GPU если доступен и запрошен, иначе CPU
    if use_gpu and torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Используем устройство для VAD: {device}")
    else:
        device = torch.device("cpu")
        logger.info(f"Используем устройство для VAD: {device} (GPU недоступен или отключен)")
    
    try:
        with tqdm(total=3, desc="Удаление тишины", unit="этап") as pbar:
            # Загрузка аудио
            wav, sr = torchaudio.load(input_wav)
            wav = wav.to(device)  # Перемещаем на GPU/CPU
            pbar.update(1)
            
            # Ресемплинг если нужно
            if sr != sample_rate:
                wav = torchaudio.functional.resample(wav, sr, sample_rate)
                sr = sample_rate
            pbar.update(1)
            
            # Загружаем модель и перемещаем на нужное устройство
            model = silero_vad.load_silero_vad()
            model = model.to(device)  # Перемещаем модель на то же устройство
            
            # Анализ речи
            speech_timestamps = silero_vad.get_speech_timestamps(
                wav[0],
                model=model,
                sampling_rate=sr,
                min_speech_duration_ms=min_speech_duration_ms,
                min_silence_duration_ms=min_silence_duration_ms,
                window_size_samples=window_size_samples
            )
            pbar.update(1)
        
        if not speech_timestamps:
            logger.warning("Речь не найдена, возвращаю исходный файл.")
            return input_wav
        
        # Создание аудио без тишины
        speech_audio = torch.cat([wav[:, ts['start']:ts['end']] for ts in speech_timestamps], dim=1)
        torchaudio.save(output_wav, speech_audio.cpu(), sr)  # Перемещаем обратно на CPU для сохранения
        logger.info(f"Файл без тишины сохранён: {output_wav}")
        return output_wav
        
    except RuntimeError as e:
        if "device" in str(e).lower() or "cuda" in str(e).lower():
            logger.warning(f"Ошибка устройства GPU: {e}")
            logger.info("Пробуем использовать CPU...")
            # Пробуем с CPU
            device = torch.device("cpu")
            wav = wav.cpu() if wav.device.type == "cuda" else wav
            model = silero_vad.load_silero_vad()
            model = model.cpu()
            
            speech_timestamps = silero_vad.get_speech_timestamps(
                wav[0],
                model=model,
                sampling_rate=sr,
                min_speech_duration_ms=min_speech_duration_ms,
                min_silence_duration_ms=min_silence_duration_ms,
                window_size_samples=window_size_samples
            )
            
            if not speech_timestamps:
                logger.warning("Речь не найдена, возвращаю исходный файл.")
                return input_wav
            
            speech_audio = torch.cat([wav[:, ts['start']:ts['end']] for ts in speech_timestamps], dim=1)
            torchaudio.save(output_wav, speech_audio, sr)
            logger.info(f"Файл без тишины сохранён (CPU): {output_wav}")
            return output_wav
        else:
            logger.error(f"Ошибка при удалении тишины: {e}")
            logger.info("Возвращаем исходный файл без удаления тишины")
            return input_wav
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении тишины: {e}")
        logger.info("Возвращаем исходный файл без удаления тишины")
        return input_wav

def split_audio_at_word_boundary(input_audio, temp_dir, max_duration_sec=600, output_prefix="part_", whisper_model=None, logger=None):
    """
    Нарезает аудиофайл на куски по max_duration_sec секунд, разделяя на границах слов.
    :param input_audio: Путь к входному аудиофайлу.
    :param temp_dir: Временная папка для сохранения частей.
    :param max_duration_sec: Максимальная длительность куска в секундах.
    :param output_prefix: Префикс для выходных файлов.
    :param whisper_model: Предзагруженная модель Whisper (если None, загружается автоматически).
    :param logger: Логгер для записи сообщений.
    :return: Список путей к созданным файлам.
    """
    import math
    os.makedirs(temp_dir, exist_ok=True)
    
    # Получаем длительность файла
    duration_str = get_mp3_duration(input_audio)
    time_parts = duration_str.split(":")
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # Если файл короче max_duration_sec, возвращаем его как есть
    if total_seconds <= max_duration_sec:
        output_file = Path(temp_dir) / f"{output_prefix}1.wav"
        if not output_file.exists():
            command = [
                "ffmpeg", "-i", input_audio,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(output_file)
            ]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Файл короче {max_duration_sec} секунд, сохранён как: {output_file}")
        return [str(output_file)]
    
    # Загружаем модель Whisper если не передана
    if whisper_model is None:
        whisper_model = whisper.load_model("base")  # Используем base для скорости
    
    num_parts = math.ceil(total_seconds / max_duration_sec)
    parts = []
    
    for i in range(num_parts):
        start_time = i * max_duration_sec
        end_time = min((i + 1) * max_duration_sec, total_seconds)
        
        # Определяем область для анализа границ слов (±30 секунд от точки разделения)
        analysis_start = max(0, start_time - 30)
        analysis_end = min(total_seconds, end_time + 30)
        
        # Создаём временный файл для анализа
        temp_file = Path(temp_dir) / f"temp_analysis_{i}.wav"
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(analysis_start), "-t", str(analysis_end - analysis_start),
            str(temp_file)
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Транскрибируем для определения границ слов
        print(f"Анализируем границы слов для части {i+1}...")
        result = whisper_model.transcribe(str(temp_file), language="ru")
        
        # Находим ближайшую границу слова к точке разделения
        target_time = start_time - analysis_start  # Время относительно начала анализа
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
        
        # Корректируем время разделения
        actual_split_time = analysis_start + best_boundary
        
        # Создаём финальный файл
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        if output_file.exists():
            print(f"Часть {i + 1} уже существует: {output_file}, пропускаем.")
        else:
            # Определяем длительность этой части
            if i == num_parts - 1:  # Последняя часть
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
            print(f"Часть {i + 1} сохранена на границе слова: {output_file}")
        
        parts.append(str(output_file))
    
    print("Нарезка на границах слов завершена.")
    return parts

def diarize_with_pyannote(input_audio, output_dir, min_segment_duration=1.5, logger=None):
    """
    Выполняет диаризацию говорящих с помощью PyAnnote.
    :param input_audio: Путь к входному аудиофайлу.
    :param output_dir: Папка для сохранения результатов.
    :param min_segment_duration: Минимальная длительность сегмента спикера в секундах.
    :param logger: Логгер для записи сообщений.
    :return: Список путей к файлам спикеров.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Используем GPU если доступен, иначе CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Используем устройство для диаризации: {device}")
    
    try:
        from pyannote.audio import Pipeline
        from pyannote.audio.pipelines.utils.hook import ProgressHook
    except ImportError:
        logger.error("PyAnnote не установлен. Запустите setup_diarization.py для установки.")
        logger.info("Возвращаем исходный файл без диаризации")
        return input_audio
    
    # Создаем выходную папку
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Путь для результата диаризации
    output_file = output_dir / f"{Path(input_audio).stem}_diarized.wav"
    
    logger.info(f"Начинаем диаризацию файла: {input_audio}")
    
    # Проверяем наличие токена
    token_file = "hf_token.txt"
    if not os.path.exists(token_file):
        logger.error("Файл с токеном HuggingFace не найден. Запустите setup_diarization.py")
        logger.info("Возвращаем исходный файл без диаризации")
        return input_audio
    
    try:
        with open(token_file, "r") as f:
            token = f.read().strip()
        if not token:
            logger.error("Токен HuggingFace пустой. Запустите setup_diarization.py")
            logger.info("Возвращаем исходный файл без диаризации")
            return input_audio
    except Exception as e:
        logger.error(f"Ошибка чтения токена: {e}")
        logger.info("Возвращаем исходный файл без диаризации")
        return input_audio

    # Проверяем токен через huggingface_hub
    try:
        api = HfApi(token=token)
        user_info = api.whoami()
        logger.info(f"Токен валиден для пользователя: {user_info.get('name')}")
    except Exception as e:
        logger.error(f"Ошибка токена HuggingFace: {e}")
        logger.info("Возвращаем исходный файл без диаризации")
        return input_audio

    try:
        # Загружаем модель диаризации с токеном
        logger.info("Загрузка модели диаризации...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        # Перемещаем модель на GPU если доступен
        if device.type == "cuda":
            pipeline = pipeline.to(device)
            logger.info("Модель перемещена на GPU")
        
        # Выполняем диаризацию
        logger.info("Выполнение диаризации...")
        with ProgressHook() as hook:
            diarization = pipeline(input_audio, hook=hook)
        
        # Анализируем результаты
        speakers = set()
        total_duration = 0
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        logger.info(f"Диаризация завершена успешно!")
        logger.info(f"  - Обнаружено спикеров: {len(speakers)}")
        logger.info(f"  - Спикеры: {', '.join(sorted(speakers))}")
        logger.info(f"  - Общая длительность речи: {total_duration:.2f} сек")
        
        # Сохраняем результат в формате RTTM
        rttm_file = output_file.with_suffix('.rttm')
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        # Создаем текстовый отчет
        report_file = output_file.with_suffix('.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ДИАРИЗАЦИИ\n")
            f.write("="*50 + "\n\n")
            f.write(f"Файл: {input_audio}\n")
            f.write(f"Обнаружено спикеров: {len(speakers)}\n")
            f.write(f"Спикеры: {', '.join(sorted(speakers))}\n")
            f.write(f"Общая длительность речи: {total_duration:.2f} сек\n\n")
            f.write("ДЕТАЛЬНЫЙ ОТЧЕТ:\n")
            f.write("-"*30 + "\n")
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                start_time = turn.start
                end_time = turn.end
                duration = end_time - start_time
                f.write(f"{speaker}: {start_time:.2f}s - {end_time:.2f}s (длительность: {duration:.2f}s)\n")
        
        logger.info(f"Результаты сохранены:")
        logger.info(f"  RTTM файл: {rttm_file}")
        logger.info(f"  Отчет: {report_file}")
        
        # Создаем отдельные файлы для каждого спикера
        logger.info("Создание отдельных файлов для каждого спикера...")
        speaker_files = create_speaker_segments(input_audio, diarization, output_dir, min_segment_duration=min_segment_duration, logger=logger)
        
        # Возвращаем список файлов спикеров вместо исходного файла
        if speaker_files:
            logger.info(f"Возвращаем {len(speaker_files)} файлов спикеров")
            return speaker_files
        else:
            logger.warning("Не удалось создать файлы спикеров, возвращаем исходный файл")
            return [input_audio]
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Ошибка при диаризации: {error_msg}")
        
        # Проверяем тип ошибки и даем рекомендации
        if "Could not download" in error_msg or "private or gated" in error_msg:
            logger.error("ПРОБЛЕМА: Модель не загружена из-за проблем с токеном или условиями использования")
            logger.info("РЕШЕНИЕ:")
            logger.info("1. Запустите: quick_diarization_setup.bat")
            logger.info("2. Или следуйте инструкциям в DIARIZATION_SETUP_GUIDE.md")
            logger.info("3. Убедитесь, что вы приняли условия использования на HuggingFace")
        elif "NoneType" in error_msg:
            logger.error("ПРОБЛЕМА: Модель не инициализирована")
            logger.info("РЕШЕНИЕ: Проверьте токен и перезапустите настройку диаризации")
        else:
            logger.error("ПРОБЛЕМА: Неожиданная ошибка при диаризации")
            logger.info("РЕШЕНИЕ: Проверьте интернет-соединение и попробуйте снова")
        
        logger.info("Возвращаем исходный файл без диаризации")
        return input_audio

def create_speaker_segments(input_audio, diarization_result, output_dir, min_segment_duration=1.5, logger=None):
    """
    Создает отдельные аудиофайлы для каждого спикера на основе результатов диаризации.
    
    :param input_audio: Путь к исходному аудиофайлу
    :param diarization_result: Результат диаризации (объект pyannote.core.Annotation)
    :param output_dir: Папка для сохранения сегментов спикеров
    :param min_segment_duration: Минимальная длительность сегмента в секундах
    :param logger: Логгер для записи сообщений
    :return: Список путей к созданным файлам спикеров
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    speaker_files = []
    speaker_segments = {}
    
    logger.info(f"Создание сегментов спикеров из файла: {input_audio}")
    
    # Группируем сегменты по спикерам
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end
        duration = end_time - start_time
        
        # Пропускаем слишком короткие сегменты
        if duration < min_segment_duration:
            logger.debug(f"Пропускаем короткий сегмент {speaker}: {start_time:.2f}s - {end_time:.2f}s ({duration:.2f}s)")
            continue
        
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        
        speaker_segments[speaker].append({
            'start': start_time,
            'end': end_time,
            'duration': duration
        })
    
    logger.info(f"Найдено {len(speaker_segments)} спикеров с сегментами")
    
    # Создаем файлы для каждого спикера
    for speaker, segments in speaker_segments.items():
        if not segments:
            continue
        
        # Сортируем сегменты по времени
        segments.sort(key=lambda x: x['start'])
        
        # Создаем имя файла для спикера
        speaker_file = output_dir / f"speaker_{speaker}.wav"
        
        # Создаем временный файл со списком сегментов для ffmpeg
        segments_list_file = output_dir / f"segments_{speaker}.txt"
        
        with open(segments_list_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                f.write(f"file '{input_audio}'\n")
                f.write(f"inpoint {segment['start']:.3f}\n")
                f.write(f"outpoint {segment['end']:.3f}\n")
        
        # Объединяем сегменты спикера в один файл
        command = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(segments_list_file),
            "-c", "copy", str(speaker_file),
            "-y"  # Перезаписать если существует
        ]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            if speaker_file.exists():
                # Получаем длительность созданного файла
                duration_str = get_mp3_duration(str(speaker_file))
                time_parts = duration_str.split(":")
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2])
                total_duration = hours * 3600 + minutes * 60 + seconds
                
                logger.info(f"Создан файл спикера {speaker}: {speaker_file.name} ({total_duration} сек, {len(segments)} сегментов)")
                speaker_files.append(str(speaker_file))
            else:
                logger.error(f"Файл спикера {speaker} не был создан")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при создании файла спикера {speaker}: {e}")
            logger.error(f"stderr: {e.stderr}")
        finally:
            # Удаляем временный файл со списком сегментов
            if segments_list_file.exists():
                segments_list_file.unlink()
    
    logger.info(f"Создано {len(speaker_files)} файлов спикеров в {output_dir}")
    return speaker_files

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

def main():
    parser = argparse.ArgumentParser(description="Аудио-процессинг пайплайн: нарезка, шумоподавление, удаление тишины, диаризация с разделением по спикерам.")
    parser.add_argument('--input', '-i', help='Путь к аудиофайлу (mp3/wav) или папке с файлами')
    parser.add_argument('--output', '-o', help='Папка для сохранения результатов')
    parser.add_argument('--chunk_duration', type=int, default=600, help='Максимальная длительность куска (секунд), по умолчанию 600 (10 минут)')
    parser.add_argument('--min_speaker_segment', type=float, default=1.5, help='Минимальная длительность сегмента спикера (секунд), по умолчанию 1.5')
    parser.add_argument('--steps', nargs='+', default=['split','denoise','vad', 'diar'],
                        help='Этапы обработки: split, denoise, vad, diar')
    parser.add_argument('--split_method', type=str, default='word_boundary', choices=['simple', 'word_boundary'],
                        help='Метод разделения: simple (простое) или word_boundary (на границах слов)')
    parser.add_argument('--use_gpu', action='store_true', help='Использовать GPU для VAD (по умолчанию CPU для стабильности)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробное логирование')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим с запросами параметров')
    args = parser.parse_args()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Запуск аудио-процессинг пайплайна ===")

    # Интерактивный режим или получение параметров
    if args.interactive or not args.input or not args.output:
        print("\n" + "="*60)
        print("АУДИО ПРОЦЕССИНГ ПАЙПЛАЙН")
        print("="*60)
        
        # Получаем входной файл/папку
        if not args.input:
            print("\nВведите путь к аудиофайлу или папке с аудиофайлами:")
            print("Примеры:")
            print("  - audio.mp3")
            print("  - C:\\path\\to\\audio.mp3")
            print("  - audio_folder")
            print("  - C:\\path\\to\\audio_folder")
            args.input = input("Входной файл/папка: ").strip().strip('"')
        
        # Получаем выходную папку
        if not args.output:
            print("\nВведите папку для сохранения результатов:")
            print("Примеры:")
            print("  - results")
            print("  - C:\\path\\to\\results")
            args.output = input("Выходная папка: ").strip().strip('"')
        
        # Дополнительные настройки
        print(f"\nТекущие настройки:")
        print(f"  - Длительность куска: {args.chunk_duration} сек")
        print(f"  - Минимальная длительность сегмента спикера: {args.min_speaker_segment} сек")
        print(f"  - Метод разделения: {args.split_method}")
        print(f"  - Этапы: {', '.join(args.steps)}")
        
        change_settings = input("\nИзменить настройки? (y/n, по умолчанию n): ").strip().lower()
        if change_settings in ['y', 'yes', 'да']:
            # Длительность куска
            new_duration = input(f"Длительность куска в секундах (по умолчанию {args.chunk_duration}): ").strip()
            if new_duration and new_duration.isdigit():
                args.chunk_duration = int(new_duration)
            
            # Минимальная длительность сегмента спикера
            new_min_segment = input(f"Минимальная длительность сегмента спикера в секундах (по умолчанию {args.min_speaker_segment}): ").strip()
            if new_min_segment and new_min_segment.replace('.', '').isdigit():
                args.min_speaker_segment = float(new_min_segment)
            
            # Метод разделения
            print("\nМетод разделения:")
            print("  simple - простое разделение по времени")
            print("  word_boundary - разделение на границах слов (рекомендуется)")
            new_method = input(f"Метод (по умолчанию {args.split_method}): ").strip()
            if new_method in ['simple', 'word_boundary']:
                args.split_method = new_method
            
            # Этапы обработки
            print("\nЭтапы обработки:")
            print("  split - нарезка на куски")
            print("  denoise - удаление шума (Demucs)")
            print("  vad - удаление тишины (Silero VAD)")
            print("  diar - диаризация говорящих (PyAnnote)")
            new_steps = input(f"Этапы через пробел (по умолчанию {' '.join(args.steps)}): ").strip()
            if new_steps:
                args.steps = new_steps.split()
            
            # Использование GPU
            use_gpu = input("Использовать GPU для VAD? (y/n, по умолчанию n): ").strip().lower()
            args.use_gpu = use_gpu in ['y', 'yes', 'да']
        
        print(f"\nЗапуск обработки с параметрами:")
        print(f"  Вход: {args.input}")
        print(f"  Выход: {args.output}")
        print(f"  Длительность куска: {args.chunk_duration} сек")
        print(f"  Минимальная длительность сегмента спикера: {args.min_speaker_segment} сек")
        print(f"  Метод разделения: {args.split_method}")
        print(f"  Этапы: {', '.join(args.steps)}")
        print(f"  Использовать GPU для VAD: {'Да' if args.use_gpu else 'Нет'}")
        
        confirm = input("\nПродолжить? (y/n, по умолчанию y): ").strip().lower()
        if confirm in ['n', 'no', 'нет']:
            print("Обработка отменена.")
            return

    logger.info(f"Входные параметры: {vars(args)}")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    chunk_duration = args.chunk_duration
    steps = args.steps
    split_method = args.split_method

    # Проверяем существование входного файла/папки
    if not input_path.exists():
        logger.error(f"Входной файл/папка не найден: {input_path}")
        print(f"\nОШИБКА: Файл или папка '{input_path}' не существует!")
        print("Проверьте правильность пути и попробуйте снова.")
        return

    files = []
    if input_path.is_file():
        files = [input_path]
        logger.info(f"Обрабатываем один файл: {input_path}")
        print(f"\nНайден файл: {input_path}")
    elif input_path.is_dir():
        files = list(input_path.glob('*.mp3')) + list(input_path.glob('*.wav'))
        logger.info(f"Найдено {len(files)} файлов в папке: {input_path}")
        print(f"\nНайдено {len(files)} аудиофайлов в папке: {input_path}")
        if not files:
            print("В папке не найдено аудиофайлов (.mp3 или .wav)")
            return
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")
    else:
        logger.error(f"Файл или папка не найдены: {input_path}")
        return

    # Создаем выходную папку
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nРезультаты будут сохранены в: {output_dir}")

    # Создаем временную папку для промежуточных файлов
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.info(f"Создана временная папка: {temp_path}")
        
        # Загружаем модель Whisper только для разделения на границах слов
        whisper_model = None
        if 'split' in steps and split_method == 'word_boundary':
            logger.info("Загружаем модель Whisper для разделения на границах слов...")
            print("Загружаем модель Whisper для анализа границ слов...")
            whisper_model = whisper.load_model("base")

        # Обработка файлов с прогресс-баром
        print(f"\nНачинаем обработку {len(files)} файлов...")
        all_processed_files = []  # Список всех обработанных файлов
        
        with tqdm(total=len(files), desc="Обработка файлов", unit="файл") as pbar_files:
            for audio in files:
                logger.info(f"\n=== Обработка файла: {audio} ===")
                print(f"\n{'='*50}")
                print(f"Обработка: {audio.name}")
                print(f"{'='*50}")
                current = audio
                
                # Создаем временные папки для этого файла
                file_temp_dir = temp_path / audio.stem
                file_temp_dir.mkdir(exist_ok=True)
                
                # 1. Нарезка по 10 минут
                if 'split' in steps:
                    logger.info("Этап 1: Нарезка аудио")
                    print("Этап 1: Нарезка аудио на куски...")
                    if split_method == 'word_boundary':
                        parts = split_audio_at_word_boundary(str(current), file_temp_dir / 'parts', 
                                                           max_duration_sec=chunk_duration, whisper_model=whisper_model, logger=logger)
                    else:
                        parts = split_audio_by_duration(str(current), file_temp_dir / 'parts', 
                                                      max_duration_sec=chunk_duration, logger=logger)
                    logger.info(f"Создано {len(parts)} частей")
                    print(f"Создано {len(parts)} частей")
                else:
                    parts = [str(current)]
                    logger.info("Пропускаем этап нарезки")
                    print("Пропускаем этап нарезки")
                
                # Обработка частей с прогресс-баром
                with tqdm(total=len(parts), desc=f"Обработка частей {audio.stem}", unit="часть") as pbar_parts:
                    for idx, part in enumerate(parts):
                        part_path = Path(part)
                        print(f"\n--- Часть {idx+1}/{len(parts)} ---")
                        
                        # 2. Шумоподавление
                        if 'denoise' in steps:
                            logger.info(f"Этап 2: Шумоподавление части {idx+1}")
                            print("Этап 2: Удаление шума (Demucs)...")
                            cleaned = clean_audio_with_demucs(str(part_path), file_temp_dir / 'cleaned', logger=logger)
                        else:
                            cleaned = str(part_path)
                            logger.info("Пропускаем этап шумоподавления")
                            print("Пропускаем этап шумоподавления")
                        
                        # 3. Удаление тишины
                        if 'vad' in steps:
                            logger.info(f"Этап 3: Удаление тишины части {idx+1}")
                            print("Этап 3: Удаление тишины (Silero VAD)...")
                            no_silence = remove_silence_with_silero(cleaned, use_gpu=args.use_gpu, logger=logger)
                        else:
                            no_silence = cleaned
                            logger.info("Пропускаем этап удаления тишины")
                            print("Пропускаем этап удаления тишины")
                        
                        # 4. Диаризация
                        if 'diar' in steps:
                            logger.info(f"Этап 4: Диаризация части {idx+1}")
                            print("Этап 4: Диаризация говорящих (PyAnnote)...")
                            diarized_files = diarize_with_pyannote(no_silence, file_temp_dir / 'diarized', min_segment_duration=args.min_speaker_segment, logger=logger)
                            # diarized_files теперь список файлов спикеров
                            if isinstance(diarized_files, list):
                                all_processed_files.extend(diarized_files)
                            else:
                                all_processed_files.append(diarized_files)
                        else:
                            diarized_files = [no_silence]
                            logger.info("Пропускаем этап диаризации")
                            print("Пропускаем этап диаризации")
                            all_processed_files.extend(diarized_files)
                        
                        pbar_parts.update(1)
                
                pbar_files.update(1)
        
        # Копируем файлы спикеров из временных папок в основную выходную папку
        if 'diar' in steps:
            logger.info("Копирование файлов спикеров в основную выходную папку...")
            print("\nКопирование файлов спикеров...")
            
            speaker_counter = 1
            for file_temp_dir in temp_path.iterdir():
                if file_temp_dir.is_dir():
                    diarized_dir = file_temp_dir / 'diarized'
                    if diarized_dir.exists():
                        for speaker_file in diarized_dir.glob('speaker_*.wav'):
                            # Создаем новое имя с номером
                            new_name = f"speaker_{speaker_counter:04d}.wav"
                            new_path = output_dir / new_name
                            
                            # Копируем файл
                            import shutil
                            shutil.copy2(speaker_file, new_path)
                            logger.info(f"Скопирован: {speaker_file.name} -> {new_name}")
                            speaker_counter += 1
            
            print(f"Скопировано {speaker_counter - 1} файлов спикеров в {output_dir}")
        
        # Обработка завершена - файлы спикеров уже созданы в папках диаризации
        logger.info("=== Обработка завершена ===")
        print("\nОбработка завершена!")
        print("Файлы спикеров созданы в папках диаризации для каждой части.")
    
    logger.info("=== Обработка завершена ===")
    print(f"\n{'='*60}")
    print("ОБРАБОТКА ЗАВЕРШЕНА!")
    print(f"{'='*60}")
    print(f"Результаты сохранены в: {output_dir}")
    print("\nСтруктура результатов:")
    
    # Показываем что создалось
    if output_dir.exists():
        # Показываем файлы спикеров если была диаризация
        if 'diar' in steps:
            speaker_files = list(output_dir.glob('speaker_*.wav'))
            if speaker_files:
                print(f"  speaker_*.wav ({len(speaker_files)} файлов)")
                for speaker_file in speaker_files:
                    try:
                        duration_str = get_mp3_duration(str(speaker_file))
                        print(f"    - {speaker_file.name}: {duration_str}")
                    except:
                        print(f"    - {speaker_file.name}")
    
    print(f"\nЛог обработки сохранен в: audio_processing.log")
    print(f"Временные файлы автоматически удалены")

if __name__ == "__main__":
    main() 