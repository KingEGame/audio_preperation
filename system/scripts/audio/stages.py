"""
Этапы обработки аудио: шумоподавление, удаление тишины, диаризация
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import torch
import torchaudio
from demucs.apply import apply_model
from demucs.audio import AudioFile

# Импорт конфигурации токена
sys.path.append(str(Path(__file__).parent.parent))
from config import get_token, token_exists

def clean_audio_with_demucs_optimized(input_audio, temp_dir, model_manager, gpu_manager, logger=None):
    """
    Оптимизированная очистка аудио с помощью Demucs с лучшим управлением памятью
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    vocals_file = temp_dir / f"{Path(input_audio).stem}_vocals.wav"

    if vocals_file.exists():
        logger.info(f"File already exists: {vocals_file}")
        return str(vocals_file)

    try:
        # Проверяем память перед обработкой
        if not gpu_manager.check_memory(required_gb=2.0):
            logger.warning("Insufficient GPU memory for Demucs, using CPU")
            device = torch.device("cpu")
        else:
            device = gpu_manager.device
        
        logger.info(f"Using device for Demucs: {device}")
        
        # Получаем кэшированную модель
        model = model_manager.get_demucs_model()
        
        # Читаем аудио файл с валидацией
        logger.info(f"Reading audio file: {input_audio}")
        try:
            wav = AudioFile(input_audio).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
            wav = wav.unsqueeze(0).to(device)
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            # Пробуем альтернативный метод чтения
            wav, sr = torchaudio.load(input_audio)
            wav = torchaudio.functional.resample(wav, sr, model.samplerate)
            wav = wav.unsqueeze(0).to(device)
        
        logger.info(f"Audio file loaded. Tensor size: {wav.shape}")

        # Применяем модель с управлением памятью
        logger.info("Applying Demucs model...")
        
        with torch.amp.autocast(device_type='cuda' if device.type == "cuda" else 'cpu'):
            sources = apply_model(model, wav, device=device)
        
        # Сохраняем вокалы
        torchaudio.save(str(vocals_file), sources[0, 0].cpu(), model.samplerate)
        logger.info(f"Saved: {vocals_file}")

        # Очищаем тензоры
        del wav, sources
        gpu_manager.cleanup()
        
        return str(vocals_file)
        
    except Exception as e:
        logger.error(f"Error during audio cleaning: {e}")
        return input_audio

def remove_silence_with_silero_optimized(input_wav, output_wav=None, min_speech_duration_ms=250, 
                                       min_silence_duration_ms=400, window_size_samples=1536, 
                                       sample_rate=16000, use_gpu=False, model_manager=None, 
                                       gpu_manager=None, logger=None):
    """
    Оптимизированное удаление тишины с лучшим управлением памятью
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        import silero_vad
    except ImportError:
        logger.info("Installing silero-vad...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "silero-vad==5.1.2"])
            import silero_vad
            logger.info("✓ silero-vad installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing silero-vad: {e}")
            return input_wav
    
    if output_wav is None:
        output_wav = str(Path(input_wav).with_name(Path(input_wav).stem + "_nosilence.wav"))
    
    logger.info(f"Starting silence removal from file: {input_wav}")
    
    # Определяем устройство
    if use_gpu and gpu_manager and gpu_manager.device.type == "cuda":
        device = gpu_manager.device
        logger.info(f"Using device for VAD: {device}")
    else:
        device = torch.device("cpu")
        logger.info(f"Using device for VAD: {device}")
    
    try:
        # Загружаем аудио
        wav, sr = torchaudio.load(input_wav)
        wav = wav.to(device)
        
        # Ресэмплируем если нужно
        if sr != sample_rate:
            wav = torchaudio.functional.resample(wav, sr, sample_rate)
            sr = sample_rate
        
        # Получаем кэшированную модель
        if model_manager:
            model = model_manager.get_silero_vad_model()
        else:
            model = silero_vad.load_silero_vad()
            model = model.to(device)
        
        # Анализ речи
        speech_timestamps = silero_vad.get_speech_timestamps(
            wav[0],
            model=model,
            sampling_rate=sr,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            window_size_samples=window_size_samples
        )
        
        if not speech_timestamps:
            logger.warning("Speech not found, returning original file.")
            return input_wav
        
        # Создаем аудио без тишины
        speech_audio = torch.cat([wav[:, ts['start']:ts['end']] for ts in speech_timestamps], dim=1)
        torchaudio.save(output_wav, speech_audio.cpu(), sr)
        logger.info(f"File without silence saved: {output_wav}")
        
        # Очищаем
        del wav, speech_audio
        if gpu_manager:
            gpu_manager.cleanup()
        
        return output_wav
        
    except Exception as e:
        logger.error(f"Error during silence removal: {e}")
        return input_wav

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
        logger.error("HuggingFace token file not found. Run setup_diarization.py")
        return input_audio
    
    token = get_token()
    if not token:
        logger.error("HuggingFace token is empty. Run setup_diarization.py")
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
        
        # Выполняем диаризацию
        logger.info("Executing diarization...")
        from pyannote.audio.pipelines.utils.hook import ProgressHook
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
        
        with open(segments_list_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                f.write(f"file '{input_audio}'\n")
                f.write(f"inpoint {segment['start']:.3f}\n")
                f.write(f"outpoint {segment['end']:.3f}\n")
        
        command = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", str(segments_list_file),
            "-c", "copy", str(speaker_file),
            "-y"
        ]
        
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            
            if speaker_file.exists():
                from .utils import get_mp3_duration
                duration_str = get_mp3_duration(str(speaker_file))
                time_parts = duration_str.split(":")
                total_duration = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                
                logger.info(f"Created speaker file {speaker}: {speaker_file.name} "
                           f"({total_duration}s, {len(segments)} segments)")
                speaker_files.append(str(speaker_file))
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating speaker file {speaker}: {e}")
        finally:
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