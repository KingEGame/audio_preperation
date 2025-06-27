#!/usr/bin/env python3
"""
Скрипт настройки диаризации с PyAnnote
"""

import subprocess
import sys
import os

def install_pyannote():
    """Устанавливает PyAnnote и зависимости с правильными версиями"""
    print("Установка PyAnnote и зависимостей...")
    
    # Сначала исправляем NumPy до совместимой версии
    print("Исправление версии NumPy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.25.2", "--force-reinstall"])
        print("✓ NumPy исправлен")
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка исправления NumPy: {e}")
        return False
    
    packages = [
        "torch>=1.12.0",
        "torchaudio>=0.12.0", 
        "librosa",
        "soundfile",
        "pyannote.audio"
    ]
    
    for package in packages:
        print(f"Установка {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} установлен")
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка установки {package}: {e}")
            return False
    
    return True

def get_hf_token():
    """Помогает получить токен HuggingFace"""
    print("\n" + "="*60)
    print("НАСТРОЙКА TOKEN ДЛЯ PYANNOTE")
    print("="*60)
    print()
    print("Для использования диаризации PyAnnote нужен токен HuggingFace:")
    print()
    print("1. Перейдите на https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("2. Нажмите 'Accept' для принятия условий использования")
    print("3. Перейдите в Settings -> Access Tokens")
    print("4. Создайте новый токен с правами 'Read'")
    print("5. Скопируйте токен")
    print()
    
    token = input("Введите ваш HuggingFace токен: ").strip()
    
    if not token:
        print("Токен не введен. Диаризация будет пропущена.")
        return None
    
    # Сохраняем токен в файл
    token_file = "hf_token.txt"
    with open(token_file, "w") as f:
        f.write(token)
    
    print(f"✓ Токен сохранен в {token_file}")
    return token

def test_pyannote():
    """Тестирует установку PyAnnote"""
    print("\nТестирование PyAnnote...")
    
    try:
        # Проверяем NumPy
        import numpy
        print(f"✓ NumPy: {numpy.__version__}")
        
        # Проверяем numba
        import numba
        print("✓ numba работает")
        
        # Проверяем PyAnnote
        from pyannote.audio import Pipeline
        print("✓ PyAnnote импортирован успешно")
        
        # Проверяем токен
        token_file = "hf_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()
            
            if token:
                print("✓ Токен найден")
                return True
            else:
                print("✗ Токен пустой")
                return False
        else:
            print("✗ Файл с токеном не найден")
            return False
            
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        return False

def main():
    print("НАСТРОЙКА ДИАРИЗАЦИИ PYANNOTE")
    print("="*40)
    
    # Устанавливаем PyAnnote
    if not install_pyannote():
        print("Ошибка установки PyAnnote")
        return
    
    # Получаем токен
    token = get_hf_token()
    
    # Тестируем
    if test_pyannote():
        print("\n" + "="*60)
        print("✅ ДИАРИЗАЦИЯ ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("="*60)
        print()
        print("Теперь вы можете использовать этап 'diar' в аудио-процессинге:")
        print("start_audio_processing.bat --input audio.mp3 --output results --steps split denoise vad diar")
    else:
        print("\n" + "="*60)
        print("⚠️  ДИАРИЗАЦИЯ НЕ НАСТРОЕНА")
        print("="*60)
        print()
        print("Проверьте:")
        print("1. Установку PyAnnote")
        print("2. Наличие токена HuggingFace")
        print("3. Принятие условий использования модели")
        print()
        print("Если есть проблемы с NumPy, запустите:")
        print("fix_numpy_diarization.bat")

if __name__ == "__main__":
    main() 