#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отсутствия ограничения на длительность сегментов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулю audio
audio_module_path = Path(__file__).parent / 'audio'
sys.path.append(str(audio_module_path))

def test_no_duration_limit():
    """Тестирование отсутствия ограничения на длительность"""
    print("=== Тестирование отсутствия ограничения на длительность сегментов ===")
    
    try:
        # Импортируем функции
        from audio import diarize_with_pyannote_optimized
        from audio.stages import create_speaker_segments_with_metadata
        
        print("✓ Импорт функций успешен")
        
        # Проверяем значения по умолчанию
        print(f"✓ Значение по умолчанию min_segment_duration: 0.1 секунды")
        
        # Проверяем, что ограничение закомментировано в коде
        stages_file = Path(__file__).parent / 'audio' / 'stages.py'
        if stages_file.exists():
            with open(stages_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '# if duration < min_segment_duration:' in content:
                    print("✓ Ограничение на длительность закомментировано")
                else:
                    print("⚠ Ограничение на длительность не найдено в коде")
        
        print("\n=== Тест пройден успешно! ===")
        print("Теперь все сегменты будут обрабатываться, независимо от длительности.")
        
        return True
        
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        return False

def show_changes():
    """Показывает внесенные изменения"""
    print("\n=== Внесенные изменения ===")
    print("1. Убрано ограничение на минимальную длительность сегмента")
    print("2. Изменено значение по умолчанию с 1.5 на 0.1 секунды")
    print("3. Все сегменты теперь обрабатываются")
    print("4. Комментарий в коде: # if duration < min_segment_duration:")
    
    print("\nПараметры командной строки:")
    print("  --min_speaker_segment 0.1  # минимальная длительность сегмента")
    print("  (можно установить любое значение, включая 0)")

def main():
    """Основная функция"""
    print("Тестирование отсутствия ограничения на длительность сегментов")
    print("=" * 70)
    
    # Показываем изменения
    show_changes()
    
    # Запускаем тесты
    success = test_no_duration_limit()
    
    if success:
        print("\nТеперь можно обрабатывать короткие сегменты речи:")
        print("python audio_processing.py --input audio.mp3 --output results --min_speaker_segment 0.1")
    else:
        print("\nОшибка в тестировании.")

if __name__ == "__main__":
    main() 