#!/usr/bin/env python3
"""
Простой тест импортов для функции разделения на роли
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

def test_imports():
    """Тестирует импорты"""
    
    print("=" * 60)
    print("ТЕСТ ИМПОРТОВ ДЛЯ РАЗДЕЛЕНИЯ НА РОЛИ")
    print("=" * 60)
    
    try:
        print("1. Тестируем импорт config...")
        from config import get_token, token_exists
        print("✓ config импортирован успешно")
        
        print("2. Тестируем функции токена...")
        if token_exists():
            token = get_token()
            print(f"✓ Токен найден: {token[:10]}..." if token else "✓ Токен пустой")
        else:
            print("⚠ Токен не найден")
        
        print("3. Тестируем импорт managers...")
        from audio.managers import GPUMemoryManager, ModelManager
        print("✓ managers импортирован успешно")
        
        print("4. Тестируем импорт stages...")
        from audio.stages import diarize_with_role_classification
        print("✓ stages импортирован успешно")
        
        print("5. Тестируем инициализацию менеджеров...")
        gpu_manager = GPUMemoryManager()
        model_manager = ModelManager(gpu_manager)
        print("✓ Менеджеры инициализированы успешно")
        
        # Очистка
        model_manager.cleanup_models()
        gpu_manager.cleanup(force=True)
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ИМПОРТЫ РАБОТАЮТ КОРРЕКТНО!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    
    if not success:
        print("\nДля исправления проблем:")
        print("1. Убедитесь, что все зависимости установлены")
        print("2. Проверьте, что токен диаризации настроен")
        print("3. Запустите: setup_diarization.bat") 