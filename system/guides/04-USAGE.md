# 🎵 Руководство по использованию - Audio Processing Pipeline

Подробное руководство по использованию системы обработки аудио.

## 🚀 Быстрый старт

### После установки

После запуска `setup.bat` и выбора опции **1** в корне проекта создаются удобные bat-файлы:

- `start_processing.bat` - Запуск обработки аудио
- `activate_environment.bat` - Активация окружения
- `audio_concat.bat` - Объединение аудиофайлов

### Первая обработка

```bash
# Базовая обработка
start_processing.bat --input "audio.mp3" --output "results"

# Объединение файлов
audio_concat.bat "chunks" "combined_audio.mp3"
```

## 📋 Основные команды

### 🎵 Обработка аудио

#### Базовая обработка
```bash
start_processing.bat --input "audio.mp3" --output "results"
```

#### Полная обработка с диаризацией
```bash
start_processing.bat --input "meeting.mp3" --output "results" --steps split denoise vad diar
```

#### Только очистка (без нарезки)
```bash
start_processing.bat --input "clean_audio.mp3" --output "results" --steps denoise vad
```

#### Создание финальных чанков
```bash
start_processing.bat --input "audio.mp3" --output "results" --create_final_chunks --final_chunk_duration 30
```

### 🔗 Объединение файлов

#### Объединение всех MP3 файлов из папки
```bash
audio_concat.bat "input_folder" "output_file.mp3"
```

#### Примеры использования
```bash
# Объединение чанков
audio_concat.bat "chunks" "combined_audio.mp3"

# Объединение результатов
audio_concat.bat "results" "final_audio.mp3"
```

### 🐍 Активация окружения

#### Для ручной работы с Python
```bash
activate_environment.bat
```

После активации доступны команды:
```bash
# Проверка версий
python -c "import torch; print(torch.__version__)"

# Запуск скриптов напрямую
python scripts\audio_processing.py --help

# Тест GPU
python scripts\test_gpu.py
```

## ⚙️ Параметры командной строки

### Основные параметры

| Параметр | Сокращение | Описание | По умолчанию |
|----------|------------|----------|--------------|
| `--input` | `-i` | Входной файл или папка | Обязательный |
| `--output` | `-o` | Выходная папка | Обязательный |
| `--chunk_duration` | | Длительность промежуточных кусков (сек) | 600 |
| `--final_chunk_duration` | | Длительность финальных чанков (сек) | 30 |
| `--steps` | | Этапы обработки | split denoise vad diar |
| `--split_method` | | Метод разделения | simple |
| `--create_final_chunks` | | Создать финальные чанки | False |
| `--verbose` | `-v` | Подробное логирование | False |
| `--interactive` | | Интерактивный режим | False |

### Этапы обработки (`--steps`)

- **split** - нарезка на куски по времени или на границах слов
- **denoise** - удаление шума и музыки (Demucs) с GPU ускорением
- **vad** - удаление тишины (Silero VAD) с GPU ускорением
- **diar** - диаризация говорящих (PyAnnote) с GPU ускорением

### Методы разделения (`--split_method`)

- **simple** - разделение по времени
- **word_boundary** - разделение на границах слов (требует Whisper)

## 📁 Структура результатов

### Без финальных чанков
```
results/
└── audio_processing.log           # Лог обработки
```

### С финальными чанками
```
results/
├── chunk_0001.wav                 # Финальные чанки (30 сек каждый)
├── chunk_0002.wav
├── chunk_0003.wav
└── audio_processing.log           # Лог обработки
```

### С диаризацией
```
temp/
├── parts/                         # Нарезанные куски
├── cleaned/                       # Очищенные от шума файлы (GPU)
├── temp_analysis/                 # Временные файлы анализа
└── diarized/                      # Диаризованные файлы (GPU)
    ├── audio_diarized.rttm        # RTTM файл с метками спикеров
    └── audio_diarized.txt         # Текстовый отчет диаризации
```

## 🎯 Примеры использования

### 🎓 Обработка лекции

```bash
# Полная обработка лекции
start_processing.bat --input "lecture.mp3" --output "lecture_results" --steps split denoise vad diar

# Создание чанков по 15 минут
start_processing.bat --input "lecture.mp3" --output "lecture_results" --final_chunk_duration 900
```

### 🏢 Обработка встречи

```bash
# Обработка с диаризацией говорящих
start_processing.bat --input "meeting.mp3" --output "meeting_results" --steps split denoise vad diar

# Объединение результатов
audio_concat.bat "meeting_results" "final_meeting.mp3"
```

### 🎵 Очистка музыкального файла

```bash
# Только удаление шума
start_processing.bat --input "noisy_music.mp3" --output "clean_music" --steps denoise
```

### 📝 Подготовка для транскрипции

```bash
# Очистка и нарезка для лучшей транскрипции
start_processing.bat --input "interview.mp3" --output "transcription_ready" --steps split denoise vad --final_chunk_duration 60
```

## 🔧 Продвинутые настройки

### Оптимизация производительности

#### Для GPU
```bash
# Увеличьте размер чанков для лучшего использования GPU
start_processing.bat --input "audio.mp3" --output "results" --chunk_duration 1200
```

#### Для CPU
```bash
# Уменьшите размер чанков для экономии памяти
start_processing.bat --input "audio.mp3" --output "results" --chunk_duration 300
```

### Кастомная обработка

#### Только диаризация
```bash
start_processing.bat --input "clean_audio.mp3" --output "diarized" --steps diar
```

#### Только удаление тишины
```bash
start_processing.bat --input "audio.mp3" --output "results" --steps vad
```

#### Разделение на границах слов
```bash
start_processing.bat --input "audio.mp3" --output "results" --split_method word_boundary
```

## 🎛️ Дополнительные параметры

### Параметры диаризации

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--min_speaker_segment` | Минимальная длительность сегмента спикера (сек) | 1.0 |
| `--max_speakers` | Максимальное количество спикеров | 10 |
| `--min_speakers` | Минимальное количество спикеров | 1 |

### Параметры производительности

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--workers` | Количество параллельных процессов | Автоопределение |
| `--use_gpu` | Использовать GPU | True |
| `--parallel` | Параллельная обработка | True |

### Параметры логирования

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--verbose` | Подробное логирование | False |
| `--log_level` | Уровень логирования | INFO |
| `--save_logs` | Сохранять логи в файл | True |

## 🔄 Интерактивный режим

### Запуск интерактивного режима
```bash
start_processing.bat --interactive
```

### Примеры интерактивного использования
```bash
# Выбор файла
Enter input file path: lecture.mp3

# Выбор папки для результатов
Enter output folder: results

# Выбор этапов обработки
Select processing steps (split,denoise,vad,diar): split,denoise,vad

# Создание финальных чанков
Create final chunks? (y/n): y
Final chunk duration (seconds): 30
```

## 📊 Мониторинг процесса

### Просмотр логов в реальном времени
```bash
# В отдельном окне
tail -f results/audio_processing.log
```

### Проверка прогресса
```bash
# Количество обработанных файлов
dir temp\parts\*.wav | find /c ".wav"

# Размер результатов
dir results /s
```

### Анализ использования ресурсов
```bash
# Мониторинг GPU
nvidia-smi

# Мониторинг CPU и памяти
tasklist | findstr python
```

## 🔗 Интеграция с другими инструментами

### Использование с FFmpeg
```bash
# Конвертация в другие форматы
ffmpeg -i results/chunk_0001.wav -c:a aac output.m4a

# Изменение качества
ffmpeg -i results/chunk_0001.wav -b:a 128k output.mp3
```

### Использование с Whisper
```bash
# Транскрипция обработанных чанков
whisper results/chunk_0001.wav --language Russian

# Пакетная транскрипция
for file in results/*.wav; do whisper "$file" --language Russian; done
```

### Использование с Python
```bash
# Активация окружения
activate_environment.bat

# Импорт модулей
python -c "from scripts.audio import process_audio_file_optimized; print('Ready')"
```

## 🚨 Обработка ошибок

### Типичные ошибки и решения

#### Ошибка "File not found"
```bash
# Проверьте путь к файлу
dir "audio.mp3"

# Используйте абсолютный путь
start_processing.bat --input "C:\path\to\audio.mp3" --output "results"
```

#### Ошибка "Out of memory"
```bash
# Уменьшите размер чанков
start_processing.bat --input "audio.mp3" --output "results" --chunk_duration 200

# Отключите GPU
start_processing.bat --input "audio.mp3" --output "results" --use_gpu False
```

#### Ошибка "CUDA not available"
```bash
# Проверьте установку CUDA
setup.bat → опция 4 → опция 7

# Используйте CPU
start_processing.bat --input "audio.mp3" --output "results" --use_gpu False
```

## 📚 Следующие шаги

После изучения всех команд:

1. **[Диаризация говорящих](05-DIARIZATION.md)** - Настройка HuggingFace токенов
2. **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка GPU и CPU
3. **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем
4. **[Структура проекта](08-STRUCTURE.md)** - Детальное описание файлов

## 🔗 Связанные руководства

- **[Быстрый старт](02-QUICK_START.md)** - Базовые команды
- **[Примеры использования](03-EXAMPLES.md)** - Практические примеры
- **[Диаризация говорящих](05-DIARIZATION.md)** - Настройка HuggingFace токенов
- **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка производительности 