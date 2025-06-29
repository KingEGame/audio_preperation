#!/usr/bin/env python3
"""
Test script for temporary directory fix
Verifies that temp_analysis folders are created in the correct temp directory
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Добавляем путь к модулю audio
audio_module_path = Path(__file__).parent.parent / 'scripts' / 'audio'
sys.path.append(str(audio_module_path))

from splitters import split_audio_smart_multithreaded_optimized, split_audio_at_word_boundary_optimized

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_temp_dir_fix.log')
        ]
    )
    return logging.getLogger(__name__)

def create_test_audio_file(output_path, duration=60):
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

def check_temp_directories(source_dir, temp_dir, logger):
    """Проверяет, что временные папки создаются в правильном месте"""
    source_path = Path(source_dir)
    temp_path = Path(temp_dir)
    
    print(f"\nChecking temporary directories...")
    print(f"Source directory: {source_path}")
    print(f"Temp directory: {temp_path}")
    
    # Проверяем, что в исходной папке НЕТ временных папок
    source_temp_dirs = list(source_path.glob("temp_analysis*"))
    if source_temp_dirs:
        print(f"✗ Found temporary directories in source folder:")
        for temp_dir in source_temp_dirs:
            print(f"  - {temp_dir}")
        return False
    else:
        print(f"✓ No temporary directories in source folder")
    
    # Проверяем, что в temp папке есть временные папки (если они должны быть)
    temp_analysis_dirs = list(temp_path.glob("temp_analysis*"))
    if temp_analysis_dirs:
        print(f"✓ Found temporary directories in temp folder:")
        for temp_dir in temp_analysis_dirs:
            print(f"  - {temp_dir}")
    else:
        print(f"ℹ No temporary directories found in temp folder (this is normal)")
    
    return True

def test_smart_multithreaded_splitting():
    """Тест умной многопоточной разбивки"""
    logger = setup_logging()
    
    print("="*60)
    print("TESTING SMART MULTITHREADED SPLITTING")
    print("="*60)
    
    # Создаем временную папку
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем папку для исходного файла
        source_dir = temp_path / "source"
        source_dir.mkdir(exist_ok=True)
        
        # Создаем тестовый аудиофайл
        test_audio = source_dir / "test_audio.wav"
        if not create_test_audio_file(test_audio, duration=120):  # 2 минуты для тестирования
            print("✗ Cannot proceed without test audio file")
            return False
        
        # Создаем папку для временных файлов
        processing_temp_dir = temp_path / "processing_temp"
        processing_temp_dir.mkdir(exist_ok=True)
        
        print(f"\nTesting smart multithreaded splitting...")
        print(f"Input audio: {test_audio}")
        print(f"Processing temp dir: {processing_temp_dir}")
        
        # Тестируем разбивку
        try:
            parts = split_audio_smart_multithreaded_optimized(
                input_audio=str(test_audio),
                temp_dir=str(processing_temp_dir),
                max_duration_sec=30,  # 30 секунд для создания нескольких частей
                whisper_model=None,  # Будет загружена автоматически
                logger=logger
            )
            
            print(f"\n✓ Smart splitting completed!")
            print(f"Created {len(parts)} parts")
            
            # Проверяем временные папки
            temp_ok = check_temp_directories(source_dir, processing_temp_dir, logger)
            
            # Проверяем созданные части
            for part in parts:
                part_path = Path(part)
                if part_path.exists():
                    print(f"  ✓ {part_path.name}: exists")
                else:
                    print(f"  ✗ {part_path.name}: missing")
            
            return len(parts) > 0 and temp_ok
            
        except Exception as e:
            print(f"✗ Error during smart splitting: {e}")
            logger.error(f"Test failed: {e}")
            return False

def test_word_boundary_splitting():
    """Тест разбивки по границам слов"""
    logger = setup_logging()
    
    print("="*60)
    print("TESTING WORD BOUNDARY SPLITTING")
    print("="*60)
    
    # Создаем временную папку
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем папку для исходного файла
        source_dir = temp_path / "source"
        source_dir.mkdir(exist_ok=True)
        
        # Создаем тестовый аудиофайл
        test_audio = source_dir / "test_audio.wav"
        if not create_test_audio_file(test_audio, duration=90):  # 1.5 минуты для тестирования
            print("✗ Cannot proceed without test audio file")
            return False
        
        # Создаем папку для временных файлов
        processing_temp_dir = temp_path / "processing_temp"
        processing_temp_dir.mkdir(exist_ok=True)
        
        print(f"\nTesting word boundary splitting...")
        print(f"Input audio: {test_audio}")
        print(f"Processing temp dir: {processing_temp_dir}")
        
        # Тестируем разбивку
        try:
            parts = split_audio_at_word_boundary_optimized(
                input_audio=str(test_audio),
                temp_dir=str(processing_temp_dir),
                max_duration_sec=30,  # 30 секунд для создания нескольких частей
                whisper_model=None,  # Будет загружена автоматически
                logger=logger
            )
            
            print(f"\n✓ Word boundary splitting completed!")
            print(f"Created {len(parts)} parts")
            
            # Проверяем временные папки
            temp_ok = check_temp_directories(source_dir, processing_temp_dir, logger)
            
            # Проверяем созданные части
            for part in parts:
                part_path = Path(part)
                if part_path.exists():
                    print(f"  ✓ {part_path.name}: exists")
                else:
                    print(f"  ✗ {part_path.name}: missing")
            
            return len(parts) > 0 and temp_ok
            
        except Exception as e:
            print(f"✗ Error during word boundary splitting: {e}")
            logger.error(f"Test failed: {e}")
            return False

def main():
    """Основная функция тестирования"""
    print("Temporary Directory Fix Test")
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
    
    # Запускаем тесты
    success1 = test_smart_multithreaded_splitting()
    print("\n" + "="*60)
    success2 = test_word_boundary_splitting()
    
    overall_success = success1 and success2
    
    if overall_success:
        print("\n" + "="*60)
        print("✓ TEMPORARY DIRECTORY FIX TEST PASSED!")
        print("✓ Temporary directories are created in the correct location")
        print("✓ No temp files are left in source directories")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ TEMPORARY DIRECTORY FIX TEST FAILED!")
        print("✗ Temporary directories are created in wrong locations")
        print("="*60)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 