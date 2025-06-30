#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех импортов
"""

import sys
from pathlib import Path

# Добавляем путь к модулю audio
audio_module_path = Path(__file__).parent / 'audio'
sys.path.append(str(audio_module_path))

def test_imports():
    """Тестирует все импорты из модуля audio"""
    
    print("Testing imports from audio module...")
    
    try:
        # Тестируем импорт менеджеров
        print("1. Testing managers...")
        from audio import GPUMemoryManager, ModelManager
        print("   ✓ GPUMemoryManager, ModelManager imported successfully")
        
        # Тестируем импорт процессоров
        print("2. Testing processors...")
        from audio import (
            process_audio_file_optimized,
            process_multiple_files_parallel_optimized,
            process_file_multithreaded_optimized
        )
        print("   ✓ All processor functions imported successfully")
        
        # Тестируем импорт этапов
        print("3. Testing stages...")
        from audio import (
            clean_audio_with_demucs_optimized,
            diarize_with_pyannote_optimized
        )
        print("   ✓ All stage functions imported successfully")
        
        # Тестируем импорт сплиттеров
        print("4. Testing splitters...")
        from audio import (
            split_audio_by_duration_optimized,
            split_audio_at_word_boundary_optimized,
            split_audio_smart_multithreaded_optimized
        )
        print("   ✓ All splitter functions imported successfully")
        
        # Тестируем импорт утилит
        print("5. Testing utils...")
        from audio import (
            get_mp3_duration,
            setup_logging,
            copy_results_to_output_optimized,
            parallel_audio_processing_optimized
        )
        print("   ✓ All utility functions imported successfully")
        
        # Тестируем импорт конфигурации
        print("6. Testing config...")
        from audio import (
            get_optimal_workers,
            setup_gpu_optimization,
            MAX_WORKERS,
            GPU_MEMORY_LIMIT,
            BATCH_SIZE
        )
        print("   ✓ All config functions and constants imported successfully")
        
        print("\n🎉 ALL IMPORTS SUCCESSFUL! 🎉")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config_imports():
    """Тестирует импорты из config.py"""
    
    print("\nTesting imports from config.py...")
    
    try:
        from config import get_token, token_exists, ensure_directories
        print("   ✓ All config functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT TESTING")
    print("=" * 60)
    
    audio_success = test_imports()
    config_success = test_config_imports()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if audio_success and config_success:
        print("✅ ALL TESTS PASSED - All imports are working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
    
    print("=" * 60) 