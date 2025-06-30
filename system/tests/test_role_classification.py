#!/usr/bin/env python3
"""
Тест функции разделения на роли (нарратор + персонажи)
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

def test_role_classification():
    """Тестирует функцию разделения на роли"""
    
    print("=" * 60)
    print("ТЕСТ РАЗДЕЛЕНИЯ НА РОЛИ")
    print("=" * 60)
    
    try:
        # Импортируем функцию
        from audio.stages import diarize_with_role_classification
        from config import get_token, token_exists
        from audio.managers import GPUMemoryManager, ModelManager
        
        print("✓ Функция импортирована успешно")
        
        # Проверяем токен
        if not token_exists():
            print("❌ Токен диаризации не найден")
            print("Запустите: setup_diarization.bat")
            return False
        
        token = get_token()
        if not token:
            print("❌ Токен диаризации пустой")
            print("Запустите: setup_diarization.bat")
            return False
        
        print("✓ Токен диаризации найден")
        
        # Создаем тестовую структуру
        test_input = "test_audio.mp3"  # Замените на реальный файл
        test_output = "test_roles_output"
        
        if not os.path.exists(test_input):
            print(f"❌ Тестовый файл не найден: {test_input}")
            print("Поместите тестовый аудиофайл в папку tests/")
            return False
        
        print(f"✓ Тестовый файл найден: {test_input}")
        
        # Инициализируем менеджеры
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        
        print("✓ Менеджеры инициализированы")
        
        # Создаем выходную папку
        output_dir = Path(test_output)
        output_dir.mkdir(exist_ok=True)
        
        print(f"✓ Выходная папка создана: {output_dir}")
        
        # Запускаем тест
        print("\nЗапуск разделения на роли...")
        print("Это может занять несколько минут...")
        
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        result = diarize_with_role_classification(
            test_input, 
            test_output,
            min_segment_duration=0.3,
            model_manager=model_manager,
            gpu_manager=gpu_manager,
            logger=logger
        )
        
        if result and result != [test_input]:
            print("✓ Разделение на роли выполнено успешно!")
            print(f"Создано файлов: {len(result)}")
            
            # Показываем результаты
            print("\nРезультаты:")
            for file_path in result:
                print(f"  - {Path(file_path).name}")
            
            # Проверяем созданные файлы
            print(f"\nФайлы в папке {test_output}:")
            for file_path in output_dir.glob("*"):
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"  - {file_path.name} ({size_mb:.1f} MB)")
            
            return True
        else:
            print("❌ Разделение на роли не удалось")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Очистка
        try:
            model_manager.cleanup_models()
            gpu_manager.cleanup(force=True)
        except:
            pass

if __name__ == "__main__":
    success = test_role_classification()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("Функция разделения на роли работает корректно")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
        print("Проверьте ошибки выше")
    print("=" * 60) 