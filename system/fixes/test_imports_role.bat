@echo off
chcp 65001 >nul
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
call ..\instructions\activate_environment.bat

echo.
echo ========================================
echo ТЕСТ ИМПОРТОВ РАЗДЕЛЕНИЯ НА РОЛИ
echo ========================================
echo.

:: Запускаем тест импортов
python ..\tests\test_imports_role.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ ИМПОРТЫ РАБОТАЮТ КОРРЕКТНО!
    echo ========================================
    echo.
    echo Теперь можно запускать тест разделения на роли:
    echo   test_role_classification.bat
) else (
    echo.
    echo ========================================
    echo ❌ ПРОБЛЕМЫ С ИМПОРТАМИ
    echo ========================================
    echo.
    echo Проверьте:
    echo   1. Установлены ли все зависимости
    echo   2. Настроен ли токен диаризации
    echo   3. Правильность путей к модулям
    echo.
    echo Для настройки диаризации:
    echo   setup_diarization.bat
)

echo.
pause 