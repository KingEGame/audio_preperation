@echo off
chcp 65001 >nul
echo ========================================
echo ИСПРАВЛЕНИЕ ПРОБЛЕМ С ДИАРИЗАЦИЕЙ
echo ========================================
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
echo.

REM Запускаем скрипт исправления
echo Запуск скрипта исправления диаризации...
python fix_diarization_access.py

if errorlevel 1 (
    echo.
    echo ОШИБКА: Не удалось исправить проблемы с диаризацией
    echo Проверьте логи в файле diarization_fix.log
    pause
    exit /b 1
)

echo.
echo ========================================
echo ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!
echo ========================================
echo Теперь диаризация должна работать корректно
echo.
pause 