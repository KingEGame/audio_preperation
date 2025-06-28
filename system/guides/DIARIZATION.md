# 🎯 Диаризация говорящих

## 📖 Что такое диаризация?

Диаризация - это процесс автоматического определения "кто говорит когда" в аудиозаписи. Система может:

- **Определить количество говорящих** в записи
- **Разделить речь по времени** для каждого говорящего
- **Создать временные метки** начала и конца каждого сегмента
- **Генерировать отчеты** с детальной информацией

## 🚀 Быстрая настройка

### 1. Автоматическая настройка
```cmd
setup_diarization.bat
```

### 2. Через setup.bat
```cmd
setup.bat
```
Выберите опцию **2** → Следуйте инструкциям

## 🔧 Ручная настройка

### 1. Создание аккаунта HuggingFace
1. Перейдите на [https://huggingface.co/join](https://huggingface.co/join)
2. Создайте аккаунт (бесплатно)
3. Подтвердите email

### 2. Создание токена доступа
1. Перейдите на [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Нажмите "New token"
3. Выберите "Read" права
4. Скопируйте токен

### 3. Принятие условий использования модели
1. Перейдите на [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. Нажмите "Accept" для принятия условий
3. Перейдите на [https://huggingface.co/pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
4. Нажмите "Accept" для принятия условий

### 4. Сохранение токена
```cmd
# Создайте файл с токеном
echo YOUR_HUGGINGFACE_TOKEN > hf_token.txt
```

## 🎯 Использование диаризации

### Базовое использование
```cmd
start_processing.bat \
    --input "meeting.mp3" \
    --output "results" \
    --steps split,denoise,vad,diar
```

### Только диаризация (без очистки)
```cmd
start_processing.bat \
    --input "clean_audio.mp3" \
    --output "results" \
    --steps diar
```

### Настройка параметров диаризации
```cmd
start_processing.bat \
    --input "audio.mp3" \
    --output "results" \
    --steps split,denoise,vad,diar \
    --min_speaker_segment 2.0 \
    --max_speakers 5
```

## 📊 Результаты диаризации

### RTTM файл (Rich Transcription Time Marked)
```
SPEAKER audio 1 0.0 2.5 <NA> <NA> SPEAKER_00 <NA> <NA>
SPEAKER audio 1 2.5 1.8 <NA> <NA> SPEAKER_01 <NA> <NA>
SPEAKER audio 1 4.3 3.2 <NA> <NA> SPEAKER_00 <NA> <NA>
```

**Формат:** `SPEAKER <file> <channel> <start> <duration> <ortho> <speaker_type> <speaker_name> <conf> <lat>`

### Текстовый отчет
```
=== Диаризация говорящих ===
Общее время: 120.5 секунд
Количество говорящих: 3

SPEAKER_00:
- Сегментов: 15
- Общее время: 45.2 сек (37.5%)
- Средняя длительность: 3.0 сек

SPEAKER_01:
- Сегментов: 12
- Общее время: 38.7 сек (32.1%)
- Средняя длительность: 3.2 сек

SPEAKER_02:
- Сегментов: 8
- Общее время: 36.6 сек (30.4%)
- Средняя длительность: 4.6 сек
```

## ⚙️ Параметры диаризации

### Основные параметры

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `--min_speaker_segment` | 1.5 | Минимальная длительность сегмента (сек) |
| `--max_speakers` | 10 | Максимальное количество говорящих |
| `--min_speakers` | 1 | Минимальное количество говорящих |

### Примеры настройки

#### Для интервью (2 говорящих)
```cmd
--min_speaker_segment 2.0 \
--max_speakers 2 \
--min_speakers 2
```

#### Для лекции (1 говорящий)
```cmd
--min_speaker_segment 1.0 \
--max_speakers 1 \
--min_speakers 1
```

#### Для совещания (много говорящих)
```cmd
--min_speaker_segment 1.5 \
--max_speakers 8 \
--min_speakers 3
```

## 🔍 Анализ результатов

### Проверка качества диаризации
```cmd
# Просмотр RTTM файла
type results\temp\diarized\audio_diarized.rttm

# Просмотр отчета
type results\temp\diarized\audio_diarized.txt
```

### Визуализация результатов
```cmd
# Создание временной шкалы
python -c "
import re
from datetime import datetime, timedelta

def parse_rttm(filename):
    speakers = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 7:
                speaker = parts[7]
                start = float(parts[3])
                duration = float(parts[4])
                end = start + duration
                
                if speaker not in speakers:
                    speakers[speaker] = []
                speakers[speaker].append((start, end))
    
    return speakers

# Парсим RTTM файл
speakers = parse_rttm('results/temp/diarized/audio_diarized.rttm')

print('=== Временная шкала говорящих ===')
for speaker, segments in speakers.items():
    print(f'\n{speaker}:')
    for start, end in segments:
        start_time = str(timedelta(seconds=int(start)))
        end_time = str(timedelta(seconds=int(end)))
        print(f'  {start_time} - {end_time}')
"
```

## ⚠️ Устранение неполадок

### Ошибка "Invalid user token"
```cmd
# Переустановите токен
setup_diarization.bat
```

### Ошибка "Model not found"
```cmd
# Примите условия использования
# Перейдите на https://huggingface.co/pyannote/speaker-diarization-3.1
# Нажмите "Accept"
```

### Плохое качество диаризации
```cmd
# Улучшите качество аудио
--steps split,denoise,vad,diar

# Настройте параметры
--min_speaker_segment 2.0 \
--max_speakers 3
```

### Медленная диаризация
```cmd
# Используйте GPU
--use_gpu

# Уменьшите размер частей
--chunk_duration 300
```

## 📈 Оптимизация производительности

### Для GPU
```cmd
# Оптимальные настройки для RTX 5080
--workers 4 \
--chunk_duration 600 \
--use_gpu \
--parallel
```

### Для CPU
```cmd
# Оптимальные настройки для CPU
--workers 2 \
--chunk_duration 300 \
--use_gpu False
```

## 🎯 Лучшие практики

### Подготовка аудио
- **Качество записи**: Минимум 16kHz, 16-bit
- **Шумоподавление**: Используйте этап `denoise`
- **Удаление тишины**: Используйте этап `vad`

### Настройка параметров
- **Короткие сегменты**: Уменьшите `min_speaker_segment`
- **Длинные сегменты**: Увеличьте `min_speaker_segment`
- **Много говорящих**: Увеличьте `max_speakers`

### Обработка результатов
- **Проверьте RTTM файл** на предмет ошибок
- **Анализируйте отчет** для понимания структуры
- **Визуализируйте результаты** для лучшего понимания

## 📋 Проверочный список

После настройки диаризации:

- [ ] Токен HuggingFace создан и сохранен
- [ ] Условия использования моделей приняты
- [ ] Тест диаризации проходит успешно
- [ ] RTTM файлы создаются корректно
- [ ] Отчеты содержат правильную информацию

## 🔗 Связанные руководства

- **[Основное руководство](MAIN_GUIDE.md)** - Полная установка системы
- **[Руководство по использованию](USAGE_GUIDE.md)** - Все параметры команд
- **[Быстрое исправление](TROUBLESHOOTING.md)** - Решения проблем
- **[Оптимизированная версия](OPTIMIZED_GUIDE.md)** - Настройки производительности 