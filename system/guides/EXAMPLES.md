# 📋 Примеры использования

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
    --output "final_results" \
    --steps diar
```

### Пакетная обработка
```cmd
# Обработка всех MP3 файлов в папке
for %f in (*.mp3) do (
    start_processing.bat \
        --input "%f" \
        --output "results\%~nf" \
        --steps split,denoise,vad
)
```

## 📊 Анализ результатов

### Просмотр логов
```cmd
# Основной лог
type results\audio_processing.log

# Последние 50 строк
type results\audio_processing.log | tail -50

# Поиск ошибок
findstr "ERROR" results\audio_processing.log
```

### Анализ диаризации
```cmd
# Просмотр RTTM файла
type results\temp\diarized\audio_diarized.rttm

# Просмотр отчета
type results\temp\diarized\audio_diarized.txt

# Подсчет говорящих
findstr "SPEAKER" results\temp\diarized\audio_diarized.rttm | find /c "SPEAKER"
```

### Проверка качества
```cmd
# Размер файлов
dir results\*.wav /s

# Длительность аудио
ffprobe -v quiet -show_entries format=duration -of csv=p=0 results\chunk_0001.wav
```

## 🚨 Устранение проблем

### Медленная обработка
```cmd
# Уменьшите количество процессов
--workers 1

# Отключите GPU
--use_gpu False

# Уменьшите размер частей
--chunk_duration 200
```

### Недостаточно памяти
```cmd
# Обработка без диаризации
--steps split,denoise,vad

# Уменьшите размер частей
--chunk_duration 150

# Отключите параллельную обработку
--parallel False
```

### Плохое качество диаризации
```cmd
# Улучшите качество аудио
--steps split,denoise,vad,diar

# Настройте параметры
--min_speaker_segment 2.0 \
--max_speakers 3
```

## 📋 Чек-лист для разных типов контента

### Лекции и презентации
- [ ] Используйте `--steps split,denoise,vad`
- [ ] Настройте `--final_chunk_duration 30` или `60`
- [ ] Примените `--split_method word_boundary`
- [ ] Используйте `--workers 2-4`

### Совещания и интервью
- [ ] Добавьте `diar` в steps
- [ ] Настройте `--max_speakers` по количеству участников
- [ ] Используйте `--min_speaker_segment 1.5-2.0`
- [ ] Примените `--workers 4` для GPU

### Музыкальные записи
- [ ] Используйте только `--steps denoise`
- [ ] Отключите VAD для сохранения музыки
- [ ] Примените `--workers 2`
- [ ] Используйте `--use_gpu` для ускорения

### Записи с шумом
- [ ] Используйте `--steps denoise,vad`
- [ ] Настройте `--chunk_duration 300-600`
- [ ] Примените `--workers 1-2`
- [ ] Проверьте качество после каждого этапа

## 🔗 Связанные руководства

- **[Основное руководство](MAIN_GUIDE.md)** - Базовая установка и настройка
- **[Руководство по использованию](USAGE_GUIDE.md)** - Все параметры команд
- **[Диаризация говорящих](DIARIZATION.md)** - Настройка диаризации
- **[Быстрое исправление](TROUBLESHOOTING.md)** - Решения проблем
- **[Оптимизированная версия](OPTIMIZED_GUIDE.md)** - Продвинутые настройки 