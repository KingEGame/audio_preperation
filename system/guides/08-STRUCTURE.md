# 📁 Структура проекта - Audio Processing Pipeline

Детальное описание организации файлов и папок системы обработки аудио.

## 🏗️ Общая организация

```
audio_preperation/
├── README.md                    # Основной README с быстрым стартом
├── setup.bat                    # Главный установщик (модульный)
├── .gitignore                   # Исключения Git
│
├── scripts/                     # Python скрипты
│   ├── audio/                   # Модульная система обработки
│   │   ├── __init__.py          # Инициализация пакета
│   │   ├── config.py            # Конфигурация и настройки
│   │   ├── managers.py          # Менеджеры ресурсов
│   │   ├── processors.py        # Основные процессоры
│   │   ├── stages.py            # Этапы обработки
│   │   ├── splitters.py         # Разбивка аудио
│   │   ├── utils.py             # Утилиты
│   │   └── README.md            # Описание модулей
│   ├── audio_processing.py      # Основной скрипт обработки
│   ├── concatenate_mp3.py       # Объединение MP3 файлов
│   ├── fix_diarization_access.py # Исправление доступа к диаризации
│   ├── setup_diarization.py     # Настройка диаризации
│   ├── test_diarization_token.py # Тест токена диаризации
│   └── test_gpu.py              # Тест GPU
│
├── system/                      # Системные файлы
│   ├── guides/                  # 📚 Документация
│   │   ├── 01-INSTALLATION.md   # Установка и настройка
│   │   ├── 02-QUICK_START.md    # Быстрый старт
│   │   ├── 03-EXAMPLES.md       # Примеры использования
│   │   ├── 04-USAGE.md          # Руководство по использованию
│   │   ├── 05-DIARIZATION.md    # Диаризация говорящих
│   │   ├── 06-PERFORMANCE.md    # Оптимизация производительности
│   │   ├── 07-PYTORCH.md        # Установка PyTorch
│   │   ├── 08-STRUCTURE.md      # Это руководство
│   │   ├── 09-DEPENDENCIES.md   # Управление зависимостями
│   │   ├── 10-TROUBLESHOOTING.md # Устранение неполадок
│   │   ├── 11-FFMPEG_FIXES.md   # Исправление ошибок FFmpeg
│   │   ├── 12-TEMP_MANAGEMENT.md # Управление временными файлами
│   │   ├── 13-DATA_STORAGE.md   # Хранение данных
│   │   ├── 14-TRANSLATION.md    # Перевод руководств
│   │   └── 15-PARALLEL.md       # Параллельная обработка
│   │
│   ├── instructions/            # 🛠️ Модульные bat-файлы
│   │   ├── install_environment.bat    # Установка окружения
│   │   ├── install_pytorch.bat        # Установка PyTorch
│   │   ├── setup_diarization.bat      # Настройка диаризации
│   │   ├── test_gpu.bat               # Тест GPU
│   │   ├── check_versions.bat         # Проверка версий
│   │   ├── fix_common_issues.bat      # Исправление проблем
│   │   ├── fix_ssl_issues.bat         # Исправление SSL
│   │   ├── activate_environment.bat   # Активация окружения
│   │   ├── start_processing.bat       # Запуск обработки
│   │   ├── delete_environment.bat     # Удаление окружения
│   │   ├── download_ffmpeg.bat        # Загрузка ffmpeg
│   │   └── install_ffmpeg_global.bat  # Глобальная установка ffmpeg
│   │
│   ├── fixes/                   # 🔧 Исправления
│   │   ├── fix_diarization_access.bat # Исправление диаризации
│   │   ├── fix_gpu.bat               # Исправление GPU
│   │   ├── fix_ssl_issues.bat        # Исправление SSL
│   │   ├── install_optimized_dependencies.bat # Оптимизированные зависимости
│   │   ├── install_pyannote_fixed.bat # Исправленная установка PyAnnote
│   │   ├── install_without_diarization.bat # Установка без диаризации
│   │   ├── run_optimized_processing.bat # Оптимизированная обработка
│   │   ├── test_diarization_token.bat # Тест токена
│   │   ├── test_parallel_parts.bat    # Тест параллельных частей
│   │   └── test_ssl_fix.bat           # Тест SSL исправления
│   │
│   ├── ffmpeg/                  # 🎬 FFmpeg
│   │   └── ffmpeg-master-latest-win64-gpl/
│   │       └── bin/
│   │           ├── ffmpeg.exe
│   │           ├── ffplay.exe
│   │           └── ffprobe.exe
│   │
│   ├── requirements/            # 📦 Зависимости
│   │   ├── requirements.txt     # Полная установка
│   │   ├── requirements_alternative.txt # Альтернативные версии
│   │   └── requirements_minimal.txt   # Минимальная установка
│   │
│   ├── tests/                   # 🧪 Тесты
│   │   ├── performance_monitor.py # Мониторинг производительности
│   │   ├── test_parallel_parts.py  # Тест параллельной обработки
│   │   └── test_diarization_results/ # Результаты тестов диаризации
│   │
│   └── docs/                    # 📖 Дополнительная документация
│       └── MIGRATION_GUIDE.md   # Руководство по миграции
│
├── audio_environment/           # 🐍 Conda окружение
├── fixes/                       # 🔧 Исправления (корневой уровень)
├── docs/                        # 📖 Документация (корневой уровень)
└── concatenate_mp3.bat          # Объединение MP3 (корневой уровень)
```

## 🎯 Назначение папок

### 📚 `system/guides/` - Документация
- **01-INSTALLATION.md** - Установка и настройка системы
- **02-QUICK_START.md** - Быстрый старт для новичков
- **03-EXAMPLES.md** - Практические примеры использования
- **04-USAGE.md** - Все команды и параметры
- **05-DIARIZATION.md** - Настройка диаризации говорящих
- **06-PERFORMANCE.md** - Оптимизация производительности
- **07-PYTORCH.md** - Установка PyTorch с CUDA
- **08-STRUCTURE.md** - Это руководство
- **09-DEPENDENCIES.md** - Управление зависимостями
- **10-TROUBLESHOOTING.md** - Решения проблем
- **11-FFMPEG_FIXES.md** - Исправление ошибок FFmpeg
- **12-TEMP_MANAGEMENT.md** - Управление временными файлами
- **13-DATA_STORAGE.md** - Рекомендации по хранению данных
- **14-TRANSLATION.md** - Перевод руководств
- **15-PARALLEL.md** - Параллельная обработка

### 🐍 `scripts/audio/` - Модульная система обработки
- **__init__.py** - Инициализация пакета, экспорт основных функций
- **config.py** - Конфигурационные константы и функции настройки
- **managers.py** - Менеджеры для управления ресурсами (GPU, модели)
- **processors.py** - Основные процессоры обработки аудио
- **stages.py** - Функции для отдельных этапов обработки
- **splitters.py** - Функции разбивки аудио на части
- **utils.py** - Утилиты и вспомогательные функции
- **README.md** - Описание модульной структуры

### 🛠️ `system/instructions/` - Модульные bat-файлы
- **install_environment.bat** - Основная установка
- **install_pytorch.bat** - Установка PyTorch с выбором CUDA
- **setup_diarization.bat** - Настройка диаризации
- **test_gpu.bat** - Проверка GPU
- **check_versions.bat** - Проверка версий
- **fix_common_issues.bat** - Исправление проблем
- **activate_environment.bat** - Активация окружения
- **start_processing.bat** - Запуск обработки
- **delete_environment.bat** - Удаление окружения
- **download_ffmpeg.bat** - Загрузка ffmpeg
- **install_ffmpeg_global.bat** - Глобальная установка ffmpeg

### 🔧 `system/fixes/` - Исправления
- **fix_diarization_access.bat** - Исправление доступа к диаризации
- **fix_gpu.bat** - Исправление проблем с GPU
- **fix_ssl_issues.bat** - Исправление SSL проблем
- **install_optimized_dependencies.bat** - Оптимизированные зависимости
- **install_pyannote_fixed.bat** - Исправленная установка PyAnnote
- **install_without_diarization.bat** - Установка без диаризации
- **run_optimized_processing.bat** - Оптимизированная обработка
- **test_diarization_token.bat** - Тест токена диаризации
- **test_parallel_parts.bat** - Тест параллельных частей
- **test_ssl_fix.bat** - Тест SSL исправления

### 🎬 `system/ffmpeg/` - FFmpeg
- Содержит распакованный FFmpeg для Windows
- Используется локально, если не установлен глобально

### 📦 `system/requirements/` - Зависимости
- **requirements.txt** - Полная установка с последними версиями
- **requirements_alternative.txt** - Альтернативные версии для совместимости
- **requirements_minimal.txt** - Минимальная установка без диаризации

### 🧪 `system/tests/` - Тесты
- **performance_monitor.py** - Мониторинг производительности
- **test_parallel_parts.py** - Тест параллельной обработки
- **test_diarization_results/** - Результаты тестов диаризации

### 🐍 `scripts/` - Python скрипты
- **audio_processing.py** - Основной скрипт обработки (координатор)
- **concatenate_mp3.py** - Объединение MP3 файлов
- **fix_diarization_access.py** - Исправление доступа к диаризации
- **setup_diarization.py** - Настройка диаризации
- **test_diarization_token.py** - Тест токена диаризации
- **test_gpu.py** - Тест GPU

## 🔄 Модульная архитектура

### Принципы организации:
1. **Разделение ответственности** - каждый bat-файл выполняет одну задачу
2. **Переиспользование** - общие функции вынесены в отдельные модули
3. **Простота обновления** - легко обновлять отдельные компоненты
4. **Гибкость** - можно использовать модули независимо

### Преимущества модульной структуры:
- ✅ **Легкое обслуживание** - каждый модуль независим
- ✅ **Простое обновление** - можно обновлять отдельные части
- ✅ **Гибкость использования** - можно запускать модули отдельно
- ✅ **Четкая документация** - каждый модуль имеет свое назначение
- ✅ **Удобное тестирование** - можно тестировать компоненты отдельно

### Модульная система обработки аудио:
- **Читаемость** - код разделен на логические блоки
- **Поддержка** - легче найти и исправить ошибки
- **Расширяемость** - простое добавление новых функций
- **Тестирование** - можно тестировать отдельные модули
- **Переиспользование** - модули можно использовать в других проектах

## 📋 Рекомендации по использованию

### Для новичков:
1. Начните с `setup.bat` (основной установщик)
2. Изучите `system/guides/01-INSTALLATION.md`
3. При проблемах обратитесь к `system/guides/10-TROUBLESHOOTING.md`

### Для продвинутых пользователей:
1. Изучите `system/guides/06-PERFORMANCE.md`
2. Настройте параметры в `system/instructions/`
3. Используйте `system/fixes/` для специфических проблем

### Для разработчиков:
1. Изучите `scripts/audio/` для понимания модульной архитектуры
2. Используйте `system/tests/` для тестирования
3. Обратитесь к `system/guides/15-PARALLEL.md`

## 🔗 Связанные руководства

- **[Установка и настройка](01-INSTALLATION.md)** - Полная установка системы
- **[Быстрый старт](02-QUICK_START.md)** - Первые шаги
- **[Руководство по использованию](04-USAGE.md)** - Все команды и параметры
- **[Оптимизация производительности](06-PERFORMANCE.md)** - Продвинутые настройки
- **[Управление зависимостями](09-DEPENDENCIES.md)** - Детали зависимостей 