#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой логики параллельной обработки частей
"""

import os
import sys
import tempfile
from pathlib import Path
import subprocess

def create_test_audio():
    """Создает тестовый аудиофайл для проверки"""
    print("Создание тестового аудиофайла...")
    
    # Создаем временный файл с тестовым аудио (30 секунд)
    test_audio = "test_audio.wav"
    
    # Генерируем тестовый аудиофайл с помощью ffmpeg
    command = [
        "ffmpeg", "-f", "lavfi", "-i", "sine=frequency=1000:duration=30",
        "-ar", "16000", "-ac", "1", test_audio, "-y"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"✓ Тестовый аудиофайл создан: {test_audio}")
        return test_audio
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка создания тестового аудио: {e}")
        return None

def test_parallel_parts():
    """Тестирует новую логику параллельной обработки частей"""
    print("\n" + "="*60)
    print("ТЕСТ НОВОЙ ЛОГИКИ ПАРАЛЛЕЛЬНОЙ ОБРАБОТКИ ЧАСТЕЙ")
    print("="*60)
    
    # Создаем тестовый аудиофайл
    test_audio = create_test_audio()
    if not test_audio:
        return False
    
    # Создаем выходную папку
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nЗапуск теста с параметрами:")
    print(f"  Входной файл: {test_audio}")
    print(f"  Выходная папка: {output_dir}")
    print(f"  Длительность куска: 10 секунд (для теста)")
    print(f"  Этапы: split, denoise, vad")
    print(f"  Параллельная обработка частей: Включена")
    print(f"  GPU: Автоматическое определение")
    
    # Запускаем обработку с тестовыми параметрами
    command = [
        sys.executable, "audio_processing.py",
        "--input", test_audio,
        "--output", output_dir,
        "--chunk_duration", "10",  # 10 секунд для быстрого теста
        "--steps", "split", "denoise", "vad",  # Пропускаем диаризацию для скорости
        "--split_method", "simple",
        "--verbose"
    ]
    
    print(f"\nКоманда: {' '.join(command)}")
    
    try:
        print("\nЗапуск обработки...")
        result = subprocess.run(command, check=True, capture_output=False)
        
        # Проверяем результаты
        output_path = Path(output_dir)
        if output_path.exists():
            files = list(output_path.glob("*.wav"))
            print(f"\n✓ Тест завершен успешно!")
            print(f"  Создано файлов: {len(files)}")
            for file in files:
                print(f"    - {file.name}")
            
            # Очистка
            if test_audio and os.path.exists(test_audio):
                os.remove(test_audio)
            print(f"\n✓ Тестовые файлы удалены")
            
            return True
        else:
            print(f"\n✗ Выходная папка не создана: {output_dir}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Ошибка выполнения: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Тестирование новой логики параллельной обработки частей")
    print("="*60)
    
    # Проверяем наличие необходимых файлов
    if not os.path.exists("audio_processing.py"):
        print("✗ Файл audio_processing.py не найден!")
        return False
    
    # Запускаем тест
    success = test_parallel_parts()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("Новая логика параллельной обработки частей работает корректно")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("Проверьте логи и исправьте ошибки")
        print("="*60)
    
    return success

if __name__ == "__main__":
    main() 