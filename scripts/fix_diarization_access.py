#!/usr/bin/env python3
"""
Скрипт для исправления проблем доступа к моделям PyAnnote
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def open_model_pages():
    """Открывает страницы моделей в браузере для принятия условий"""
    models = [
        "https://huggingface.co/pyannote/speaker-diarization-3.1",
        "https://huggingface.co/pyannote/segmentation-3.0", 
        "https://huggingface.co/pyannote/embedding-3.0"
    ]
    
    print("Открываю страницы моделей в браузере...")
    print("Для каждой модели:")
    print("1. Нажмите 'Accept' для принятия условий использования")
    print("2. Подождите подтверждения")
    print("3. Переходите к следующей модели")
    print()
    
    for i, model_url in enumerate(models, 1):
        print(f"{i}. Открываю: {model_url}")
        webbrowser.open(model_url)
        if i < len(models):
            input("Нажмите Enter после принятия условий для этой модели...")
    
    print("\nВсе страницы открыты. Примите условия для всех моделей.")

def update_token():
    """Обновляет токен HuggingFace"""
    print("\n" + "="*60)
    print("ОБНОВЛЕНИЕ TOKEN HUGGINGFACE")
    print("="*60)
    print()
    print("Если у вас новый токен или нужно обновить существующий:")
    print()
    print("1. Перейдите на https://huggingface.co/settings/tokens")
    print("2. Создайте новый токен с правами 'Read'")
    print("3. Скопируйте токен")
    print()
    
    new_token = input("Введите новый токен (или нажмите Enter для пропуска): ").strip()
    
    if new_token:
        # Сохраняем новый токен
        token_file = "hf_token.txt"
        with open(token_file, "w") as f:
            f.write(new_token)
        
        print(f"✓ Новый токен сохранен в {token_file}")
        return True
    else:
        print("Токен не изменен.")
        return False

def test_after_fix():
    """Тестирует доступ после исправления"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ПОСЛЕ ИСПРАВЛЕНИЯ")
    print("="*60)
    print()
    print("Подождите 2-3 минуты после принятия условий, затем:")
    print("1. Запустите: test_diarization_token.bat")
    print("2. Или запустите аудио-процессинг снова")
    print()

def main():
    print("ИСПРАВЛЕНИЕ ДОСТУПА К PYANNOTE")
    print("="*50)
    print()
    print("Эта программа поможет исправить проблемы с доступом к моделям PyAnnote.")
    print()
    
    # Проверяем наличие токена
    token_file = Path("hf_token.txt")
    if not token_file.exists():
        print("✗ Файл hf_token.txt не найден")
        print("Сначала запустите setup_diarization.py для создания токена")
        return
    
    with open(token_file, "r") as f:
        token = f.read().strip()
    
    if not token:
        print("✗ Токен пустой в файле hf_token.txt")
        print("Сначала запустите setup_diarization.py для создания токена")
        return
    
    print(f"✓ Токен найден: {token[:10]}...")
    print()
    
    # Показываем меню
    print("Выберите действие:")
    print("1. Открыть страницы моделей для принятия условий")
    print("2. Обновить токен HuggingFace")
    print("3. Показать инструкции по исправлению")
    print("4. Выход")
    print()
    
    choice = input("Введите номер (1-4): ").strip()
    
    if choice == "1":
        open_model_pages()
    elif choice == "2":
        update_token()
    elif choice == "3":
        show_instructions()
    elif choice == "4":
        print("Выход.")
        return
    else:
        print("Неверный выбор.")
        return
    
    test_after_fix()

def show_instructions():
    """Показывает подробные инструкции"""
    print("\n" + "="*60)
    print("ПОДРОБНЫЕ ИНСТРУКЦИИ ПО ИСПРАВЛЕНИЮ")
    print("="*60)
    print()
    print("ПРОБЛЕМА: 'Could not download model' или 'private or gated'")
    print()
    print("РЕШЕНИЕ:")
    print()
    print("1. ПРИНЯТИЕ УСЛОВИЙ ИСПОЛЬЗОВАНИЯ:")
    print("   - Перейдите на https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   - Нажмите кнопку 'Accept' для принятия условий")
    print("   - Повторите для других моделей:")
    print("     * https://huggingface.co/pyannote/segmentation-3.0")
    print("     * https://huggingface.co/pyannote/embedding-3.0")
    print()
    print("2. ПРОВЕРКА TOKEN:")
    print("   - Перейдите на https://huggingface.co/settings/tokens")
    print("   - Убедитесь, что токен имеет права 'Read'")
    print("   - При необходимости создайте новый токен")
    print()
    print("3. ТЕСТИРОВАНИЕ:")
    print("   - Запустите: test_diarization_token.bat")
    print("   - Или запустите аудио-процессинг снова")
    print()
    print("4. ВРЕМЯ ОЖИДАНИЯ:")
    print("   - После принятия условий подождите 2-3 минуты")
    print("   - Изменения могут применяться не мгновенно")
    print()

if __name__ == "__main__":
    main() 