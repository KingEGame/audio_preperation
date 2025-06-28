# Модульная система обработки аудио

Данная папка содержит модульную систему для обработки аудио файлов, разделенную на логические компоненты.

## Структура модулей

### `__init__.py`
Инициализационный файл пакета, экспортирует основные функции и классы для использования в главном скрипте.

### `config.py`
Конфигурационные константы и функции настройки системы:
- `MAX_WORKERS`, `GPU_MEMORY_LIMIT`, `BATCH_SIZE` - глобальные настройки
- `get_optimal_workers()` - определение оптимального количества процессов
- `setup_gpu_optimization()` - настройка GPU для производительности

### `managers.py`
Менеджеры для управления ресурсами:
- `GPUMemoryManager` - управление GPU памятью с автоматической очисткой
- `ModelManager` - централизованное управление ML моделями с кэшированием

### `processors.py`
Основные процессоры обработки аудио:
- `process_audio_file_optimized()` - обработка одного аудио файла
- `process_parts_optimized()` - обработка частей аудио файла
- `process_single_part_optimized()` - обработка одной части

### `stages.py`
Функции для отдельных этапов обработки:
- `clean_audio_with_demucs_optimized()` - шумоподавление с Demucs
- `remove_silence_with_silero_optimized()` - удаление тишины с Silero VAD
- `diarize_with_pyannote_optimized()` - диаризация спикеров с PyAnnote
- `create_speaker_segments_optimized()` - создание сегментов спикеров

### `splitters.py`
Функции разбивки аудио на части:
- `split_audio_by_duration_optimized()` - разбивка по времени
- `split_audio_at_word_boundary_optimized()` - разбивка по границам слов

### `utils.py`
Утилиты и вспомогательные функции:
- `get_mp3_duration()` - получение длительности аудио
- `setup_logging()` - настройка логирования
- `copy_results_to_output_optimized()` - копирование результатов
- `parallel_audio_processing_optimized()` - параллельная обработка

## Использование

Импорт основных функций из пакета:

```python
from audio import (
    setup_logging, get_mp3_duration, setup_gpu_optimization, 
    get_optimal_workers, parallel_audio_processing_optimized,
    process_audio_file_optimized, GPUMemoryManager, ModelManager
)
```

## Преимущества модульной структуры

1. **Читаемость** - код разделен на логические блоки
2. **Поддержка** - легче найти и исправить ошибки
3. **Расширяемость** - простое добавление новых функций
4. **Тестирование** - можно тестировать отдельные модули
5. **Переиспользование** - модули можно использовать в других проектах

## Главный скрипт

Главный файл `audio_processing.py` теперь содержит только:
- Функцию `main()` с обработкой аргументов
- Интерактивное меню `show_interactive_menu()`
- Логику координации обработки

Размер главного файла сокращен с ~1270 строк до ~340 строк.