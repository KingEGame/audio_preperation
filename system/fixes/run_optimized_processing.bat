@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo ОПТИМИЗИРОВАННЫЙ АУДИО-ПРОЦЕССИНГ ПАЙПЛАЙН
echo ========================================
echo Система: RTX 5080 GPU, 32GB RAM, Ryzen 5600X
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8 или выше
    pause
    exit /b 1
)

echo ✓ Python найден

REM Проверяем CUDA
python -c "import torch; print('CUDA доступен:', torch.cuda.is_available())" 2>nul
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: PyTorch не установлен или CUDA недоступен
    echo Установите PyTorch с CUDA поддержкой
)

REM Проверяем зависимости
echo.
echo Проверка зависимостей...
python -c "import demucs, whisper, torch, torchaudio" 2>nul
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: Некоторые зависимости не установлены
    echo Запустите install_optimized_dependencies.bat для установки
)

REM Создаем папку для логов если её нет
if not exist "logs" mkdir logs

REM Запускаем мониторинг производительности в фоне
echo.
echo Запуск мониторинга производительности...
start /B python performance_monitor.py

REM Ждем немного для запуска мониторинга
timeout /t 3 /nobreak >nul

REM Запускаем оптимизированную обработку
echo.
echo Запуск оптимизированного аудио-процессинг пайплайна...
echo Логи сохраняются в папке logs/
echo.

REM Устанавливаем переменные окружения для стабильности
set "PYTHONUNBUFFERED=1"
set "CUDA_LAUNCH_BLOCKING=1"
set "TORCH_CUDNN_V8_API_ENABLED=1"

REM Запускаем обработку с улучшенной обработкой ошибок
python audio_processing.py ^
    --input "audio" ^
    --output "audio/export" ^
    --chunk-duration 600 ^
    --min-speaker-segment 1.5 ^
    --steps split,denoise,vad,diar ^
    --split-method word_boundary ^
    --use-gpu ^
    --parallel ^
    --workers 4 ^
    --verbose

REM Проверяем результат
if errorlevel 1 (
    echo.
    echo ОШИБКА: Обработка завершилась с ошибками
    echo Проверьте логи в папке logs/
    echo.
    echo Возможные решения:
    echo 1. Запустите fix_diarization_access.bat для исправления диаризации
    echo 2. Уменьшите количество workers до 2
    echo 3. Отключите GPU: уберите --use-gpu
    echo 4. Проверьте свободное место на диске
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo Результаты сохранены в папке audio/export/
echo Логи сохранены в папке logs/
echo.

REM Останавливаем мониторинг
taskkill /f /im python.exe /fi "WINDOWTITLE eq performance_monitor.py" >nul 2>&1

echo Нажмите любую клавишу для завершения...
pause >nul 