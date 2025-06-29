#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы нового модуля audio
"""

import sys
from pathlib import Path

# Добавляем путь к модулю audio
sys.path.append(str(Path(__file__).parent / 'audio'))

def test_imports():
    """Тестирует импорт всех функций из модуля audio"""
    try:
        from audio import (
            GPUMemoryManager, ModelManager,
            clean_audio_with_demucs_optimized, 
            diarize_with_pyannote_optimized,
            split_audio_by_duration_optimized, split_audio_at_word_boundary_optimized,
            get_mp3_duration, setup_logging,
            process_audio_file_optimized, parallel_audio_processing_optimized,
            get_optimal_workers, setup_gpu_optimization, 
            MAX_WORKERS, GPU_MEMORY_LIMIT, BATCH_SIZE
        )
        print("✓ Все импорты успешны!")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False

def test_gpu_setup():
    """Тестирует настройку GPU"""
    try:
        from audio import setup_gpu_optimization, get_optimal_workers
        gpu_available = setup_gpu_optimization()
        workers = get_optimal_workers()
        print(f"✓ GPU настройка: {'доступна' if gpu_available else 'недоступна'}")
        print(f"✓ Оптимальное количество процессов: {workers}")
        return True
    except Exception as e:
        print(f"✗ Ошибка настройки GPU: {e}")
        return False

def test_logging():
    """Тестирует настройку логирования"""
    try:
        from audio import setup_logging
        logger = setup_logging()
        logger.info("Тестовое сообщение")
        print("✓ Логирование работает!")
        return True
    except Exception as e:
        print(f"✗ Ошибка логирования: {e}")
        return False

def main():
    print("Тестирование модуля audio...")
    print("=" * 50)
    
    tests = [
        ("Импорты", test_imports),
        ("Настройка GPU", test_gpu_setup),
        ("Логирование", test_logging),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nТест: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"Тест {test_name} провален!")
    
    print("\n" + "=" * 50)
    print(f"Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✓ Все тесты пройдены! Модуль audio готов к использованию.")
        return True
    else:
        print("✗ Некоторые тесты провалены. Проверьте настройки.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 