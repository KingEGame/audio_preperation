# 📦 Управление зависимостями - Audio Processing Pipeline

Руководство по установке и управлению зависимостями системы обработки аудио.

## 📋 Категории зависимостей

### 1. Основные зависимости (Обязательные)
Эти пакеты необходимы для базовой функциональности:

#### PyTorch экосистема
- **torch>=2.0.0** - Фреймворк глубокого обучения
- **torchaudio>=2.0.0** - Обработка аудио для PyTorch
- **numpy>=1.25.2** - Численные вычисления
- **scipy>=1.11.4** - Научные вычисления

#### Обработка аудио
- **librosa>=0.10.1** - Библиотека анализа аудио
- **soundfile>=0.12.1** - Ввод/вывод аудио файлов
- **ffmpeg-python>=0.2.0** - Обертка для FFmpeg
- **pydub>=0.25.1** - Манипуляции с аудио
- **audioread>=3.0.0** - Чтение аудио файлов

#### Мониторинг системы
- **psutil>=5.9.0** - Мониторинг системы и процессов
- **tqdm>=4.66.1** - Индикаторы прогресса
- **requests>=2.31.0** - HTTP библиотека
- **urllib3>=1.26.0** - HTTP клиент

### 2. Продвинутые функции (Опциональные)
Эти пакеты обеспечивают продвинутые возможности обработки:

#### Распознавание речи
- **openai-whisper>=20231117** - Распознавание и транскрипция речи
- **transformers>=4.30.0** - Библиотека HuggingFace transformers

#### Улучшение аудио
- **demucs>=4.0.1** - Разделение источников аудио (удаление шума)

#### Обнаружение голосовой активности
- **silero-vad>=5.1.2** - Обнаружение голосовой активности

#### Диаризация говорящих
- **pyannote.audio>=3.0.0,<4.0.0** - Диаризация говорящих
- **sentencepiece>=0.1.97,<0.2.0** - Токенизация текста
- **speechbrain>=1.0.0,<2.0.0** - Набор инструментов для обработки речи

#### Интеграция с HuggingFace
- **huggingface_hub[cli]>=0.19.0** - HuggingFace модель хаб

## 🚀 Варианты установки

### 1. Полная установка (Рекомендуется)
Включает все функции с последними версиями:
```bash
system\instructions\install_dependencies_choice.bat
# Выберите опцию 1
```

**Включаемые функции:**
- Полный конвейер обработки аудио
- Распознавание речи с Whisper
- Удаление шума с Demucs
- Диаризация говорящих с PyAnnote
- Продвинутое управление памятью GPU
- Все функции оптимизации

### 2. Альтернативная установка
Консервативные версии для лучшей совместимости:
```bash
system\instructions\install_dependencies_choice.bat
# Выберите опцию 2
```

**Используйте когда:**
- У вас есть проблемы совместимости с последними версиями
- Ваша система имеет старые версии Python/CUDA
- Вы испытываете ошибки установки с полной версией

### 3. Минимальная установка
Только базовая функциональность:
```bash
system\instructions\install_dependencies_choice.bat
# Выберите опцию 3
```

**Включаемые функции:**
- Базовая обработка аудио
- Обнаружение голосовой активности
- Основные утилиты
- Управление памятью GPU

**НЕ включаемые функции:**
- Распознавание речи (Whisper)
- Удаление шума (Demucs)
- Диаризация говорящих (PyAnnote)

### 4. Пользовательская установка
Выберите конкретные функции:
```bash
system\instructions\install_dependencies_choice.bat
# Выберите опцию 4
```

**Опции:**
1. Установить только Whisper
2. Установить только Demucs
3. Установить только PyAnnote
4. Установить все опциональные функции

## 🔧 Ручная установка

### Использование pip напрямую:
```bash
# Сначала активируйте окружение
call audio_environment\Scripts\activate.bat

# Установите из конкретного файла requirements
pip install -r system\requirements\requirements.txt
```

### Установка отдельных пакетов:
```bash
# Основные зависимости
pip install torch torchaudio numpy scipy

# Обработка аудио
pip install librosa soundfile ffmpeg-python pydub audioread

# Мониторинг системы
pip install psutil tqdm requests urllib3

# Опционально: Продвинутые функции
pip install openai-whisper demucs silero-vad
pip install pyannote.audio sentencepiece speechbrain
pip install huggingface_hub[cli] transformers
```

## 🔄 Совместимость версий

### Версии PyTorch
- **CUDA 12.1**: `torch>=2.0.0` (рекомендуется)
- **CUDA 11.8**: `torch>=1.13.0,<2.1.0` (альтернатива)
- **Только CPU**: `torch>=2.0.0` (без CUDA)

### Версии Python
- **Python 3.8-3.11**: Полная поддержка
- **Python 3.12**: Ограниченная поддержка (используйте альтернативные версии)

### Операционные системы
- **Windows 10/11**: Полная поддержка
- **Linux**: Ограниченное тестирование
- **macOS**: Ограниченное тестирование

## 🛠️ Устранение неполадок

### Частые проблемы установки

#### Ошибка установки PyTorch
```bash
# Попробуйте альтернативную версию CUDA
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Или версию только для CPU
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Проблемы установки Demucs
```bash
# Установите с конкретной версией
pip install demucs==4.0.1

# Или попробуйте альтернативную версию
pip install demucs==3.0.0
```

#### Проблемы установки PyAnnote
```bash
# Установите с конкретными ограничениями
pip install pyannote.audio==3.0.0
pip install sentencepiece==0.1.97
pip install speechbrain==1.0.0
```

#### Проблемы с памятью во время установки
```bash
# Используйте меньший размер батча
pip install --no-cache-dir -r requirements.txt

# Или устанавливайте пакеты по одному
pip install torch
pip install torchaudio
# ... продолжите с другими пакетами
```

### Конфликты зависимостей

#### Конфликты версий
```bash
# Проверьте конфликты
pip check

# Установите совместимые версии
pip install --upgrade pip
pip install -r system\requirements\requirements_alternative.txt
```

#### Проблемы с NumPy
```bash
# Переустановите NumPy
pip uninstall numpy -y
pip install numpy==1.25.2
```

## 📊 Файлы зависимостей

### requirements.txt (Полная установка)
```txt
# Основные зависимости
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.25.2
scipy>=1.11.4

# Обработка аудио
librosa>=0.10.1
soundfile>=0.12.1
ffmpeg-python>=0.2.0
pydub>=0.25.1
audioread>=3.0.0

# Продвинутые функции
openai-whisper>=20231117
demucs>=4.0.1
silero-vad>=5.1.2
pyannote.audio>=3.0.0,<4.0.0
transformers>=4.30.0
huggingface_hub[cli]>=0.19.0
```

### requirements_alternative.txt (Альтернативные версии)
```txt
# Консервативные версии для совместимости
torch>=1.13.0,<2.1.0
torchaudio>=1.13.0,<2.1.0
numpy>=1.21.0,<1.26.0
scipy>=1.9.0,<1.12.0

# Обработка аудио
librosa>=0.9.0,<0.11.0
soundfile>=0.10.0,<0.13.0
ffmpeg-python>=0.2.0
pydub>=0.25.1
audioread>=3.0.0

# Продвинутые функции (стабильные версии)
openai-whisper>=20231117
demucs>=3.0.0,<4.1.0
silero-vad>=5.1.2
pyannote.audio>=3.0.0,<4.0.0
transformers>=4.30.0,<4.35.0
huggingface_hub[cli]>=0.19.0
```

### requirements_minimal.txt (Минимальная установка)
```txt
# Только основные зависимости
torch>=2.0.0
torchaudio>=2.0.0
numpy>=1.25.2
scipy>=1.11.4

# Обработка аудио
librosa>=0.10.1
soundfile>=0.12.1
ffmpeg-python>=0.2.0
pydub>=0.25.1
audioread>=3.0.0

# Мониторинг системы
psutil>=5.9.0
tqdm>=4.66.1
requests>=2.31.0
urllib3>=1.26.0
```

## 🔄 Обновление зависимостей

### Автоматическое обновление
```bash
# Обновите все пакеты
pip install --upgrade -r system\requirements\requirements.txt

# Или используйте системный скрипт
system\instructions\install_optimized_dependencies.bat
```

### Ручное обновление
```bash
# Обновите конкретные пакеты
pip install --upgrade torch torchaudio
pip install --upgrade demucs
pip install --upgrade openai-whisper
```

### Проверка обновлений
```bash
# Проверьте доступные обновления
pip list --outdated

# Проверьте совместимость
pip check
```

## 📋 Проверочный список

После установки зависимостей проверьте:

- [ ] PyTorch работает: `python -c "import torch; print(torch.__version__)"`
- [ ] CUDA доступен: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Обработка аудио: `python -c "import librosa, soundfile"`
- [ ] Whisper (если установлен): `python -c "import whisper"`
- [ ] Demucs (если установлен): `python -c "import demucs"`
- [ ] PyAnnote (если установлен): `python -c "import pyannote.audio"`

## 📚 Следующие шаги

После установки зависимостей:

1. **[Быстрый старт](02-QUICK_START.md)** - Проверьте работу системы
2. **[Примеры использования](03-EXAMPLES.md)** - Попробуйте обработку
3. **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройте производительность
4. **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем

## 🔗 Связанные руководства

- **[Установка и настройка](01-INSTALLATION.md)** - Полная установка системы
- **[Установка PyTorch](07-PYTORCH.md)** - Настройка CUDA и GPU
- **[Оптимизация производительности](06-PERFORMANCE.md)** - Настройки производительности
- **[Устранение неполадок](10-TROUBLESHOOTING.md)** - Решения проблем с зависимостями 