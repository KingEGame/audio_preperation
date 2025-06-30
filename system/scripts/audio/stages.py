"""
Этапы обработки аудио: шумоподавление, удаление тишины, диаризация
"""

import os
import sys
import subprocess
import logging
import threading
import time
import shutil
from pathlib import Path
import torch
import torchaudio
from demucs.apply import apply_model
from demucs.audio import AudioFile
from tqdm import tqdm

# Импорт конфигурации токена
sys.path.append(str(Path(__file__).parent.parent))
from config import get_token, token_exists

# Глобальная блокировка для диаризации (предотвращает конфликты прогресс-баров)
DIARIZATION_LOCK = threading.Lock()

def clean_audio_with_demucs_optimized(input_audio, temp_dir, model_manager, gpu_manager, logger=None, mode='vocals'):
    """
    Оптимизированная очистка аудио с помощью Demucs с лучшим управлением памятью
    mode: 'vocals' - только вокалы, 'no_vocals' - без вокалов, 'all' - все источники, 'enhanced' - улучшенное аудио
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем разные имена файлов в зависимости от режима
    if mode == 'vocals':
        output_file = temp_dir / f"{Path(input_audio).stem}_vocals.wav"
    elif mode == 'no_vocals':
        output_file = temp_dir / f"{Path(input_audio).stem}_no_vocals.wav"
    elif mode == 'all':
        output_file = temp_dir / f"{Path(input_audio).stem}_enhanced.wav"
    elif mode == 'enhanced':
        output_file = temp_dir / f"{Path(input_audio).stem}_enhanced.wav"
    else:
        output_file = temp_dir / f"{Path(input_audio).stem}_cleaned.wav"

    if output_file.exists():
        logger.info(f"File already exists: {output_file}")
        return str(output_file)

    try:
        # Проверяем память перед обработкой
        if not gpu_manager.check_memory(required_gb=3.0):
            logger.warning("Insufficient GPU memory for Demucs, using CPU")
            device = torch.device("cpu")
        else:
            device = gpu_manager.device
        
        logger.info(f"Using device for Demucs: {device}")
        logger.info(f"Processing mode: {mode}")
        
        # Получаем кэшированную модель
        model = model_manager.get_demucs_model()
        
        # Читаем аудио файл с валидацией
        logger.info(f"Reading audio file: {input_audio}")
        try:
            wav = AudioFile(input_audio).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
            wav = wav.unsqueeze(0)
        except Exception as e:
            logger.error(f"Error reading audio file with AudioFile: {e}")
            # Пробуем альтернативный метод чтения
            try:
                wav, sr = torchaudio.load(input_audio)
                wav = torchaudio.functional.resample(wav, sr, model.samplerate)
                wav = wav.unsqueeze(0)
            except Exception as e2:
                logger.error(f"Error reading audio file with torchaudio: {e2}")
                return input_audio
        
        # Проверяем размер тензора
        if wav.numel() == 0:
            logger.error("Audio tensor is empty")
            return input_audio
        
        logger.info(f"Audio file loaded. Tensor size: {wav.shape}")
        
        # Проверяем уровень громкости исходного аудио
        original_rms = torch.sqrt(torch.mean(wav**2))
        logger.info(f"Original audio RMS: {original_rms:.6f}")
        
        if original_rms < 0.001:
            logger.warning("Original audio is very quiet, skipping Demucs processing")
            return input_audio
        
        # Перемещаем на устройство
        wav = wav.to(device, dtype=torch.float32)
        
        # Применяем модель с улучшенным управлением памятью
        logger.info("Applying Demucs model...")
        
        try:
            with torch.no_grad():
                sources = apply_model(model, wav, device=device)
            
            # Проверяем результат
            if sources is None or sources.numel() == 0:
                logger.error("Demucs returned empty result")
                return input_audio
            
            logger.info(f"Demucs sources shape: {sources.shape}")
            
            # Обрабатываем результат в зависимости от режима
            if mode == 'vocals':
                # Только вокалы (индекс 0)
                result = sources[0, 0]
                logger.info("Extracting vocals only")
            elif mode == 'no_vocals':
                # Все кроме вокалов (индексы 1, 2, 3)
                result = sources[0, 1] + sources[0, 2] + sources[0, 3]
                logger.info("Extracting non-vocal components")
            elif mode == 'all':
                # Все источники вместе
                result = sources[0, 0] + sources[0, 1] + sources[0, 2] + sources[0, 3]
                logger.info("Combining all sources")
            elif mode == 'enhanced':
                # Улучшенное аудио: вокалы + немного остального
                vocals = sources[0, 0]
                other = (sources[0, 1] + sources[0, 2] + sources[0, 3]) * 0.3  # Уменьшаем фоновые звуки
                result = vocals + other
                logger.info("Creating enhanced audio (vocals + reduced background)")
            else:
                # По умолчанию - вокалы
                result = sources[0, 0]
                logger.info("Default mode: extracting vocals")
            
            # Проверяем уровень громкости результата
            result_rms = torch.sqrt(torch.mean(result**2))
            logger.info(f"Result audio RMS: {result_rms:.6f}")
            
            # Если результат слишком тихий, возвращаем оригинал
            if result_rms < 0.0001:
                logger.warning("Demucs result is too quiet, returning original audio")
                return input_audio
            
            # Нормализуем громкость если нужно
            if result_rms < 0.01:
                logger.info("Normalizing audio volume")
                target_rms = 0.1
                gain = target_rms / result_rms
                result = result * gain
                # Ограничиваем максимальную громкость
                result = torch.clamp(result, -0.95, 0.95)
            
            # Перемещаем на CPU и сохраняем
            result = result.cpu()
            torchaudio.save(str(output_file), result, model.samplerate)
            logger.info(f"Saved: {output_file}")

        except Exception as e:
            logger.error(f"Error during Demucs processing: {e}")
            # Пробуем с CPU если GPU не работает
            if device.type == "cuda":
                logger.info("Retrying with CPU...")
                try:
                    wav_cpu = wav.cpu()
                    model_cpu = model.cpu()
                    with torch.no_grad():
                        sources = apply_model(model_cpu, wav_cpu, device=torch.device("cpu"))
                    
                    # Обрабатываем результат
                    if mode == 'vocals':
                        result = sources[0, 0]
                    elif mode == 'no_vocals':
                        result = sources[0, 1] + sources[0, 2] + sources[0, 3]
                    elif mode == 'all':
                        result = sources[0, 0] + sources[0, 1] + sources[0, 2] + sources[0, 3]
                    elif mode == 'enhanced':
                        vocals = sources[0, 0]
                        other = (sources[0, 1] + sources[0, 2] + sources[0, 3]) * 0.3
                        result = vocals + other
                    else:
                        result = sources[0, 0]
                    
                    torchaudio.save(str(output_file), result, model.samplerate)
                    logger.info(f"Saved with CPU: {output_file}")
                except Exception as e2:
                    logger.error(f"CPU processing also failed: {e2}")
                    return input_audio
            else:
                return input_audio

        # Очищаем тензоры
        del wav
        if 'sources' in locals():
            del sources
        if 'result' in locals():
            del result
        gpu_manager.cleanup()
        
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error during audio cleaning: {e}")
        return input_audio

def diarize_with_pyannote_optimized(input_audio, output_dir, min_segment_duration=0.1, 
                                   chunk_info=None, model_manager=None, gpu_manager=None, logger=None):
    """
    Оптимизированная диаризация спикеров с организацией по папкам и метками времени
    chunk_info: dict с информацией о чанке (start_time, end_time, chunk_number)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Проверяем доступность токена
    if not token_exists():
        logger.warning("HuggingFace token file not found. Skipping diarization.")
        logger.info("To enable diarization, run: setup_diarization.bat")
        return input_audio
    
    token = get_token()
    if not token:
        logger.warning("HuggingFace token is empty. Skipping diarization.")
        logger.info("To enable diarization, run: setup_diarization.bat")
        return input_audio

    # Создаем выходную папку
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting diarization of file: {input_audio}")
    if chunk_info:
        logger.info(f"Chunk info: {chunk_info}")
    
    try:
        # Получаем кэшированный пайплайн
        if model_manager:
            pipeline = model_manager.get_diarization_pipeline(token)
        else:
            from pyannote.audio import Pipeline
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token
            )
            if gpu_manager and gpu_manager.device.type == "cuda":
                pipeline = pipeline.to(gpu_manager.device)
        
        # Выполняем диаризацию с блокировкой для предотвращения конфликтов прогресс-баров
        logger.info("Executing diarization...")
        from pyannote.audio.pipelines.utils.hook import ProgressHook
        
        with DIARIZATION_LOCK:
            with ProgressHook() as hook:
                diarization = pipeline(input_audio, hook=hook)
        
        # Анализируем результаты
        speakers = set()
        total_duration = 0
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        logger.info(f"Diarization completed! Speakers: {len(speakers)}, Duration: {total_duration:.2f}s")
        
        # Сохраняем результаты RTTM
        rttm_file = output_dir / f"{Path(input_audio).stem}_diarization.rttm"
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        # Создаем файлы спикеров с метками времени
        speaker_files = create_speaker_segments_with_metadata(
            input_audio, diarization, output_dir, min_segment_duration, 
            chunk_info, logger
        )
        
        # Очищаем
        if gpu_manager:
            gpu_manager.cleanup()
        
        return speaker_files if speaker_files else [input_audio]
        
    except Exception as e:
        logger.error(f"Error during diarization: {e}")
        logger.warning("Diarization failed, returning original file without speaker separation")
        logger.info("To fix diarization issues:")
        logger.info("1. Run: setup_diarization.bat")
        logger.info("2. Or run: test_diarization_token.bat")
        return input_audio

def create_speaker_segments_with_metadata(input_audio, diarization_result, output_dir, 
                                        min_segment_duration=0.3, chunk_info=None, logger=None):
    """
    Создание сегментов спикеров с метками времени и организацией по папкам
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    speaker_files = []
    speaker_segments = {}
    
    logger.info(f"Creating speaker segments from file: {input_audio}")
    
    # Группируем сегменты по спикерам
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end
        duration = end_time - start_time
        
        # Проверяем ограничение только если min_segment_duration > 0
        if min_segment_duration > 0 and duration < min_segment_duration:
            continue
        
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        
        # Добавляем информацию о чанке если есть
        segment_info = {
            'start': start_time,
            'end': end_time,
            'duration': duration,
            'chunk_info': chunk_info
        }
        
        speaker_segments[speaker].append(segment_info)
    
    logger.info(f"Found {len(speaker_segments)} speakers with segments")
    
    # Создаем файлы для каждого спикера
    for speaker, segments in speaker_segments.items():
        if not segments:
            continue
        
        segments.sort(key=lambda x: x['start'])
        
        # Создаем папку для спикера
        speaker_dir = output_dir / f"speaker_{speaker}"
        speaker_dir.mkdir(exist_ok=True)
        
        # Создаем файл с метками времени
        metadata_file = speaker_dir / f"metadata_{Path(input_audio).stem}.txt"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"Speaker: {speaker}\n")
            f.write(f"Source file: {Path(input_audio).name}\n")
            if chunk_info:
                f.write(f"Chunk: {chunk_info.get('chunk_number', 'unknown')}\n")
                f.write(f"Chunk start time: {chunk_info.get('start_time', 0):.2f}s\n")
                f.write(f"Chunk end time: {chunk_info.get('end_time', 0):.2f}s\n")
            f.write(f"Total segments: {len(segments)}\n")
            f.write(f"Total duration: {sum(s['duration'] for s in segments):.2f}s\n\n")
            f.write("Segments:\n")
            f.write("-" * 50 + "\n")
            
            for i, segment in enumerate(segments, 1):
                f.write(f"{i:3d}. {segment['start']:8.2f}s - {segment['end']:8.2f}s "
                       f"(duration: {segment['duration']:6.2f}s)\n")
        
        # Создаем аудиофайл для спикера
        speaker_file = speaker_dir / f"speaker_{speaker}_{Path(input_audio).stem}.wav"
        segments_list_file = speaker_dir / f"segments_{speaker}_{Path(input_audio).stem}.txt"
        
        # Метод 1: Создаем файл списка сегментов для FFmpeg concat
        with open(segments_list_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                # Используем абсолютный путь для надежности
                abs_input_path = str(Path(input_audio).absolute())
                f.write(f"file '{abs_input_path}'\n")
                f.write(f"inpoint {segment['start']:.3f}\n")
                f.write(f"outpoint {segment['end']:.3f}\n")
        
        # Метод 1: Пробуем FFmpeg concat с copy
        success = False
        try:
            command = [
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", str(segments_list_file),
                "-c", "copy", str(speaker_file),
                "-y"
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and speaker_file.exists():
                from .utils import get_mp3_duration
                duration_str = get_mp3_duration(str(speaker_file))
                time_parts = duration_str.split(":")
                total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                
                logger.info(f"Created speaker file {speaker}: {speaker_file.name} "
                           f"({total_duration}s, {len(segments)} segments)")
                speaker_files.append(str(speaker_file))
                success = True
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"FFmpeg concat with copy failed for {speaker}: {e}")
            if e.stderr:
                logger.debug(f"FFmpeg stderr: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning(f"FFmpeg concat timeout for {speaker}")
        except Exception as e:
            logger.warning(f"FFmpeg concat error for {speaker}: {e}")
        
        # Метод 2: Если concat не сработал, пробуем с перекодированием
        if not success:
            try:
                command = [
                    "ffmpeg", "-f", "concat", "-safe", "0",
                    "-i", str(segments_list_file),
                    "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                    str(speaker_file), "-y"
                ]
                
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and speaker_file.exists():
                    from .utils import get_mp3_duration
                    duration_str = get_mp3_duration(str(speaker_file))
                    time_parts = duration_str.split(":")
                    total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                    
                    logger.info(f"Created speaker file {speaker} (recode): {speaker_file.name} "
                               f"({total_duration}s, {len(segments)} segments)")
                    speaker_files.append(str(speaker_file))
                    success = True
                    
            except subprocess.CalledProcessError as e:
                logger.warning(f"FFmpeg concat with recode failed for {speaker}: {e}")
                if e.stderr:
                    logger.debug(f"FFmpeg stderr: {e.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning(f"FFmpeg concat recode timeout for {speaker}")
            except Exception as e:
                logger.warning(f"FFmpeg concat recode error for {speaker}: {e}")
        
        # Метод 3: Если concat не работает, создаем отдельные файлы и объединяем
        if not success and len(segments) > 0:
            try:
                logger.info(f"Trying alternative method for {speaker}: creating individual segments")
                
                # Создаем временную папку для сегментов
                temp_segments_dir = speaker_dir / "temp_segments"
                temp_segments_dir.mkdir(exist_ok=True)
                
                segment_files = []
                
                # Создаем отдельные файлы для каждого сегмента
                for i, segment in enumerate(segments):
                    segment_file = temp_segments_dir / f"segment_{i:04d}.wav"
                    
                    command = [
                        "ffmpeg", "-i", str(input_audio),
                        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                        "-ss", str(segment['start']), "-t", str(segment['duration']),
                        str(segment_file), "-y"
                    ]
                    
                    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and segment_file.exists():
                        segment_files.append(str(segment_file))
                
                # Объединяем сегменты
                if segment_files:
                    concat_list_file = temp_segments_dir / "concat_list.txt"
                    with open(concat_list_file, 'w', encoding='utf-8') as f:
                        for segment_file in segment_files:
                            f.write(f"file '{segment_file}'\n")
                    
                    command = [
                        "ffmpeg", "-f", "concat", "-safe", "0",
                        "-i", str(concat_list_file),
                        "-c", "copy", str(speaker_file),
                        "-y"
                    ]
                    
                    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0 and speaker_file.exists():
                        from .utils import get_mp3_duration
                        duration_str = get_mp3_duration(str(speaker_file))
                        time_parts = duration_str.split(":")
                        total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        
                        logger.info(f"Created speaker file {speaker} (alternative): {speaker_file.name} "
                                   f"({total_duration}s, {len(segments)} segments)")
                        speaker_files.append(str(speaker_file))
                        success = True
                
                # Очищаем временные файлы
                import shutil
                if temp_segments_dir.exists():
                    shutil.rmtree(temp_segments_dir)
                    
            except Exception as e:
                logger.error(f"Alternative method failed for {speaker}: {e}")
        
        # Если все методы не сработали
        if not success:
            logger.error(f"Failed to create speaker file {speaker} after trying all methods")
        
        # Очищаем временный файл списка
        if segments_list_file.exists():
            segments_list_file.unlink()
    
    logger.info(f"Created {len(speaker_files)} speaker files in {len(speaker_segments)} folders")
    return speaker_files

def organize_speakers_to_output(speaker_folders, output_dir, logger=None):
    """
    Организация файлов спикеров в выходную папку
    speaker_folders: список путей к папкам с файлами спикеров
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    speaker_counter = 1
    organized_speakers = {}
    
    logger.info(f"Organizing speakers to output directory: {output_dir}")
    
    for speaker_folder in speaker_folders:
        speaker_folder = Path(speaker_folder)
        if not speaker_folder.exists() or not speaker_folder.is_dir():
            continue
            
        # Находим все аудиофайлы в папке спикера
        audio_files = list(speaker_folder.glob("*.wav"))
        metadata_files = list(speaker_folder.glob("metadata_*.txt"))
        
        if not audio_files:
            continue
            
        # Определяем имя спикера из папки
        speaker_name = speaker_folder.name
        if speaker_name.startswith("speaker_"):
            speaker_name = speaker_name[8:]  # Убираем "speaker_"
        
        # Создаем папку для спикера в выходной директории
        output_speaker_dir = output_dir / f"speaker_{speaker_counter:04d}"
        output_speaker_dir.mkdir(exist_ok=True)
        
        organized_speakers[speaker_name] = {
            'folder': output_speaker_dir,
            'files': [],
            'metadata': []
        }
        
        # Копируем аудиофайлы
        for audio_file in audio_files:
            new_name = f"chunk_{speaker_counter:04d}_{audio_file.stem}.wav"
            new_path = output_speaker_dir / new_name
            
            import shutil
            shutil.copy2(audio_file, new_path)
            organized_speakers[speaker_name]['files'].append(str(new_path))
            
            logger.info(f"Copied: {audio_file.name} -> {new_name}")
        
        # Копируем метаданные
        for metadata_file in metadata_files:
            new_name = f"metadata_{speaker_counter:04d}_{metadata_file.stem}.txt"
            new_path = output_speaker_dir / new_name
            
            import shutil
            shutil.copy2(metadata_file, new_path)
            organized_speakers[speaker_name]['metadata'].append(str(new_path))
        
        # Создаем общий файл с информацией о спикере
        info_file = output_speaker_dir / f"speaker_{speaker_counter:04d}_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"Speaker ID: {speaker_counter:04d}\n")
            f.write(f"Original Speaker: {speaker_name}\n")
            f.write(f"Total audio files: {len(audio_files)}\n")
            f.write(f"Total metadata files: {len(metadata_files)}\n")
            f.write(f"Folder: {output_speaker_dir}\n\n")
            
            f.write("Audio files:\n")
            for audio_file in audio_files:
                f.write(f"  - {audio_file.name}\n")
            
            f.write("\nMetadata files:\n")
            for metadata_file in metadata_files:
                f.write(f"  - {metadata_file.name}\n")
        
        speaker_counter += 1
    
    logger.info(f"Organized {len(organized_speakers)} speakers to output directory")
    return organized_speakers

def diarize_with_role_classification(input_audio, output_dir, min_segment_duration=0.3, 
                                   chunk_info=None, model_manager=None, gpu_manager=None, logger=None):
    """
    Диаризация с автоматическим разделением на роли (нарратор + персонажи)
    Автоматически определяет количество ролей и объединяет сегменты каждой роли
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Проверяем доступность токена
    if not token_exists():
        logger.warning("HuggingFace token file not found. Skipping diarization.")
        logger.info("To enable diarization, run: setup_diarization.bat")
        return input_audio
    
    token = get_token()
    if not token:
        logger.warning("HuggingFace token is empty. Skipping diarization.")
        logger.info("To enable diarization, run: setup_diarization.bat")
        return input_audio

    # Создаем выходную папку
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting role-based diarization of file: {input_audio}")
    if chunk_info:
        logger.info(f"Chunk info: {chunk_info}")
    
    try:
        # Получаем кэшированный пайплайн
        if model_manager:
            pipeline = model_manager.get_diarization_pipeline(token)
        else:
            from pyannote.audio import Pipeline
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token
            )
            if gpu_manager and gpu_manager.device.type == "cuda":
                pipeline = pipeline.to(gpu_manager.device)
        
        # Выполняем диаризацию
        logger.info("Executing diarization...")
        from pyannote.audio.pipelines.utils.hook import ProgressHook
        
        with DIARIZATION_LOCK:
            with ProgressHook() as hook:
                diarization = pipeline(input_audio, hook=hook)
        
        # Собираем сегменты и получаем эмбеддинги
        segments = []
        embeddings = []
        
        logger.info("Extracting embeddings for role classification...")
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_time = turn.start
            end_time = turn.end
            duration = end_time - start_time
            
            # Проверяем минимальную длительность
            if min_segment_duration > 0 and duration < min_segment_duration:
                continue
            
            # Получаем эмбеддинг для сегмента
            try:
                # Используем метод get_embedding если доступен
                if hasattr(pipeline, 'get_embedding'):
                    emb = pipeline.get_embedding(input_audio, segment=turn)
                else:
                    # Альтернативный способ получения эмбеддинга
                    from pyannote.audio import Audio
                    audio = Audio(sample_rate=16000, mono=True)
                    waveform, sample_rate = audio.crop(input_audio, segment=turn)
                    
                    # Используем модель эмбеддингов
                    from pyannote.audio.models import SegmentationModel
                    model = SegmentationModel.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
                    if gpu_manager and gpu_manager.device.type == "cuda":
                        model = model.to(gpu_manager.device)
                    
                    with torch.no_grad():
                        emb = model(waveform.unsqueeze(0)).mean(dim=1).squeeze().cpu().numpy()
                
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'duration': duration,
                    'speaker': speaker,
                    'original_speaker': speaker
                })
                embeddings.append(emb)
                
            except Exception as e:
                logger.warning(f"Failed to get embedding for segment {start_time:.2f}-{end_time:.2f}: {e}")
                continue
        
        if not segments:
            logger.warning("No valid segments found for role classification")
            return input_audio
        
        logger.info(f"Extracted {len(segments)} segments with embeddings")
        
        # Автоматически определяем количество ролей
        # Минимум 2 (нарратор + персонаж), максимум 10
        n_segments = len(segments)
        n_roles = min(max(2, n_segments // 5), 10)  # Примерно 5 сегментов на роль
        
        logger.info(f"Clustering {len(segments)} segments into {n_roles} roles...")
        
        # Кластеризация эмбеддингов
        try:
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            # Подготавливаем эмбеддинги
            embeddings_array = np.vstack(embeddings)
            
            # Нормализуем эмбеддинги
            scaler = StandardScaler()
            embeddings_scaled = scaler.fit_transform(embeddings_array)
            
            # Кластеризация
            kmeans = KMeans(n_clusters=n_roles, random_state=42, n_init='auto')
            role_labels = kmeans.fit_predict(embeddings_scaled)
            
            # Назначаем роли сегментам
            for i, segment in enumerate(segments):
                segment['role'] = f"role_{role_labels[i]:02d}"
            
            logger.info(f"Successfully classified segments into {n_roles} roles")
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            logger.info("Falling back to original speaker labels")
            for segment in segments:
                segment['role'] = segment['original_speaker']
        
        # Группируем сегменты по ролям
        role_segments = {}
        for segment in segments:
            role = segment['role']
            if role not in role_segments:
                role_segments[role] = []
            role_segments[role].append(segment)
        
        logger.info(f"Grouped segments by roles: {list(role_segments.keys())}")
        
        # Определяем нарратора (самая длинная роль)
        role_durations = {}
        for role, segs in role_segments.items():
            total_duration = sum(s['duration'] for s in segs)
            role_durations[role] = total_duration
        
        # Находим роль с максимальной длительностью (нарратор)
        narrator_role = max(role_durations, key=role_durations.get)
        
        # Создаем файлы для каждой роли
        role_files = []
        
        for role, segs in role_segments.items():
            if not segs:
                continue
            
            # Сортируем сегменты по времени
            segs.sort(key=lambda x: x['start'])
            
            # Определяем имя файла
            if role == narrator_role:
                output_filename = "narrator.wav"
                role_name = "Narrator"
            else:
                # Находим номер персонажа
                character_roles = [r for r in role_segments.keys() if r != narrator_role]
                character_number = character_roles.index(role) + 1
                output_filename = f"character_{character_number:02d}.wav"
                role_name = f"Character {character_number}"
            
            output_file = output_dir / output_filename
            
            # Создаем файл списка сегментов для FFmpeg
            segments_list_file = output_dir / f"segments_{role}.txt"
            
            with open(segments_list_file, 'w', encoding='utf-8') as f:
                for segment in segs:
                    abs_input_path = str(Path(input_audio).absolute())
                    f.write(f"file '{abs_input_path}'\n")
                    f.write(f"inpoint {segment['start']:.3f}\n")
                    f.write(f"outpoint {segment['end']:.3f}\n")
            
            # Создаем аудиофайл с помощью FFmpeg
            success = False
            try:
                command = [
                    "ffmpeg", "-f", "concat", "-safe", "0",
                    "-i", str(segments_list_file),
                    "-c", "copy", str(output_file),
                    "-y"
                ]
                
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and output_file.exists():
                    from .utils import get_mp3_duration
                    duration_str = get_mp3_duration(str(output_file))
                    time_parts = duration_str.split(":")
                    total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                    
                    logger.info(f"Created {role_name} file: {output_filename} "
                               f"({total_duration}s, {len(segs)} segments)")
                    role_files.append(str(output_file))
                    success = True
                    
            except subprocess.CalledProcessError as e:
                logger.warning(f"FFmpeg concat failed for {role_name}: {e}")
            except subprocess.TimeoutExpired:
                logger.warning(f"FFmpeg timeout for {role_name}")
            except Exception as e:
                logger.warning(f"FFmpeg error for {role_name}: {e}")
            
            # Если concat не сработал, пробуем с перекодированием
            if not success:
                try:
                    command = [
                        "ffmpeg", "-f", "concat", "-safe", "0",
                        "-i", str(segments_list_file),
                        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                        str(output_file), "-y"
                    ]
                    
                    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0 and output_file.exists():
                        from .utils import get_mp3_duration
                        duration_str = get_mp3_duration(str(output_file))
                        time_parts = duration_str.split(":")
                        total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        
                        logger.info(f"Created {role_name} file (recode): {output_filename} "
                                   f"({total_duration}s, {len(segs)} segments)")
                        role_files.append(str(output_file))
                        success = True
                        
                except Exception as e:
                    logger.error(f"Failed to create {role_name} file: {e}")
            
            # Очищаем временный файл
            if segments_list_file.exists():
                segments_list_file.unlink()
            
            # Создаем метаданные для роли
            metadata_file = output_dir / f"metadata_{role}.txt"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(f"Role: {role_name}\n")
                f.write(f"Role ID: {role}\n")
                f.write(f"Source file: {Path(input_audio).name}\n")
                if chunk_info:
                    f.write(f"Chunk: {chunk_info.get('chunk_number', 'unknown')}\n")
                    f.write(f"Chunk start time: {chunk_info.get('start_time', 0):.2f}s\n")
                    f.write(f"Chunk end time: {chunk_info.get('end_time', 0):.2f}s\n")
                f.write(f"Total segments: {len(segs)}\n")
                f.write(f"Total duration: {sum(s['duration'] for s in segs):.2f}s\n")
                f.write(f"Is narrator: {'Yes' if role == narrator_role else 'No'}\n\n")
                f.write("Segments:\n")
                f.write("-" * 50 + "\n")
                
                for i, segment in enumerate(segs, 1):
                    f.write(f"{i:3d}. {segment['start']:8.2f}s - {segment['end']:8.2f}s "
                           f"(duration: {segment['duration']:6.2f}s)\n")
        
        # Создаем общий файл с информацией о ролях
        info_file = output_dir / "roles_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("ROLE CLASSIFICATION RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Source file: {Path(input_audio).name}\n")
            f.write(f"Total segments: {len(segments)}\n")
            f.write(f"Total roles detected: {len(role_segments)}\n")
            f.write(f"Narrator role: {narrator_role}\n\n")
            
            f.write("Role details:\n")
            f.write("-" * 30 + "\n")
            for role, segs in role_segments.items():
                total_duration = sum(s['duration'] for s in segs)
                is_narrator = "Yes" if role == narrator_role else "No"
                f.write(f"Role {role}: {len(segs)} segments, {total_duration:.2f}s, Narrator: {is_narrator}\n")
        
        logger.info(f"Created {len(role_files)} role files in {output_dir}")
        return role_files if role_files else [input_audio]
        
    except Exception as e:
        logger.error(f"Error during role-based diarization: {e}")
        logger.warning("Role-based diarization failed, returning original file")
        return input_audio