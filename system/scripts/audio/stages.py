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

def diarize_with_pyannote_optimized(input_audio, output_dir, min_segment_duration=1.5, 
                                   model_manager=None, gpu_manager=None, logger=None):
    """
    Оптимизированная диаризация спикеров с лучшим управлением памятью
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
    
    output_file = output_dir / f"{Path(input_audio).stem}_diarized.wav"
    
    logger.info(f"Starting diarization of file: {input_audio}")
    
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
        
        # Сохраняем результаты
        rttm_file = output_file.with_suffix('.rttm')
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        # Создаем файлы спикеров
        speaker_files = create_speaker_segments_optimized(
            input_audio, diarization, output_dir, min_segment_duration, logger
        )
        
        # Очищаем
        if gpu_manager:
            gpu_manager.cleanup()
        
        return speaker_files if speaker_files else [input_audio]
        
    except Exception as e:
        logger.error(f"Error during diarization: {e}")
        return input_audio

def create_speaker_segments_optimized(input_audio, diarization_result, output_dir, 
                                    min_segment_duration=1.5, logger=None):
    """
    Оптимизированное создание сегментов спикеров
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
        
        if duration < min_segment_duration:
            continue
        
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        
        speaker_segments[speaker].append({
            'start': start_time,
            'end': end_time,
            'duration': duration
        })
    
    logger.info(f"Found {len(speaker_segments)} speakers with segments")
    
    # Создаем файлы для каждого спикера
    for speaker, segments in speaker_segments.items():
        if not segments:
            continue
        
        segments.sort(key=lambda x: x['start'])
        speaker_file = output_dir / f"speaker_{speaker}.wav"
        segments_list_file = output_dir / f"segments_{speaker}.txt"
        
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
                
                logger.info(f"Created speaker file {speaker}: {speaker_file.name} ({total_duration}s, {len(segments)} segments)")
                speaker_files.append(str(speaker_file))
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating speaker file {speaker}: {e}")
        finally:
            if segments_list_file.exists():
                segments_list_file.unlink()
    
    logger.info(f"Created {len(speaker_files)} speaker files")
    return speaker_files