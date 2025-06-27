#!/usr/bin/env python3
"""
Скрипт для тестирования токена HuggingFace и диагностики проблем с PyAnnote (через huggingface_hub)
Дополнительно тестирует диаризацию на реальном аудиофайле
"""

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError
from pathlib import Path
import tempfile
import subprocess
import os
import sys

def test_hf_token(token):
    print(f"Тестирование токена: {token[:10]}...")
    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        print(f"✓ Токен валиден! Пользователь: {user_info.get('name')}")
        return True
    except Exception as e:
        print(f"✗ Токен невалиден или ошибка: {e}")
        return False

def test_model_access(token, model_name):
    print(f"Тестирование доступа к модели: {model_name}")
    api = HfApi(token=token)
    try:
        model_info = api.model_info(model_name)
        print(f"✓ Доступ к модели {model_name} разрешен")
        print(f"  - Автор: {model_info.author}")
        # Проверяем наличие атрибута license перед его использованием
        if hasattr(model_info, 'license'):
            print(f"  - Лицензия: {model_info.license}")
        else:
            print(f"  - Лицензия: информация недоступна")
        return True
    except HfHubHTTPError as e:
        if e.response.status_code == 404:
            print(f"✗ Модель {model_name} не найдена")
        elif e.response.status_code == 401:
            print(f"✗ Нет доступа к модели {model_name} (401 Unauthorized)")
        elif e.response.status_code == 403:
            print(f"✗ Доступ к модели {model_name} запрещен (403 Forbidden)")
            print("  Возможные причины:")
            print("  1. Не приняты условия использования модели")
            print("  2. Токен не имеет прав доступа")
            print("  3. Модель приватная")
        else:
            print(f"✗ Ошибка доступа к модели: {e}")
        return False
    except Exception as e:
        print(f"✗ Ошибка тестирования модели: {e}")
        return False

def create_test_audio():
    """
    Создает простой тестовый аудиофайл с помощью ffmpeg
    """
    print("Создание тестового аудиофайла...")
    
    # Создаем временную папку
    temp_dir = Path("E:/Project/alltalk_tts/finetune/put-voice-samples-in-here")
    test_audio = temp_dir / "temp.mp3"
    
    try:
        # Создаем простой аудиофайл с тоном 440Hz на 60 секунд
        command = [
            "ffmpeg", "-f", "lavfi", "-i", "sine=frequency=440:duration=60",
            "-ar", "16000", "-ac", "1", str(test_audio),
            "-y"  # Перезаписать если существует
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0 and test_audio.exists():
            print(f"✓ Тестовый аудиофайл создан: {test_audio}")
            return str(test_audio)
        else:
            print(f"✗ Ошибка создания тестового аудио: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Ошибка при создании тестового аудио: {e}")
        return None

def test_diarization_with_audio(token, audio_file):
    """
    Тестирует диаризацию на реальном аудиофайле
    """
    print(f"\nТестирование диаризации на файле: {audio_file}")
    
    
    try:
        from pyannote.audio import Pipeline
        from pyannote.audio.pipelines.utils.hook import ProgressHook
        import torch
    except ImportError as e:
        print(f"✗ PyAnnote не установлен: {e}")
        print("Запустите setup_diarization.py для установки")
        return False
    
    # Проверяем доступность GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Используем устройство: {device}")
    
    try:
        # Загружаем модель диаризации
        print("Загрузка модели диаризации...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        # Перемещаем модель на GPU если доступен
        if device.type == "cuda":
            pipeline = pipeline.to(device)
            print("Модель перемещена на GPU")
        
        # Выполняем диаризацию
        print("Выполнение диаризации...")
        with ProgressHook() as hook:
            diarization = pipeline(audio_file, hook=hook)
        
        # Анализируем результаты
        speakers = set()
        total_duration = 0
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            total_duration += turn.end - turn.start
        
        print(f"✓ Диаризация завершена успешно!")
        print(f"  - Обнаружено спикеров: {len(speakers)}")
        print(f"  - Спикеры: {', '.join(sorted(speakers))}")
        print(f"  - Общая длительность речи: {total_duration:.2f} сек")
        
        # Создаем простой отчет
        output_dir = Path("test_diarization_results")
        output_dir.mkdir(exist_ok=True)
        
        rttm_file = output_dir / "test_diarization.rttm"
        with open(rttm_file, 'w') as f:
            diarization.write_rttm(f)
        
        report_file = output_dir / "test_diarization_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ТЕСТОВОЙ ДИАРИЗАЦИИ\n")
            f.write("="*50 + "\n\n")
            f.write(f"Тестовый файл: {audio_file}\n")
            f.write(f"Обнаружено спикеров: {len(speakers)}\n")
            f.write(f"Спикеры: {', '.join(sorted(speakers))}\n")
            f.write(f"Общая длительность речи: {total_duration:.2f} сек\n\n")
            f.write("ДЕТАЛЬНЫЙ ОТЧЕТ:\n")
            f.write("-"*30 + "\n")
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                start_time = turn.start
                end_time = turn.end
                duration = end_time - start_time
                f.write(f"{speaker}: {start_time:.2f}s - {end_time:.2f}s (длительность: {duration:.2f}s)\n")
        
        print(f"  - RTTM файл: {rttm_file}")
        print(f"  - Отчет: {report_file}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Ошибка при диаризации: {error_msg}")
        
        # Проверяем тип ошибки и даем рекомендации
        if "Could not download" in error_msg or "private or gated" in error_msg:
            print("ПРОБЛЕМА: Модель не загружена из-за проблем с токеном или условиями использования")
            print("РЕШЕНИЕ:")
            print("1. Запустите: quick_diarization_setup.bat")
            print("2. Или следуйте инструкциям в DIARIZATION_SETUP_GUIDE.md")
            print("3. Убедитесь, что вы приняли условия использования на HuggingFace")
        elif "NoneType" in error_msg:
            print("ПРОБЛЕМА: Модель не инициализирована")
            print("РЕШЕНИЕ: Проверьте токен и перезапустите настройку диаризации")
        else:
            print("ПРОБЛЕМА: Неожиданная ошибка при диаризации")
            print("РЕШЕНИЕ: Проверьте интернет-соединение и попробуйте снова")
        
        return False

def main():
    print("ДИАГНОСТИКА TOKEN И ТЕСТИРОВАНИЕ ДИАРИЗАЦИИ")
    print("="*50)
    
    # Читаем токен из файла
    token_file = Path("hf_token.txt")
    if not token_file.exists():
        print("✗ Файл hf_token.txt не найден")
        print("Запустите setup_diarization.py для настройки токена")
        return
    
    with open(token_file, "r") as f:
        token = f.read().strip()
    
    if not token:
        print("✗ Токен пустой в файле hf_token.txt")
        print("Запустите setup_diarization.py для настройки токена")
        return
    
    print(f"Найден токен: {token[:10]}...")
    
    # Тестируем токен
    if not test_hf_token(token):
        print("\nРЕШЕНИЕ:")
        print("1. Перейдите на https://huggingface.co/settings/tokens")
        print("2. Создайте новый токен с правами 'Read'")
        print("3. Запустите setup_diarization.py и введите новый токен")
        return
    
    # Тестируем доступ к моделям PyAnnote
    models_to_test = [
        "pyannote/speaker-diarization-3.1"
    ]
    
    print("\nТестирование доступа к моделям PyAnnote:")
    all_models_accessible = True
    
    for model in models_to_test:
        print(f"\n--- {model} ---")
        if not test_model_access(token, model):
            all_models_accessible = False
    
    if not all_models_accessible:
        print("\n" + "="*50)
        print("⚠️  ПРОБЛЕМЫ С ДОСТУПОМ К МОДЕЛЯМ")
        print("="*50)
        print("Следуйте инструкциям выше для исправления.")
        return
    
    # Тестируем диаризацию на реальном аудиофайле
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ДИАРИЗАЦИИ НА РЕАЛЬНОМ АУДИО")
    print("="*50)
    
    # Используем реальный аудиофайл
    temp_dir = Path("E:/Project/alltalk_tts/finetune/put-voice-samples-in-here")
    test_audio = temp_dir / "temp.mp3"
    
    if not test_audio.exists():
        print(f"✗ Аудиофайл не найден: {test_audio}")
        print("Создаем тестовый аудиофайл...")
        test_audio = create_test_audio()
        if not test_audio:
            print("Не удалось создать тестовый аудиофайл. Проверьте установку ffmpeg.")
            return
    else:
        print(f"✓ Используем существующий аудиофайл: {test_audio}")
    
    # Тестируем диаризацию
    diarization_success = test_diarization_with_audio(token, test_audio)
    
    # Очищаем временные файлы только если это был созданный тестовый файл
    if "temp.mp3" in str(test_audio) and test_audio.exists():
        try:
            test_audio.unlink()
            print(f"Тестовый файл удален: {test_audio}")
        except Exception as e:
            print(f"Не удалось удалить тестовый файл: {e}")
    
    # Финальный результат
    print("\n" + "="*50)
    if diarization_success:
        print("✅ ДИАРИЗАЦИЯ РАБОТАЕТ КОРРЕКТНО!")
        print("="*50)
        print("Все тесты пройдены успешно. Диаризация готова к использованию.")
    else:
        print("❌ ПРОБЛЕМЫ С ДИАРИЗАЦИЕЙ")
        print("="*50)
        print("Следуйте инструкциям выше для исправления проблем.")

if __name__ == "__main__":
    main() 