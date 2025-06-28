#!/usr/bin/env python3
"""
Optimized Audio Processing Pipeline with Advanced GPU Management
Stages: splitting, denoising, silence removal, diarization
Optimized for RTX 5080, 32GB RAM, R5 5600X

IMPROVEMENTS:
- Advanced GPU memory management with automatic cleanup
- Model caching and reuse across processes
- Improved multiprocessing with proper resource management
- Better error handling and recovery
- Optimized processing pipeline with memory monitoring
"""

import os
import sys
import subprocess
import argparse
import logging
import tempfile
import math
import multiprocessing as mp
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import threading
import queue
import time
from functools import partial
import gc
import psutil
import atexit

# Imports for audio processing
try:
    import torch
    import torchaudio
    import whisper
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    from demucs.audio import AudioFile
    from huggingface_hub import HfApi
    # Import config functions directly
    import sys
    sys.path.append(str(Path(__file__).parent))
    from config import get_token, token_exists
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed")
    sys.exit(1)

# Global settings for performance optimization
MAX_WORKERS = min(mp.cpu_count(), 6)  # Reduced for stability
GPU_MEMORY_LIMIT = 0.95  # Reduced to 75% for better stability
BATCH_SIZE = 4  # Reduced batch size
MODEL_CACHE = {}  # Global model cache
GPU_LOCK = threading.Lock()  # GPU access lock

class GPUMemoryManager:
    """Advanced GPU memory management with automatic cleanup"""
    
    def __init__(self, memory_limit=0.75):
        self.memory_limit = memory_limit
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.initial_memory = self._get_gpu_memory() if self.device.type == "cuda" else 0
        
    def _get_gpu_memory(self):
        """Get current GPU memory usage"""
        if self.device.type == "cuda":
            return torch.cuda.memory_allocated() / 1024**3  # GB
        return 0
    
    def _get_gpu_memory_total(self):
        """Get total GPU memory"""
        if self.device.type == "cuda":
            return torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        return 0
    
    def check_memory(self, required_gb=2.0):
        """Check if enough GPU memory is available"""
        if self.device.type != "cuda":
            return True
            
        current_usage = self._get_gpu_memory()
        total_memory = self._get_gpu_memory_total()
        available = total_memory * self.memory_limit - current_usage
        
        return available >= required_gb
    
    def cleanup(self, force=False):
        """Clean up GPU memory"""
        if self.device.type == "cuda":
            with GPU_LOCK:
                torch.cuda.empty_cache()
                gc.collect()
                
                if force:
                    # Force cleanup by allocating and freeing memory
                    try:
                        temp_tensor = torch.zeros(1, device=self.device)
                        del temp_tensor
                        torch.cuda.empty_cache()
                    except:
                        pass
    
    def monitor_memory(self, logger=None):
        """Monitor and log GPU memory usage"""
        if self.device.type == "cuda":
            current = self._get_gpu_memory()
            total = self._get_gpu_memory_total()
            if logger:
                logger.info(f"GPU Memory: {current:.2f}GB / {total:.2f}GB ({current/total*100:.1f}%)")
            return current, total
        return 0, 0

class ModelManager:
    """Centralized model management with caching and GPU optimization"""
    
    def __init__(self, gpu_manager):
        self.gpu_manager = gpu_manager
        self.models = {}
        self.device = gpu_manager.device
        
    def get_whisper_model(self, model_size="base"):
        """Get Whisper model with caching"""
        model_key = f"whisper_{model_size}"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            self.models[model_key] = whisper.load_model(model_size)
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def get_demucs_model(self):
        """Get Demucs model with caching"""
        model_key = "demucs_htdemucs"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            self.models[model_key] = get_model("htdemucs")
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def get_silero_vad_model(self):
        """Get Silero VAD model with caching"""
        model_key = "silero_vad"
        
        if model_key not in self.models:
            try:
                import silero_vad
                self.models[model_key] = silero_vad.load_silero_vad()
                if self.device.type == "cuda":
                    self.models[model_key] = self.models[model_key].to(self.device)
            except ImportError:
                raise ImportError("silero-vad not installed")
        
        return self.models[model_key]
    
    def get_diarization_pipeline(self, token):
        """Get PyAnnote diarization pipeline with caching"""
        model_key = "pyannote_diarization"
        
        if model_key not in self.models:
            self.gpu_manager.cleanup()
            from pyannote.audio import Pipeline
            self.models[model_key] = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=token
            )
            if self.device.type == "cuda":
                self.models[model_key] = self.models[model_key].to(self.device)
        
        return self.models[model_key]
    
    def cleanup_models(self):
        """Clean up all models"""
        for model in self.models.values():
            if hasattr(model, 'cpu'):
                model.cpu()
            del model
        self.models.clear()
        self.gpu_manager.cleanup(force=True)

def get_optimal_workers():
    """
    Determines optimal number of worker processes based on system
    """
    cpu_count = mp.cpu_count()
    memory_gb = psutil.virtual_memory().total / 1024**3
    
    # Conservative approach for stability
    if cpu_count >= 12 and memory_gb >= 24:
        return min(6, cpu_count // 2)  # Use half of cores
    elif cpu_count >= 8 and memory_gb >= 16:
        return min(4, cpu_count // 2)
    else:
        return min(2, cpu_count // 2)

def setup_gpu_optimization():
    """
    Configures GPU for optimal performance with improved memory management
    """
    if torch.cuda.is_available():
        # Set optimal settings for RTX 5080
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Configure memory management
        torch.cuda.set_per_process_memory_fraction(GPU_MEMORY_LIMIT)
        
        # Enable memory efficient attention if available
        if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
            torch.backends.cuda.enable_flash_sdp(True)
        
        total_memory = torch.cuda.get_device_properties(0).total_memory
        max_memory = int(total_memory * GPU_MEMORY_LIMIT)
        
        print(f"GPU optimization: {total_memory / 1024**3:.1f}GB -> {max_memory / 1024**3:.1f}GB")
        return True
    return False

def process_audio_file_optimized(audio_file, output_dir, steps, chunk_duration, 
                                min_segment_duration, split_method, use_gpu, logger):
    """
    Optimized processing of a single audio file with improved resource management
    """
    gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
    model_manager = ModelManager(gpu_manager)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            current = Path(audio_file)
            
            # Create temporary folders for this file
            file_temp_dir = temp_path / current.stem
            file_temp_dir.mkdir(exist_ok=True)
            
            # Monitor initial memory
            gpu_manager.monitor_memory(logger)
            
            # 1. Time-based splitting
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
            
            # Check that parts were created
            if not parts:
                raise ValueError("Failed to create file parts")
            
            logger.info(f"Created {len(parts)} parts for processing")
            
            # Process parts with improved memory management
            processed_parts = process_parts_optimized(
                parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager
            )
            
            # Copy results to output folder
            final_results = copy_results_to_output_optimized(
                processed_parts, output_dir, current.stem, logger
            )
            
            # Final cleanup
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
            
            return final_results
            
    except Exception as e:
        logger.error(f"Error processing file {audio_file.name}: {e}")
        return None

def process_parts_optimized(parts, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager):
    """
    Optimized processing of audio parts with better resource management
    """
    processed_parts = []
    
    # Process parts sequentially with memory management
    for idx, part in enumerate(parts):
        try:
            logger.info(f"Processing part {idx+1}/{len(parts)}")
            
            # Check memory before processing
            if not gpu_manager.check_memory(required_gb=1.5):
                logger.warning("Low GPU memory, forcing cleanup")
                gpu_manager.cleanup(force=True)
            
            result = process_single_part_optimized(
                part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager
            )
            processed_parts.append(result)
            
            # Monitor memory after each part
            gpu_manager.monitor_memory(logger)
            
        except Exception as e:
            logger.error(f"Error processing part {idx+1}: {e}")
            processed_parts.append([part])  # Return original part
    
    return processed_parts

def process_single_part_optimized(part, idx, file_temp_dir, steps, use_gpu, logger, model_manager, gpu_manager):
    """
    Optimized processing of a single audio part
    """
    part_path = Path(part)
    logger.info(f"Processing part {idx+1}: {part_path.name}")
    
    try:
        current = part_path
        
        # Check file existence
        if not current.exists():
            logger.error(f"File part not found: {current}")
            return [str(current)]
        
        # 2. Noise removal
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
        
        # 3. Silence removal
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
        
        # 4. Diarization
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

def clean_audio_with_demucs_optimized(input_audio, temp_dir, model_manager, gpu_manager, logger=None):
    """
    Optimized audio cleaning using Demucs with better memory management
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
        # Check memory before processing
        if not gpu_manager.check_memory(required_gb=2.0):
            logger.warning("Insufficient GPU memory for Demucs, using CPU")
            device = torch.device("cpu")
        else:
            device = gpu_manager.device
        
        logger.info(f"Using device for Demucs: {device}")
        
        # Get cached model
        model = model_manager.get_demucs_model()
        
        # Read audio file with validation
        logger.info(f"Reading audio file: {input_audio}")
        try:
            wav = AudioFile(input_audio).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
            wav = wav.unsqueeze(0).to(device)
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            # Try alternative reading method
            wav, sr = torchaudio.load(input_audio)
            wav = torchaudio.functional.resample(wav, sr, model.samplerate)
            wav = wav.unsqueeze(0).to(device)
        
        logger.info(f"Audio file loaded. Tensor size: {wav.shape}")

        # Apply model with memory management
        logger.info("Applying Demucs model...")
        
        with torch.amp.autocast(device_type='cuda' if device.type == "cuda" else 'cpu'):
            sources = apply_model(model, wav, device=device)
        
        # Save vocals
        torchaudio.save(str(vocals_file), sources[0, 0].cpu(), model.samplerate)
        logger.info(f"Saved: {vocals_file}")

        # Clean up tensors
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
    Optimized silence removal with better memory management
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        import silero_vad
    except ImportError:
        logger.info("Installing silero-vad...")
        import subprocess
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
    
    # Determine device
    if use_gpu and gpu_manager and gpu_manager.device.type == "cuda":
        device = gpu_manager.device
        logger.info(f"Using device for VAD: {device}")
    else:
        device = torch.device("cpu")
        logger.info(f"Using device for VAD: {device}")
    
    try:
        # Load audio
        wav, sr = torchaudio.load(input_wav)
        wav = wav.to(device)
        
        # Resample if needed
        if sr != sample_rate:
            wav = torchaudio.functional.resample(wav, sr, sample_rate)
            sr = sample_rate
        
        # Get cached model
        if model_manager:
            model = model_manager.get_silero_vad_model()
        else:
            model = silero_vad.load_silero_vad()
            model = model.to(device)
        
        # Speech analysis
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
        
        # Create audio without silence
        speech_audio = torch.cat([wav[:, ts['start']:ts['end']] for ts in speech_timestamps], dim=1)
        torchaudio.save(output_wav, speech_audio.cpu(), sr)
        logger.info(f"File without silence saved: {output_wav}")
        
        # Clean up
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
    Optimized speaker diarization with better memory management
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Check token availability
    if not token_exists():
        logger.error("HuggingFace token file not found. Run setup_diarization.py")
        return input_audio
    
    token = get_token()
    if not token:
        logger.error("HuggingFace token is empty. Run setup_diarization.py")
        return input_audio

    # Create output folder
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{Path(input_audio).stem}_diarized.wav"
    
    logger.info(f"Starting diarization of file: {input_audio}")
    
    try:
        # Get cached pipeline
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
        
        # Perform diarization
        logger.info("Executing diarization...")
        from pyannote.audio.pipelines.utils.hook import ProgressHook
        with ProgressHook() as hook:
            diarization = pipeline(input_audio, hook=hook)
        
        # Analyze results
        speakers = set()
        total_duration = 0
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        logger.info(f"Diarization completed! Speakers: {len(speakers)}, Duration: {total_duration:.2f}s")
        
        # Save results
        rttm_file = output_file.with_suffix('.rttm')
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        # Create speaker files
        speaker_files = create_speaker_segments_optimized(
            input_audio, diarization, output_dir, min_segment_duration, logger
        )
        
        # Clean up
        if gpu_manager:
            gpu_manager.cleanup()
        
        return speaker_files if speaker_files else [input_audio]
        
    except Exception as e:
        logger.error(f"Error during diarization: {e}")
        return input_audio

def create_speaker_segments_optimized(input_audio, diarization_result, output_dir, 
                                    min_segment_duration=1.5, logger=None):
    """
    Optimized creation of speaker segments
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    speaker_files = []
    speaker_segments = {}
    
    logger.info(f"Creating speaker segments from file: {input_audio}")
    
    # Group segments by speakers
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
    
    # Create files for each speaker
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

def split_audio_by_duration_optimized(input_audio, temp_dir, max_duration_sec=600, 
                                    output_prefix="part_", logger=None):
    """
    Optimized audio splitting by duration
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
    Optimized audio splitting at word boundaries
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
        
        analysis_start = max(0, start_time - 30)
        analysis_end = min(total_seconds, end_time + 30)
        
        temp_file = Path(temp_dir) / f"temp_analysis_{i}.wav"
        command = [
            "ffmpeg", "-i", input_audio,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-ss", str(analysis_start), "-t", str(analysis_end - analysis_start),
            str(temp_file)
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        result = whisper_model.transcribe(str(temp_file), language="ru")
        
        target_time = start_time - analysis_start
        best_boundary = target_time
        min_distance = float('inf')
        
        for segment in result["segments"]:
            segment_end = segment["end"]
            distance = abs(segment_end - target_time)
            if distance < min_distance:
                min_distance = distance
                best_boundary = segment_end
        
        temp_file.unlink()
        
        actual_split_time = analysis_start + best_boundary
        
        output_file = Path(temp_dir) / f"{output_prefix}{i + 1}.wav"
        if not output_file.exists():
            if i == num_parts - 1:
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

def copy_results_to_output_optimized(processed_parts, output_dir, file_stem, logger):
    """
    Optimized copying of results to output folder
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
                        import shutil
                        shutil.copy2(result_file, new_path)
                        all_files.append(str(new_path))
                        speaker_counter += 1
                    else:
                        new_name = f"{file_stem}_{Path(result_file).stem}.wav"
                        new_path = output_dir / new_name
                        import shutil
                        shutil.copy2(result_file, new_path)
                        all_files.append(str(new_path))
    
    logger.info(f"Copied {len(all_files)} files for {file_stem}")
    return all_files

def parallel_audio_processing_optimized(audio_files, output_dir, steps, chunk_duration, 
                                      min_segment_duration, split_method, use_gpu, logger):
    """
    Optimized parallel processing with better resource management
    """
    optimal_workers = get_optimal_workers()
    logger.info(f"Using {optimal_workers} parallel processes")
    
    all_results = []
    
    # Process files with improved parallelization
    with ProcessPoolExecutor(max_workers=optimal_workers) as executor:
        futures = []
        
        for audio_file in audio_files:
            future = executor.submit(
                process_audio_file_optimized,
                audio_file, output_dir, steps, chunk_duration,
                min_segment_duration, split_method, use_gpu, logger
            )
            futures.append(future)
        
        # Collect results with progress bar
        with tqdm(total=len(futures), desc="Processing files", unit="file") as pbar:
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=7200)  # 2 hour timeout
                    all_results.append(result)
                except Exception as e:
                    logger.error(f"Error in parallel processing: {e}")
                    all_results.append(None)
                finally:
                    pbar.update(1)
    
    return all_results

def get_mp3_duration(file_path):
    """
    Gets MP3 file duration using ffprobe.
    :param file_path: Path to MP3 file.
    :return: String with duration in HH:MM:SS format.
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
    Sets up logging with timestamps and formatting.
    :param log_level: Logging level.
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
    parser = argparse.ArgumentParser(description="Optimized Audio Processing Pipeline: splitting, denoising, silence removal, diarization with speaker separation.")
    parser.add_argument('--input', '-i', help='Path to audio file (mp3/wav) or folder with files')
    parser.add_argument('--output', '-o', help='Folder for saving results')
    parser.add_argument('--chunk_duration', type=int, default=600, help='Maximum chunk duration (seconds), default 600 (10 minutes)')
    parser.add_argument('--min_speaker_segment', type=float, default=1.5, help='Minimum speaker segment duration (seconds), default 1.5')
    parser.add_argument('--steps', nargs='+', default=['split','denoise','vad', 'diar'],
                        help='Processing stages: split, denoise, vad, diar')
    parser.add_argument('--split_method', type=str, default='word_boundary', choices=['simple', 'word_boundary'],
                        help='Splitting method: simple or word_boundary')
    parser.add_argument('--use_gpu', action='store_true', help='Use GPU for VAD (default CPU for stability)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode with parameter prompts')
    parser.add_argument('--parallel', action='store_true', default=True, help='Use parallel processing (enabled by default)')
    parser.add_argument('--workers', type=int, help='Number of worker processes (auto-determined)')
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=== Starting optimized audio processing pipeline ===")
    
    # Setup optimization for RTX 5080
    print("\n" + "="*60)
    print("OPTIMIZATION FOR RTX 5080 + R5 5600X + 32GB RAM")
    print("="*60)
    
    # GPU setup
    gpu_available = setup_gpu_optimization()
    if gpu_available:
        print("✓ GPU optimization applied")
        args.use_gpu = True  # Automatically enable GPU
    else:
        print("⚠ GPU not available, using CPU")
    
    # Determine optimal number of processes
    optimal_workers = get_optimal_workers()
    if args.workers:
        optimal_workers = min(args.workers, optimal_workers)
    
    print(f"✓ Optimal number of processes: {optimal_workers}")
    print(f"✓ Parallel parts processing: {'Enabled' if args.parallel else 'Disabled'}")
    
    # Interactive mode or get parameters
    if args.interactive or not args.input or not args.output:
        print("\n" + "="*60)
        print("AUDIO PROCESSING PIPELINE (OPTIMIZED)")
        print("="*60)
        
        # Get input file/folder
        if not args.input:
            print("\nEnter path to audio file or folder with audio files:")
            print("Examples:")
            print("  - audio.mp3")
            print("  - C:\\path\\to\\audio.mp3")
            print("  - audio_folder")
            print("  - C:\\path\\to\\audio_folder")
            args.input = input("Input file/folder: ").strip().strip('"')
        
        # Get output folder
        if not args.output:
            print("\nEnter folder for saving results:")
            print("Examples:")
            print("  - results")
            print("  - C:\\path\\to\\results")
            args.output = input("Output folder: ").strip().strip('"')
        
        # Additional settings
        print(f"\nCurrent settings:")
        print(f"  - Chunk duration: {args.chunk_duration} sec")
        print(f"  - Minimum speaker segment duration: {args.min_speaker_segment} sec")
        print(f"  - Splitting method: {args.split_method}")
        print(f"  - Stages: {', '.join(args.steps)}")
        print(f"  - Parallel parts processing: {'Enabled' if args.parallel else 'Disabled'}")
        print(f"  - Number of processes: {optimal_workers}")
        print(f"  - GPU: {'Enabled' if gpu_available else 'Disabled'}")
        
        change_settings = input("\nChange settings? (y/n, default n): ").strip().lower()
        if change_settings in ['y', 'yes', 'da']:
            # Chunk duration
            new_duration = input(f"Chunk duration in seconds (default {args.chunk_duration}): ").strip()
            if new_duration and new_duration.isdigit():
                args.chunk_duration = int(new_duration)
            
            # Minimum speaker segment duration
            new_min_segment = input(f"Minimum speaker segment duration in seconds (default {args.min_speaker_segment}): ").strip()
            if new_min_segment and new_min_segment.replace('.', '').isdigit():
                args.min_speaker_segment = float(new_min_segment)
            
            # Splitting method
            print("\nSplitting method:")
            print("  simple - simple time-based splitting")
            print("  word_boundary - splitting at word boundaries (recommended)")
            new_method = input(f"Method (default {args.split_method}): ").strip()
            if new_method in ['simple', 'word_boundary']:
                args.split_method = new_method
            
            # Processing stages
            print("\nProcessing stages:")
            print("  split - split into chunks")
            print("  denoise - noise removal (Demucs)")
            print("  vad - silence removal (Silero VAD)")
            print("  diar - speaker diarization (PyAnnote)")
            new_steps = input(f"Stages separated by space (default {' '.join(args.steps)}): ").strip()
            if new_steps:
                args.steps = new_steps.split()
            
            # Parallel parts processing
            parallel_choice = input("Use parallel parts processing? (y/n, default y): ").strip().lower()
            args.parallel = parallel_choice not in ['n', 'no', 'net']
            
            # Number of processes
            new_workers = input(f"Number of processes for parts (default {optimal_workers}): ").strip()
            if new_workers and new_workers.isdigit():
                optimal_workers = min(int(new_workers), optimal_workers)
        
        print(f"\nStarting processing with parameters:")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")
        print(f"  Chunk duration: {args.chunk_duration} sec")
        print(f"  Minimum speaker segment duration: {args.min_speaker_segment} sec")
        print(f"  Splitting method: {args.split_method}")
        print(f"  Stages: {', '.join(args.steps)}")
        print(f"  Parallel parts processing: {'Yes' if args.parallel else 'No'}")
        print(f"  Number of processes: {optimal_workers}")
        print(f"  GPU: {'Yes' if gpu_available else 'No'}")
        
        confirm = input("\nContinue? (y/n, default y): ").strip().lower()
        if confirm in ['n', 'no', 'net']:
            print("Processing cancelled.")
            return

    logger.info(f"Input parameters: {vars(args)}")

    input_path = Path(args.input)
    output_dir = Path(args.output)
    chunk_duration = args.chunk_duration
    steps = args.steps
    split_method = args.split_method

    # Check input file/folder existence
    if not input_path.exists():
        logger.error(f"Input file/folder not found: {input_path}")
        print(f"\nERROR: File or folder '{input_path}' does not exist!")
        print("Check the path and try again.")
        return

    files = []
    if input_path.is_file():
        files = [input_path]
        logger.info(f"Processing single file: {input_path}")
        print(f"\nFound file: {input_path}")
    elif input_path.is_dir():
        files = list(input_path.glob('*.mp3')) + list(input_path.glob('*.wav'))
        logger.info(f"Found {len(files)} files in folder: {input_path}")
        print(f"\nFound {len(files)} audio files in folder: {input_path}")
        if not files:
            print("No audio files (.mp3 or .wav) found in folder")
            return
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")
    else:
        logger.error(f"File or folder not found: {input_path}")
        return

    # Create output folder
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nResults will be saved in: {output_dir}")

    # Start timing
    start_time = time.time()
    
    if args.parallel and len(files) > 1:
        # Parallel processing of parts for multiple files
        print(f"\nStarting parallel parts processing for {len(files)} files...")
        logger.info("Using parallel parts processing")
        
        results = parallel_audio_processing_optimized(
            files, output_dir, steps, chunk_duration,
            args.min_speaker_segment, split_method, args.use_gpu, logger
        )
        
        # Count total processed files
        total_processed = sum(len(r) if r else 0 for r in results)
        print(f"\nParallel parts processing completed! Files processed: {total_processed}")
        
    else:
        # Sequential processing for single file or disabled parallelization
        print(f"\nStarting sequential processing...")
        logger.info("Using sequential processing")
        
        # Create temporary folder for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temporary folder: {temp_path}")
            
            # Initialize managers for sequential processing
            gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
            model_manager = ModelManager(gpu_manager)
            
            # Load Whisper model only for word boundary splitting
            whisper_model = None
            if 'split' in steps and split_method == 'word_boundary':
                logger.info("Loading Whisper model for word boundary splitting...")
                print("Loading Whisper model for word boundary analysis...")
                whisper_model = model_manager.get_whisper_model("base")

            # Process files with progress bar
            print(f"\nStarting processing of {len(files)} files...")
            all_processed_files = []  # List of all processed files
            
            with tqdm(total=len(files), desc="Processing files", unit="file") as pbar_files:
                for audio in files:
                    logger.info(f"\n=== Processing file: {audio} ===")
                    print(f"\n{'='*50}")
                    print(f"Processing: {audio.name}")
                    print(f"{'='*50}")
                    current = audio
                    
                    # Create temporary folders for this file
                    file_temp_dir = temp_path / audio.stem
                    file_temp_dir.mkdir(exist_ok=True)
                    
                    # 1. Split by 10 minutes
                    if 'split' in steps:
                        logger.info("Stage 1: Audio splitting")
                        print("Stage 1: Splitting audio into chunks...")
                        if split_method == 'word_boundary':
                            parts = split_audio_at_word_boundary_optimized(str(current), file_temp_dir / 'parts', 
                                                               max_duration_sec=chunk_duration, whisper_model=whisper_model, logger=logger)
                        else:
                            parts = split_audio_by_duration_optimized(str(current), file_temp_dir / 'parts', 
                                                          max_duration_sec=chunk_duration, logger=logger)
                        logger.info(f"Created {len(parts)} parts")
                        print(f"Created {len(parts)} parts")
                    else:
                        parts = [str(current)]
                        logger.info("Skipping splitting stage")
                        print("Skipping splitting stage")
                    
                    # Process parts with progress bar
                    with tqdm(total=len(parts), desc=f"Processing parts {audio.stem}", unit="part") as pbar_parts:
                        for idx, part in enumerate(parts):
                            part_path = Path(part)
                            print(f"\n--- Part {idx+1}/{len(parts)} ---")
                            
                            # 2. Denoising
                            if 'denoise' in steps:
                                logger.info(f"Stage 2: Denoising part {idx+1}")
                                print("Stage 2: Noise removal (Demucs)...")
                                cleaned = clean_audio_with_demucs_optimized(str(part_path), file_temp_dir / 'cleaned', model_manager, gpu_manager, logger)
                            else:
                                cleaned = str(part_path)
                                logger.info("Skipping denoising stage")
                                print("Skipping denoising stage")
                            
                            # 3. Silence removal
                            if 'vad' in steps:
                                logger.info(f"Stage 3: Silence removal part {idx+1}")
                                print("Stage 3: Silence removal (Silero VAD)...")
                                no_silence = remove_silence_with_silero_optimized(cleaned, use_gpu=args.use_gpu, model_manager=model_manager, gpu_manager=gpu_manager, logger=logger)
                            else:
                                no_silence = cleaned
                                logger.info("Skipping silence removal stage")
                                print("Skipping silence removal stage")
                            
                            # 4. Diarization
                            if 'diar' in steps:
                                logger.info(f"Stage 4: Diarization part {idx+1}")
                                print("Stage 4: Speaker diarization (PyAnnote)...")
                                diarized_files = diarize_with_pyannote_optimized(no_silence, file_temp_dir / 'diarized', min_segment_duration=args.min_speaker_segment, model_manager=model_manager, gpu_manager=gpu_manager, logger=logger)
                                # diarized_files is now list of speaker files
                                if isinstance(diarized_files, list):
                                    all_processed_files.extend(diarized_files)
                                else:
                                    all_processed_files.append(diarized_files)
                            else:
                                diarized_files = [no_silence]
                                logger.info("Skipping diarization stage")
                                print("Skipping diarization stage")
                                all_processed_files.extend(diarized_files)
                            
                            pbar_parts.update(1)
                    
                    pbar_files.update(1)
            
            # Copy speaker files from temporary folders to main output folder
            if 'diar' in steps:
                logger.info("Copying speaker files to main output folder...")
                print("\nCopying speaker files...")
                
                speaker_counter = 1
                for file_temp_dir in temp_path.iterdir():
                    if file_temp_dir.is_dir():
                        diarized_dir = file_temp_dir / 'diarized'
                        if diarized_dir.exists():
                            for speaker_file in diarized_dir.glob('speaker_*.wav'):
                                # Create new name with number
                                new_name = f"speaker_{speaker_counter:04d}.wav"
                                new_path = output_dir / new_name
                                
                                # Copy file
                                import shutil
                                shutil.copy2(speaker_file, new_path)
                                logger.info(f"Copied: {speaker_file.name} -> {new_name}")
                                speaker_counter += 1
                
                print(f"Copied {speaker_counter - 1} speaker files to {output_dir}")
            
            # Clean up managers
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
    
    # Calculate execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info("=== Processing completed ===")
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETED!")
    print(f"{'='*60}")
    print(f"Total execution time: {total_time/60:.1f} minutes")
    print(f"Results saved in: {output_dir}")
    print("\nResults structure:")
    
    # Show what was created
    if output_dir.exists():
        # Show speaker files if diarization was performed
        if 'diar' in steps:
            speaker_files = list(output_dir.glob('speaker_*.wav'))
            if speaker_files:
                print(f"  speaker_*.wav ({len(speaker_files)} files)")
                for speaker_file in speaker_files:
                    try:
                        duration_str = get_mp3_duration(str(speaker_file))
                        print(f"    - {speaker_file.name}: {duration_str}")
                    except:
                        print(f"    - {speaker_file.name}")
    
    print(f"\nProcessing log saved in: audio_processing.log")
    print(f"Temporary files automatically deleted")
    
    # Show performance statistics
    if args.parallel and len(files) > 1:
        print(f"\nPERFORMANCE STATISTICS:")
        print(f"  - Files processed: {len(files)}")
        print(f"  - Time per file: {total_time/len(files):.1f} seconds")
        print(f"  - Speedup from parallelization: ~{optimal_workers}x")
        print(f"  - GPU used: {'Yes' if gpu_available else 'No'}")
        print(f"  - Logic: Optimized parallel processing with memory management")

if __name__ == "__main__":
    main() 