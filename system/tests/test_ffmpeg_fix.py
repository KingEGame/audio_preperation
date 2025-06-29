#!/usr/bin/env python3
"""
Test script for FFmpeg fix in speaker segment creation
Tests the improved create_speaker_segments_with_metadata function
"""

import os
import sys
import logging
import tempfile
from pathlib import Path

# Добавляем путь к модулю audio
audio_module_path = Path(__file__).parent.parent / 'scripts' / 'audio'
sys.path.append(str(audio_module_path))

from stages import create_speaker_segments_with_metadata

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_ffmpeg_fix.log')
        ]
    )
    return logging.getLogger(__name__)

def create_test_audio_file(output_path, duration=30):
    """Создание тестового аудиофайла"""
    try:
        command = [
            "ffmpeg", "-f", "lavfi", "-i", f"anoisesrc=d={duration}:c=pink[out]",
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            str(output_path), "-y"
        ]
        
        import subprocess
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and output_path.exists():
            print(f"✓ Created test audio file: {output_path}")
            return True
        else:
            print(f"✗ Failed to create test audio file: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating test audio file: {e}")
        return False

def create_mock_diarization_result(audio_path, num_speakers=2):
    """Создание мок-результата диаризации"""
    from pyannote.core import Segment, Annotation
    
    annotation = Annotation()
    
    # Создаем сегменты для каждого спикера
    segment_duration = 5.0  # 5 секунд на сегмент
    current_time = 0.0
    
    for speaker_id in range(num_speakers):
        speaker_name = f"SPEAKER_{speaker_id:02d}"
        
        # Создаем несколько сегментов для каждого спикера
        for i in range(3):
            start_time = current_time + i * segment_duration
            end_time = start_time + segment_duration
            
            if end_time <= 30:  # Ограничиваем длительностью файла
                segment = Segment(start_time, end_time)
                annotation[segment] = speaker_name
        
        current_time += 15  # Смещаем время для следующего спикера
    
    return annotation

def test_speaker_segment_creation():
    """Тест создания сегментов спикеров"""
    logger = setup_logging()
    
    print("="*60)
    print("TESTING FFMPEG FIX FOR SPEAKER SEGMENT CREATION")
    print("="*60)
    
    # Создаем временную папку
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем тестовый аудиофайл
        test_audio = temp_path / "test_audio.wav"
        if not create_test_audio_file(test_audio):
            print("✗ Cannot proceed without test audio file")
            return False
        
        # Создаем мок-результат диаризации
        diarization_result = create_mock_diarization_result(test_audio)
        
        # Создаем выходную папку
        output_dir = temp_path / "speaker_output"
        output_dir.mkdir(exist_ok=True)
        
        print(f"\nTesting speaker segment creation...")
        print(f"Input audio: {test_audio}")
        print(f"Output directory: {output_dir}")
        print(f"Number of speakers: {len(set(diarization_result.labels()))}")
        
        # Тестируем создание сегментов
        try:
            speaker_files = create_speaker_segments_with_metadata(
                input_audio=str(test_audio),
                diarization_result=diarization_result,
                output_dir=str(output_dir),
                min_segment_duration=0.1,
                chunk_info={'chunk_number': 1, 'start_time': 0, 'end_time': 30},
                logger=logger
            )
            
            print(f"\n✓ Speaker segment creation completed!")
            print(f"Created {len(speaker_files)} speaker files")
            
            # Проверяем созданные файлы
            for speaker_file in speaker_files:
                speaker_path = Path(speaker_file)
                if speaker_path.exists():
                    try:
                        from utils import get_mp3_duration
                        duration_str = get_mp3_duration(str(speaker_path))
                        print(f"  ✓ {speaker_path.name}: {duration_str}")
                    except:
                        print(f"  ✓ {speaker_path.name}: exists")
                else:
                    print(f"  ✗ {speaker_path.name}: missing")
            
            # Проверяем структуру папок
            speaker_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('speaker_')]
            print(f"\nSpeaker directories created: {len(speaker_dirs)}")
            
            for speaker_dir in speaker_dirs:
                audio_files = list(speaker_dir.glob("*.wav"))
                metadata_files = list(speaker_dir.glob("metadata_*.txt"))
                print(f"  {speaker_dir.name}: {len(audio_files)} audio, {len(metadata_files)} metadata")
            
            return len(speaker_files) > 0
            
        except Exception as e:
            print(f"✗ Error during speaker segment creation: {e}")
            logger.error(f"Test failed: {e}")
            return False

def main():
    """Основная функция тестирования"""
    print("FFmpeg Fix Test for Speaker Segment Creation")
    print("="*50)
    
    # Проверяем наличие FFmpeg
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
        else:
            print("✗ FFmpeg not found or not working")
            return False
    except Exception as e:
        print(f"✗ Error checking FFmpeg: {e}")
        return False
    
    # Запускаем тест
    success = test_speaker_segment_creation()
    
    if success:
        print("\n" + "="*60)
        print("✓ FFMPEG FIX TEST PASSED!")
        print("✓ Speaker segment creation is working correctly")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ FFMPEG FIX TEST FAILED!")
        print("✗ Speaker segment creation has issues")
        print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 