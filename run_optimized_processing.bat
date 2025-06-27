@echo off
chcp 65001 >nul
echo ========================================
echo ОПТИМИЗИРОВАННАЯ АУДИО ОБРАБОТКА
echo ========================================
echo Оптимизировано для RTX 5080 + R5 5600X + 32GB RAM
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ и добавьте в PATH
    pause
    exit /b 1
)

REM Проверяем наличие CUDA
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: NVIDIA GPU не найден
    echo Обработка будет выполняться на CPU
    echo.
) else (
    echo ✓ NVIDIA GPU обнаружен
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    echo.
)

REM Устанавливаем зависимости для мониторинга производительности
echo Установка зависимостей для мониторинга...
pip install psutil GPUtil --quiet

REM Запускаем мониторинг производительности в фоне
echo Запуск мониторинга производительности...
start /B python performance_monitor.py

REM Ждем немного для запуска мониторинга
timeout /t 3 /nobreak >nul

REM Запускаем оптимизированную обработку
echo.
echo ========================================
echo ЗАПУСК ОПТИМИЗИРОВАННОЙ ОБРАБОТКИ
echo ========================================
echo.

REM Проверяем аргументы командной строки
if "%1"=="" (
    echo Использование: run_optimized_processing.bat [входной_файл/папка] [выходная_папка]
    echo.
    echo Примеры:
    echo   run_optimized_processing.bat audio.mp3 results
    echo   run_optimized_processing.bat audio_folder results
    echo.
    echo Запуск в интерактивном режиме...
    python audio_processing.py --interactive
) else (
    if "%2"=="" (
        echo ОШИБКА: Не указана выходная папка
        echo Использование: run_optimized_processing.bat [входной_файл/папка] [выходная_папка]
        pause
        exit /b 1
    )
    
    echo Входной файл/папка: %1
    echo Выходная папка: %2
    echo.
    
    REM Запускаем с указанными параметрами
    python audio_processing.py --input "%1" --output "%2" --parallel --use_gpu
)

REM Ждем завершения обработки
echo.
echo Ожидание завершения обработки...
timeout /t 5 /nobreak >nul

REM Останавливаем мониторинг
echo Остановка мониторинга производительности...
taskkill /f /im python.exe >nul 2>&1

echo.
echo ========================================
echo ОБРАБОТКА ЗАВЕРШЕНА
echo ========================================
echo.
echo Результаты мониторинга сохранены в: performance_log.json
echo Лог обработки сохранен в: audio_processing.log
echo.

REM Показываем краткую статистику если есть
if exist "performance_log.json" (
    echo КРАТКАЯ СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:
    python -c "import json; data=json.load(open('performance_log.json')); summary=data.get('summary', {}); print(f'CPU: средняя загрузка {summary.get(\"cpu\", {}).get(\"avg_percent\", 0):.1f}%'); print(f'RAM: среднее использование {summary.get(\"memory\", {}).get(\"avg_percent\", 0):.1f}%'); print(f'GPU: средняя температура {summary.get(\"gpu\", {}).get(\"avg_temperature\", 0):.1f}°C')" 2>nul
)

pause 