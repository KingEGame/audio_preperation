@echo off
chcp 65001 >nul
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
call ..\instructions\activate_environment.bat

echo.
echo ========================================
echo РАЗДЕЛЕНИЕ АУДИОКНИГИ НА РОЛИ
echo ========================================
echo.
echo Этот скрипт разделяет аудиокнигу на роли:
echo   - Нарратор (самая длинная роль)
echo   - Персонажи (остальные роли)
echo.

:: Проверяем аргументы
if "%~1"=="" (
    echo ❌ Не указан входной файл!
    echo.
    echo Использование:
    echo   run_role_classification.bat "путь_к_файлу.mp3" [папка_результатов]
    echo.
    echo Примеры:
    echo   run_role_classification.bat "audiobook.mp3"
    echo   run_role_classification.bat "audiobook.mp3" "results"
    echo.
    pause
    exit /b 1
)

set INPUT_FILE=%~1
set OUTPUT_DIR=%~2

if "%OUTPUT_DIR%"=="" (
    set OUTPUT_DIR=roles_output
)

:: Проверяем существование входного файла
if not exist "%INPUT_FILE%" (
    echo ❌ Входной файл не найден: %INPUT_FILE%
    pause
    exit /b 1
)

echo ✓ Входной файл: %INPUT_FILE%
echo ✓ Папка результатов: %OUTPUT_DIR%
echo.

:: Создаем папку результатов
if not exist "%OUTPUT_DIR%" (
    echo Создаем папку результатов...
    mkdir "%OUTPUT_DIR%"
)

echo.
echo ========================================
echo ЗАПУСК РАЗДЕЛЕНИЯ НА РОЛИ
echo ========================================
echo.
echo Обработка может занять значительное время
echo в зависимости от размера файла.
echo.

:: Создаем временный Python скрипт
echo import sys > temp_role_processing.py
echo import os >> temp_role_processing.py
echo from pathlib import Path >> temp_role_processing.py
echo sys.path.append(str(Path(__file__).parent.parent / 'scripts')) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo from audio.stages import diarize_with_role_classification >> temp_role_processing.py
echo from config import get_token, token_exists >> temp_role_processing.py
echo from audio.managers import GPUMemoryManager, ModelManager >> temp_role_processing.py
echo import logging >> temp_role_processing.py
echo. >> temp_role_processing.py
echo # Настройка логирования >> temp_role_processing.py
echo logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s') >> temp_role_processing.py
echo logger = logging.getLogger(__name__) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo # Проверяем токен >> temp_role_processing.py
echo if not token_exists(): >> temp_role_processing.py
echo     print("❌ Токен диаризации не найден. Запустите setup_diarization.bat") >> temp_role_processing.py
echo     sys.exit(1) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo # Инициализируем менеджеры >> temp_role_processing.py
echo gpu_manager = GPUMemoryManager() >> temp_role_processing.py
echo model_manager = ModelManager(gpu_manager) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo try: >> temp_role_processing.py
echo     print("Запуск разделения на роли...") >> temp_role_processing.py
echo     result = diarize_with_role_classification( >> temp_role_processing.py
echo         r"%INPUT_FILE%", >> temp_role_processing.py
echo         r"%OUTPUT_DIR%", >> temp_role_processing.py
echo         min_segment_duration=0.3, >> temp_role_processing.py
echo         model_manager=model_manager, >> temp_role_processing.py
echo         gpu_manager=gpu_manager, >> temp_role_processing.py
echo         logger=logger >> temp_role_processing.py
echo     ) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo     if result and result != [r"%INPUT_FILE%"]: >> temp_role_processing.py
echo         print(f"✅ Создано файлов ролей: {len(result)}") >> temp_role_processing.py
echo         for file_path in result: >> temp_role_processing.py
echo             print(f"  - {Path(file_path).name}") >> temp_role_processing.py
echo     else: >> temp_role_processing.py
echo         print("❌ Разделение на роли не удалось") >> temp_role_processing.py
echo         sys.exit(1) >> temp_role_processing.py
echo. >> temp_role_processing.py
echo finally: >> temp_role_processing.py
echo     model_manager.cleanup_models() >> temp_role_processing.py
echo     gpu_manager.cleanup(force=True) >> temp_role_processing.py

:: Запускаем обработку
python temp_role_processing.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ РАЗДЕЛЕНИЕ НА РОЛИ ЗАВЕРШЕНО!
    echo ========================================
    echo.
    echo Результаты сохранены в папке: %OUTPUT_DIR%
    echo.
    echo Структура результатов:
    echo   - narrator.wav          (все сегменты нарратора)
    echo   - character_01.wav      (все сегменты персонажа 1)
    echo   - character_02.wav      (все сегменты персонажа 2)
    echo   - roles_info.txt        (информация о ролях)
    echo   - metadata_*.txt        (метаданные каждой роли)
    echo.
    echo Каждый файл содержит все сегменты соответствующей роли,
    echo объединенные в хронологическом порядке.
) else (
    echo.
    echo ========================================
    echo ❌ ОБРАБОТКА НЕ УДАЛАСЬ
    echo ========================================
    echo.
    echo Проверьте ошибки выше.
    echo.
    echo Возможные причины:
    echo   - Не установлен токен диаризации
    echo   - Проблемы с зависимостями
    echo   - Недостаточно памяти GPU
    echo   - Проблемы с входным файлом
    echo.
    echo Для настройки диаризации запустите:
    echo   setup_diarization.bat
)

:: Очищаем временный файл
del temp_role_processing.py

echo.
pause 