# 📁 Структура проекта

## 🏗️ Общая организация

```
audio_preperation/
├── README.md                    # Основной README с быстрым стартом
├── setup.bat                    # Главный установщик (модульный)
├── .gitignore                   # Исключения Git
│
├── scripts/                     # Python скрипты
│   ├── audio_processing.py      # Основной скрипт обработки
│   ├── concatenate_mp3.py       # Объединение MP3 файлов
│   ├── fix_diarization_access.py # Исправление доступа к диаризации
│   ├── setup_diarization.py     # Настройка диаризации
│   ├── test_diarization_token.py # Тест токена диаризации
│   └── test_gpu.py              # Тест GPU
│
├── system/                      # Системные файлы
│   ├── guides/                  # 📚 Документация
│   │   ├── README.md            # Главная страница документации
│   │   ├── MAIN_GUIDE.md        # Основное руководство
│   │   ├── OPTIMIZED_GUIDE.md   # Оптимизированная версия
│   │   ├── USAGE_GUIDE.md       # Руководство по использованию
│   │   ├── DIARIZATION.md       # Диаризация говорящих
│   │   ├── PYTORCH_INSTALL.md   # Установка PyTorch
│   │   ├── TROUBLESHOOTING.md   # Быстрое исправление проблем
│   │   ├── PARALLEL_PROCESSING.md # Параллельная обработка
│   │   └── PROJECT_STRUCTURE.md # Это руководство
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
│   │   └── requirements.txt     # Список Python пакетов
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
- **README.md** - Главная страница с навигацией
- **MAIN_GUIDE.md** - Основное руководство для новичков
- **OPTIMIZED_GUIDE.md** - Продвинутые настройки
- **USAGE_GUIDE.md** - Все команды и параметры
- **DIARIZATION.md** - Настройка диаризации
- **PYTORCH_INSTALL.md** - Установка PyTorch с CUDA
- **TROUBLESHOOTING.md** - Решения проблем
- **PARALLEL_PROCESSING.md** - Параллельная обработка
- **PROJECT_STRUCTURE.md** - Это руководство

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
- **requirements.txt** - Список Python пакетов

### 🧪 `system/tests/` - Тесты
- **performance_monitor.py** - Мониторинг производительности
- **test_parallel_parts.py** - Тест параллельной обработки
- **test_diarization_results/** - Результаты тестов диаризации

### 🐍 `scripts/` - Python скрипты
- **audio_processing.py** - Основной скрипт обработки
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

## 📋 Рекомендации по использованию

### Для новичков:
1. Начните с `setup.bat` (основной установщик)
2. Изучите `system/guides/MAIN_GUIDE.md`
3. При проблемах обратитесь к `system/guides/TROUBLESHOOTING.md`

### Для продвинутых пользователей:
1. Изучите `system/guides/OPTIMIZED_GUIDE.md`
2. Настройте параметры в `system/instructions/`
3. Используйте `system/fixes/` для специфических проблем

### Для разработчиков:
1. Изучите `scripts/` для понимания логики
2. Используйте `system/tests/` для тестирования
3. Обратитесь к `system/guides/PARALLEL_PROCESSING.md`

## 🔗 Связанные руководства

- **[Главная страница документации](README.md)** - Навигация по всем руководствам
- **[Основное руководство](MAIN_GUIDE.md)** - Полная установка и настройка
- **[Руководство по использованию](USAGE_GUIDE.md)** - Все команды и параметры
- **[Оптимизированная версия](OPTIMIZED_GUIDE.md)** - Продвинутые настройки 