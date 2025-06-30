#!/usr/bin/env python3
"""
Тестовый скрипт для проверки разных режимов деноизинга Demucs
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулю audio
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

def test_demucs_modes():
    """
    Тестирует разные режимы деноизинга Demucs
    """
    print("=" * 60)
    print("ТЕСТ РЕЖИМОВ ДЕНОИЗИНГА DEMUCS")
    print("=" * 60)
    
    try:
        from audio.stages import clean_audio_with_demucs_optimized
        from audio.managers import GPUMemoryManager, ModelManager
        from audio.config import GPU_MEMORY_LIMIT
        import logging
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        print("✓ Модули импортированы успешно")
        
        # Проверяем наличие тестового аудио файла
        test_audio = input("\nВведите путь к тестовому аудио файлу: ").strip().strip('"')
        
        if not os.path.exists(test_audio):
            print(f"✗ Файл не найден: {test_audio}")
            return False
        
        print(f"✓ Тестовый файл найден: {test_audio}")
        
        # Создаем менеджеры
        gpu_manager = GPUMemoryManager(GPU_MEMORY_LIMIT)
        model_manager = ModelManager(gpu_manager)
        
        # Создаем временную папку для результатов
        temp_dir = Path("test_demucs_results")
        temp_dir.mkdir(exist_ok=True)
        
        # Тестируем разные режимы
        modes = [
            ('vocals', 'Только вокалы'),
            ('no_vocals', 'Без вокалов'),
            ('all', 'Все источники'),
            ('enhanced', 'Улучшенное аудио')
        ]
        
        results = {}
        
        for mode, description in modes:
            print(f"\n--- Тестирование режима: {mode} ({description}) ---")
            
            try:
                result_file = clean_audio_with_demucs_optimized(
                    test_audio, temp_dir, model_manager, gpu_manager, logger, mode=mode
                )
                
                if result_file and os.path.exists(result_file):
                    # Проверяем размер файла
                    file_size = os.path.getsize(result_file)
                    print(f"✓ Режим {mode}: файл создан ({file_size} байт)")
                    results[mode] = result_file
                else:
                    print(f"✗ Режим {mode}: файл не создан")
                    results[mode] = None
                    
            except Exception as e:
                print(f"✗ Режим {mode}: ошибка - {e}")
                results[mode] = None
        
        # Показываем результаты
        print(f"\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        for mode, description in modes:
            if results[mode]:
                print(f"✓ {mode}: {description} - УСПЕШНО")
                print(f"  Файл: {results[mode]}")
            else:
                print(f"✗ {mode}: {description} - ОШИБКА")
        
        # Рекомендации
        print(f"\n" + "=" * 60)
        print("РЕКОМЕНДАЦИИ")
        print("=" * 60)
        
        if results.get('enhanced'):
            print("✓ Рекомендуется использовать режим 'enhanced' для лучшего качества")
            print("  Этот режим сохраняет вокалы и немного фоновых звуков")
        elif results.get('vocals'):
            print("✓ Можно использовать режим 'vocals' для извлечения только голоса")
        elif results.get('all'):
            print("✓ Можно использовать режим 'all' для сохранения всех звуков")
        
        print(f"\nРезультаты сохранены в папке: {temp_dir}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return False

def main():
    print("Этот скрипт тестирует разные режимы деноизинга Demucs")
    print("для решения проблемы с пустым аудио после обработки.")
    print()
    
    success = test_demucs_modes()
    
    if success:
        print(f"\n✓ Тестирование завершено успешно!")
        print("Проверьте созданные файлы и выберите лучший режим.")
    else:
        print(f"\n✗ Тестирование завершено с ошибками")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 