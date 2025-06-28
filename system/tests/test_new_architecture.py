#!/usr/bin/env python3
"""
Тестовый скрипт для новой архитектуры аудио обработки
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулю audio
audio_module_path = Path(__file__).parent / 'audio'
sys.path.append(str(audio_module_path))

def test_new_architecture():
    """Тестирование новой архитектуры"""
    print("=== Тестирование новой архитектуры аудио обработки ===")
    
    try:
        # Импортируем новые функции
        from audio import (
            process_multiple_files_parallel_optimized,
            process_file_multithreaded_optimized,
            GPUMemoryManager, ModelManager,
            setup_logging, setup_gpu_optimization
        )
        print("✓ Импорт новых функций успешен")
        
        # Тестируем настройку GPU
        gpu_available = setup_gpu_optimization()
        print(f"✓ GPU настройка: {'Доступна' if gpu_available else 'Недоступна'}")
        
        # Тестируем логирование
        logger = setup_logging()
        print("✓ Логирование настроено")
        
        # Тестируем менеджеры
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        print("✓ Менеджеры инициализированы")
        
        # Очистка
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        print("✓ Менеджеры очищены")
        
        print("\n=== Все тесты пройдены успешно! ===")
        print("Новая архитектура готова к использованию.")
        
        return True
        
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        return False

def show_architecture_info():
    """Показывает информацию о новой архитектуре"""
    print("\n=== Информация о новой архитектуре ===")
    print("1. Многопоточная обработка (4 потока на файл)")
    print("2. Блокировка диаризации (только один поток)")
    print("3. Организация по спикерам в папках")
    print("4. Метаданные с временными метками")
    print("5. Автоматическая очистка временных файлов")
    
    print("\nСтруктура выходных файлов:")
    print("output/")
    print("├── speaker_0001/")
    print("│   ├── chunk_0001_part1.wav")
    print("│   ├── metadata_0001_part1.txt")
    print("│   └── speaker_0001_info.txt")
    print("├── speaker_0002/")
    print("│   └── ...")
    print("└── ...")

def main():
    """Основная функция"""
    print("Тестирование новой архитектуры аудио обработки")
    print("=" * 60)
    
    # Показываем информацию
    show_architecture_info()
    
    # Запускаем тесты
    success = test_new_architecture()
    
    if success:
        print("\nДля использования новой архитектуры:")
        print("python audio_processing.py --input audio.mp3 --output results")
        print("\nПараметры:")
        print("  --parallel: включить параллельную обработку")
        print("  --steps split denoise vad diar: все этапы")
        print("  --chunk_duration 600: 10 минут на чанк")
        print("  --min_speaker_segment 1.5: минимальная длительность сегмента")
    else:
        print("\nОшибка в тестировании. Проверьте установку зависимостей.")

if __name__ == "__main__":
    main() 