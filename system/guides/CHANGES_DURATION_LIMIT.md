# Изменения ограничения длительности сегментов

## Проблема
Ранее существовало жесткое ограничение на минимальную длительность сегмента спикера (1.5 секунды), что приводило к потере коротких фраз и слов.

## Решение

### 1. Убрано жесткое ограничение
- **Было**: `if duration < min_segment_duration: continue`
- **Стало**: `if min_segment_duration > 0 and duration < min_segment_duration: continue`

### 2. Изменены значения по умолчанию
- **Было**: `min_segment_duration=1.5`
- **Стало**: `min_segment_duration=0.1`

### 3. Добавлена опция полного отключения
- **Новый параметр**: `--no_duration_limit`
- **Значение 0**: полностью отключает ограничение

## Использование

### Обработка всех сегментов (без ограничений)
```bash
python audio_processing.py --input audio.mp3 --output results --no_duration_limit
```

### Минимальное ограничение (0.1 секунды)
```bash
python audio_processing.py --input audio.mp3 --output results --min_speaker_segment 0.1
```

### Пользовательское ограничение
```bash
python audio_processing.py --input audio.mp3 --output results --min_speaker_segment 0.5
```

### Полное отключение через значение
```bash
python audio_processing.py --input audio.mp3 --output results --min_speaker_segment 0
```

## Преимущества

1. **Полнота данных**: обрабатываются все сегменты речи
2. **Гибкость**: можно настроить любое ограничение
3. **Совместимость**: работает с существующим кодом
4. **Производительность**: не влияет на скорость обработки

## Структура файлов

Теперь в папках спикеров будут файлы с любыми сегментами:
```
speaker_0001/
├── chunk_0001_part1.wav          # Может содержать короткие фразы
├── metadata_0001_part1.txt       # Все сегменты с метками времени
└── speaker_0001_info.txt         # Полная информация
```

## Тестирование

Запустите тест для проверки изменений:
```bash
python test_no_duration_limit.py
``` 