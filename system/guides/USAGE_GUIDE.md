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
start_processing.bat --input "audio.mp3" --output "no_silence" --steps vad
```

## 🎮 GPU ускорение

### Автоматическое определение
Система автоматически использует GPU если доступен:
- **Demucs** - шумоподавление с CUDA ускорением
- **Silero VAD** - удаление тишины с GPU
- **PyAnnote** - диаризация с GPU ускорением

### Проверка GPU
```bash
# Тест GPU
system\instructions\test_gpu.bat

# Проверка версий с GPU
system\instructions\check_versions.bat
```

### Производительность с GPU
- **Demucs**: 5-10x быстрее
- **Silero VAD**: 2-3x быстрее
- **PyAnnote**: 3-5x быстрее
- **Общее время**: сокращается в 3-5 раз

## 📊 Логирование

### Уровни логирования
- **INFO** - основная информация о процессе
- **WARNING** - предупреждения
- **ERROR** - ошибки
- **DEBUG** - отладочная информация (с `--verbose`)

### Просмотр логов
```bash
# Просмотр лога обработки
type results\audio_processing.log

# Поиск ошибок
findstr "ERROR" results\audio_processing.log
```

## 🔍 Устранение неполадок

### Частые проблемы

#### "Environment not found"
```bash
# Переустановите окружение
setup.bat
# Выберите опцию 1
```

#### Медленная обработка
```bash
# Проверьте GPU
system\instructions\test_gpu.bat

# Уменьшите размер чанков
start_processing.bat --input "audio.mp3" --output "results" --chunk_duration 300
```

#### Ошибки диаризации
```bash
# Проверьте токен
system\instructions\test_diarization_token.bat

# Настройте заново
system\instructions\setup_diarization.bat
```

### Исправление проблем
```bash
# Автоматическое исправление
system\instructions\fix_common_issues.bat
```

## 📚 Дополнительные ресурсы

- **[Основное руководство](MAIN_GUIDE.md)** - Полная установка и настройка
- **[Диаризация говорящих](DIARIZATION.md)** - Настройка и использование диаризации
- **[Примеры использования](EXAMPLES.md)** - Практические примеры
- **[Устранение неполадок](TROUBLESHOOTING.md)** - Решения проблем 