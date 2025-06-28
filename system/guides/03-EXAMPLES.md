# 📋 Примеры использования - Audio Processing Pipeline

Практические примеры использования системы обработки аудио для различных сценариев.

## 🚀 Быстрые примеры

### 1. Обработка лекции
```cmd
start_processing.bat \
    --input "lecture.mp3" \
    --output "lecture_results" \
    --steps split,denoise,vad \
    --create_final_chunks \
    --final_chunk_duration 30
```

**Результат:** Очищенная лекция, нарезанная на 30-секундные чанки.

### 2. Обработка совещания с диаризацией
```cmd
start_processing.bat \
    --input "meeting.mp3" \
    --output "meeting_results" \
    --steps split,denoise,vad,diar \
    --workers 4 \
    --use_gpu
```

**Результат:** Очищенное совещание с определением говорящих.

### 3. Только очистка аудио
```cmd
start_processing.bat \
    --input "noisy_audio.mp3" \
    --output "clean_results" \
    --steps denoise,vad
```

**Результат:** Очищенное от шума и тишины аудио.

## 🎯 Специализированные сценарии

### Подкаст с несколькими спикерами
```cmd
start_processing.bat \
    --input "podcast.mp3" \
    --output "podcast_results" \
    --steps split,denoise,vad,diar \
    --min_speaker_segment 2.0 \
    --max_speakers 3 \
    --workers 4 \
    --use_gpu \
    --create_final_chunks \
    --final_chunk_duration 60
```

**Особенности:**
- Оптимизировано для 2-3 говорящих
- Длинные сегменты (2+ секунды)
- 60-секундные финальные чанки

### Интервью (вопрос-ответ)
```cmd
start_processing.bat \
    --input "interview.mp3" \
    --output "interview_results" \
    --steps split,denoise,vad,diar \
    --min_speaker_segment 1.5 \
    --max_speakers 2 \
    --min_speakers 2 \
    --workers 2
```

**Особенности:**
- Точно 2 говорящих
- Короткие сегменты для быстрых переключений
- Умеренное количество процессов

### Лекция с музыкой
```cmd
start_processing.bat \
    --input "lecture_with_music.mp3" \
    --output "lecture_clean" \
    --steps split,denoise,vad \
    --chunk_duration 300 \
    --workers 1 \
    --use_gpu
```

**Особенности:**
- Удаление фоновой музыки
- Длинные части для стабильности
- Один процесс для последовательности

### Запись с шумом
```cmd
start_processing.bat \
    --input "noisy_recording.mp3" \
    --output "clean_recording" \
    --steps denoise,vad \
    --workers 2 \
    --use_gpu
```

**Особенности:**
- Только очистка, без нарезки
- Удаление шума и тишины
- Сохранение оригинальной структуры

## ⚙️ Настройки для разных систем

### Мощная система (RTX 5080 + 32GB RAM)
```cmd
start_processing.bat \
    --input "audio.mp3" \
    --output "results" \
    --steps split,denoise,vad,diar \
    --workers 4 \
    --chunk_duration 600 \
    --use_gpu \
    --parallel \
    --create_final_chunks \
    --final_chunk_duration 30
```

### Средняя система (GTX 1060 + 16GB RAM)
```cmd
start_processing.bat \
    --input "audio.mp3" \
    --output "results" \
    --steps split,denoise,vad,diar \
    --workers 2 \
    --chunk_duration 300 \
    --use_gpu \
    --parallel
```

### Слабая система (CPU + 8GB RAM)
```cmd
start_processing.bat \
    --input "audio.mp3" \
    --output "results" \
    --steps split,denoise,vad \
    --workers 1 \
    --chunk_duration 200 \
    --use_gpu False \
    --parallel False
```

## 🎵 Типы контента

### Музыкальные записи
```cmd
# Удаление вокала, сохранение инструментов
start_processing.bat \
    --input "song_with_vocals.mp3" \
    --output "instrumental" \
    --steps denoise \
    --workers 2 \
    --use_gpu
```

### Аудиокниги
```cmd
# Очистка и нарезка на главы
start_processing.bat \
    --input "audiobook.mp3" \
    --output "audiobook_clean" \
    --steps split,denoise,vad \
    --split_method word_boundary \
    --create_final_chunks \
    --final_chunk_duration 300
```

### Записи с конференций
```cmd
# Обработка с множественными спикерами
start_processing.bat \
    --input "conference.mp3" \
    --output "conference_results" \
    --steps split,denoise,vad,diar \
    --min_speaker_segment 1.0 \
    --max_speakers 10 \
    --workers 4 \
    --use_gpu
```

## 🔧 Комбинированные сценарии

### Поэтапная обработка
```cmd
# Этап 1: Очистка
start_processing.bat \
    --input "raw_audio.mp3" \
    --output "step1_clean" \
    --steps denoise,vad

# Этап 2: Нарезка
start_processing.bat \
    --input "step1_clean" \
    --output "step2_split" \
    --steps split

# Этап 3: Диаризация
start_processing.bat \
    --input "step2_split" \
    --output "step3_diarized" \
    --steps diar
```

### Обработка папки с файлами
```cmd
# Обработка всех MP3 файлов в папке
start_processing.bat \
    --input "audio_folder" \
    --output "processed_folder" \
    --steps split,denoise,vad \
    --workers 2
```

### Создание финальных чанков
```cmd
# Обработка с созданием финальных чанков
start_processing.bat \
    --input "long_audio.mp3" \
    --output "final_chunks" \
    --steps split,denoise,vad \
    --create_final_chunks \
    --final_chunk_duration 60 \
    --workers 2
```

## 🎯 Оптимизация для конкретных задач

### Подготовка для транскрипции
```cmd
start_processing.bat \
    --input "interview.mp3" \
    --output "transcription_ready" \
    --steps split,denoise,vad \
    --final_chunk_duration 60 \
    --split_method word_boundary \
    --workers 2
```

### Очистка для архивирования
```cmd
start_processing.bat \
    --input "archive_audio.mp3" \
    --output "clean_archive" \
    --steps denoise,vad \
    --workers 1
```

### Обработка для стриминга
```cmd
start_processing.bat \
    --input "stream_audio.mp3" \
    --output "stream_ready" \
    --steps split,denoise,vad \
    --final_chunk_duration 30 \
    --workers 2
```

## 🔗 Объединение результатов

### Объединение обработанных файлов
```cmd
# Объединение всех чанков
audio_concat.bat "results" "combined_audio.mp3"

# Объединение с сортировкой по имени
audio_concat.bat "chunks" "sorted_audio.mp3"
```

### Создание плейлиста
```cmd
# После обработки создайте плейлист из чанков
dir /b results\*.wav > playlist.txt
```

## 📊 Анализ результатов

### Проверка качества обработки
```cmd
# Активируйте окружение для анализа
activate_environment.bat

# Проверьте длительность файлов
python -c "import librosa; print(librosa.get_duration(filename='results/chunk_0001.wav'))"
```

### Анализ диаризации
```cmd
# Просмотр результатов диаризации
type temp\diarized\audio_diarized.txt
```

## 🚨 Частые ошибки и решения

### Ошибка "File not found"
```cmd
# Проверьте путь к файлу
dir "audio.mp3"

# Используйте абсолютный путь
start_processing.bat --input "C:\path\to\audio.mp3" --output "results"
```

### Ошибка "Out of memory"
```cmd
# Уменьшите размер чанков
start_processing.bat --input "audio.mp3" --output "results" --chunk_duration 200

# Отключите GPU
start_processing.bat --input "audio.mp3" --output "results" --use_gpu False
```

### Медленная обработка
```cmd
# Увеличьте количество процессов
start_processing.bat --input "audio.mp3" --output "results" --workers 4

# Используйте GPU
start_processing.bat --input "audio.mp3" --output "results" --use_gpu
```

## 📚 Следующие шаги

После изучения примеров:

1. **[Руководство по использованию](04-USAGE.md)** - Все команды и параметры
2. **[Диаризация говорящих](05-DIARIZATION.md)** - Настройка HuggingFace токенов
3. **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка GPU и CPU
4. **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем

## 🔗 Связанные руководства

- **[Быстрый старт](02-QUICK_START.md)** - Базовые команды
- **[Руководство по использованию](04-USAGE.md)** - Все параметры
- **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка производительности 