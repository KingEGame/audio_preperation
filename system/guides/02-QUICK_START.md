# 🚀 Быстрый старт - Audio Processing Pipeline

Быстрое руководство для начала работы после установки системы.

## ✅ После установки

После запуска `setup.bat` и выбора опции **1** в корне проекта создаются удобные bat-файлы:

- `start_processing.bat` - Запуск обработки аудио
- `activate_environment.bat` - Активация окружения
- `audio_concat.bat` - Объединение аудиофайлов

## 🎵 Первая обработка

### Базовая обработка
```bash
# Обработка аудио файла
start_processing.bat --input "audio.mp3" --output "results"

# Объединение файлов
audio_concat.bat "chunks" "combined_audio.mp3"
```

### Полная обработка с диаризацией
```bash
start_processing.bat --input "meeting.mp3" --output "results" --steps split denoise vad diar
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

## ⚙️ Основные параметры

| Параметр | Сокращение | Описание | По умолчанию |
|----------|------------|----------|--------------|
| `--input` | `-i` | Входной файл или папка | Обязательный |
| `--output` | `-o` | Выходная папка | Обязательный |
| `--chunk_duration` | | Длительность промежуточных кусков (сек) | 600 |
| `--final_chunk_duration` | | Длительность финальных чанков (сек) | 30 |
| `--steps` | | Этапы обработки | split denoise vad diar |
| `--create_final_chunks` | | Создать финальные чанки | False |
| `--verbose` | `-v` | Подробное логирование | False |

## 🎯 Этапы обработки (`--steps`)

- **split** - нарезка на куски по времени или на границах слов
- **denoise** - удаление шума и музыки (Demucs) с GPU ускорением
- **vad** - удаление тишины (Silero VAD) с GPU ускорением
- **diar** - диаризация говорящих (PyAnnote) с GPU ускорением

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

## 🎯 Быстрые примеры

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

## 🔧 Проверка работы

### Тест системы
```bash
setup.bat
# Выберите опцию 2 - Test Everything
```

### Тест GPU
```bash
setup.bat
# Выберите опцию 4 → опция 7
```

### Проверка версий
```bash
setup.bat
# Выберите опцию 3
```

## 🚨 Частые проблемы

### Ошибка "Environment not found"
```bash
# Переустановите окружение
setup.bat → опция 1
```

### Ошибка "Python not found"
```bash
# Исправьте активацию окружения
setup.bat → опция 4 → опция 6
```

### Медленная обработка
```bash
# Проверьте GPU
setup.bat → опция 2

# Установите оптимизированные зависимости
setup.bat → опция 4 → опция 11
```

## 📚 Следующие шаги

После освоения базовых команд:

1. **[Примеры использования](03-EXAMPLES.md)** - Больше практических примеров
2. **[Руководство по использованию](04-USAGE.md)** - Все команды и параметры
3. **[Диаризация говорящих](05-DIARIZATION.md)** - Настройка HuggingFace токенов
4. **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройка GPU и CPU

## 🔗 Связанные руководства

- **[Установка и настройка](01-INSTALLATION.md)** - Полная установка системы
- **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем
- **[Установка PyTorch](07-PYTORCH.md)** - Настройка CUDA и GPU 