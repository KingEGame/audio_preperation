# Руководство по миграции

## 🆕 Что изменилось?

Проект был реорганизован для упрощения использования. Вместо множества отдельных файлов теперь используется единая система.

## 📁 Новая структура

```
audio_preperation/
├── setup.bat                    # 🆕 Универсальный установщик
├── README.md                    # 🆕 Единая документация
├── audio_processing.py          # Основной скрипт обработки
├── start_audio_environment.bat  # Активация окружения
├── start_audio_processing.bat   # Запуск обработки
├── scripts/                     # 🆕 Папка со скриптами
│   ├── test_gpu.py
│   └── setup_diarization.py
└── docs/                        # 🆕 Папка для документации
```

## 🔄 Миграция

### Старые файлы → Новые команды

| Старый файл | Новая команда в setup.bat |
|-------------|---------------------------|
| `audio_setup.bat` | Опция 1: Install/Update Environment |
| `setup_diarization.bat` | Опция 2: Setup Diarization |
| `test_gpu.bat` | Опция 3: Test GPU |
| `check_versions.bat` | Опция 4: Check Versions |
| `fix_numpy.bat` | Опция 5: Fix Common Issues |
| `start_audio_environment.bat` | Опция 6: Start Audio Environment |
| `start_audio_processing.bat` | Опция 7: Start Audio Processing |

### Удаленные файлы

Следующие файлы были удалены и их функциональность включена в `setup.bat`:
- `fix_numpy_compatibility.bat`
- `fix_numpy_diarization.bat`
- `install_missing_packages.bat`
- `quick_diarization_setup.bat`
- `DIARIZATION_GUIDE.md`
- `DIARIZATION_SETUP_GUIDE.md`
- `GPU_GUIDE.md`
- `NUMPY_FIX_GUIDE.md`
- `README_AUDIO_PROCESSING.md`

## 🚀 Быстрый старт

1. **Запустите новый установщик:**
   ```cmd
   setup.bat
   ```

2. **Выберите нужную опцию:**
   - 1 - Установка/обновление окружения
   - 2 - Настройка диаризации
   - 3 - Тест GPU
   - 4 - Проверка версий
   - 5 - Исправление проблем
   - 6 - Активация окружения
   - 7 - Запуск обработки
   - 8 - Справка
   - 9 - Удаление окружения

## ✅ Преимущества новой структуры

- **Один файл** вместо множества
- **Единая документация** в README.md
- **Лучшая организация** файлов
- **Упрощенное использование**
- **Меньше путаницы**

## 🔧 Если что-то не работает

1. Запустите `setup.bat` и выберите опцию 5 (Fix Common Issues)
2. Если проблемы остаются, выберите опцию 9 (Delete Environment), затем опцию 1 (Install/Update Environment)
3. Обратитесь к README.md для подробной документации 