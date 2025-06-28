# Новая архитектура аудио обработки с организацией по спикерам

## Обзор

Новая архитектура обеспечивает:
1. **Многопоточную обработку** всех этапов кроме диаризации
2. **Блокировку диаризации** - только один поток может использовать PyAnnote
3. **Организацию по спикерам** - каждый спикер в отдельной папке
4. **Метки времени** для каждого чанка и сегмента

## Структура обработки

### 1. Разделение на чанки (многопоточное)
- **Whisper анализ** для определения границ предложений
- **Максимум 10 минут** на чанк
- **Метаданные чанка**: номер, время начала/конца, длительность

### 2. Деноизинг (многопоточное)
- **Demucs модель** для удаления музыки и шума
- **4 потока** одновременно
- **GPU оптимизация** с управлением памятью

### 3. Удаление тишины (многопоточное)
- **Silero VAD** для определения речи
- **4 потока** одновременно
- **Настраиваемые параметры** длительности

### 4. Диаризация (блокированная)
- **PyAnnote speaker-diarization-3.1**
- **Только один поток** (блокировка DIARIZATION_LOCK)
- **Создание папок по спикерам**

### 5. Организация файлов
- **Папка для каждого спикера**: `speaker_0001`, `speaker_0002`, etc.
- **Аудиофайлы**: `chunk_0001_*.wav`
- **Метаданные**: `metadata_*.txt` с временными метками
- **Информация**: `speaker_*_info.txt`

## Структура выходных файлов

```
output/
├── speaker_0001/
│   ├── chunk_0001_part1.wav
│   ├── chunk_0001_part2.wav
│   ├── metadata_0001_part1.txt
│   ├── metadata_0001_part2.txt
│   └── speaker_0001_info.txt
├── speaker_0002/
│   ├── chunk_0002_part1.wav
│   ├── metadata_0002_part1.txt
│   └── speaker_0002_info.txt
└── ...
```

## Метаданные

### Файл метаданных спикера
```
Speaker: SPEAKER_00
Source file: audio.mp3
Chunk: 1
Chunk start time: 0.00s
Chunk end time: 600.00s
Total segments: 15
Total duration: 245.67s

Segments:
--------------------------------------------------
  1.     12.50s -    45.20s (duration:  32.70s)
  2.     67.30s -    89.45s (duration:  22.15s)
  3.    123.80s -   156.90s (duration:  33.10s)
  ...
```

### Файл информации о спикере
```
Speaker ID: 0001
Original Speaker: SPEAKER_00
Total audio files: 3
Total metadata files: 3
Folder: /path/to/speaker_0001

Audio files:
  - chunk_0001_part1.wav
  - chunk_0001_part2.wav
  - chunk_0001_part3.wav

Metadata files:
  - metadata_0001_part1.txt
  - metadata_0001_part2.txt
  - metadata_0001_part3.txt
```

## Многопоточность

### Потоки на файл: 4
- **Деноизинг**: параллельно
- **VAD**: параллельно  
- **Диаризация**: блокированная (1 поток)
- **FFmpeg**: параллельно

### Потоки на несколько файлов: 4
- **ThreadPoolExecutor** для совместимости с менеджерами
- **Объединение результатов** по спикерам
- **Автоматическая очистка** временных файлов

## Блокировка диаризации

```python
# Глобальная блокировка
DIARIZATION_LOCK = threading.Lock()

# Использование в коде
with DIARIZATION_LOCK:
    diarized_files = diarize_with_pyannote_optimized(...)
```

## Преимущества новой архитектуры

1. **Производительность**: 4x ускорение за счет многопоточности
2. **Организация**: четкая структура по спикерам
3. **Метаданные**: полная информация о времени и чанках
4. **Совместимость**: работает с существующими менеджерами
5. **Надежность**: блокировка предотвращает конфликты диаризации

## Использование

```python
# Обработка одного файла
organized_speakers = process_file_multithreaded_optimized(
    audio_file, output_dir, steps, chunk_duration,
    min_speaker_segment, split_method, use_gpu, 
    logger, model_manager, gpu_manager
)

# Обработка нескольких файлов
all_speakers = process_multiple_files_parallel_optimized(
    files, output_dir, steps, chunk_duration,
    min_speaker_segment, split_method, use_gpu, logger
)
``` 