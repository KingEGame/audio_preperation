@echo off
chcp 65001 >nul
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
call ..\instructions\activate_environment.bat

echo.
echo ========================================
echo ТЕСТ РАЗДЕЛЕНИЯ НА РОЛИ
echo ========================================
echo.
echo Этот тест проверяет новую функцию разделения
echo аудиокниги на роли (нарратор + персонажи).
echo.

:: Проверяем наличие тестового файла
if not exist "..\tests\test_audio.mp3" (
    echo ❌ Тестовый файл не найден!
    echo.
    echo Поместите тестовый аудиофайл в папку tests/
    echo с именем test_audio.mp3
    echo.
    echo Или укажите путь к файлу:
    set /p TEST_FILE="Путь к аудиофайлу: "
    if "!TEST_FILE!"=="" (
        echo Тест отменен.
        pause
        exit /b 1
    )
) else (
    set TEST_FILE=..\tests\test_audio.mp3
)

echo ✓ Тестовый файл: !TEST_FILE!
echo.

:: Запускаем тест
echo Запуск теста разделения на роли...
echo Это может занять несколько минут...
echo.

python ..\tests\test_role_classification.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ ТЕСТ ПРОЙДЕН УСПЕШНО!
    echo ========================================
    echo.
    echo Функция разделения на роли работает корректно.
    echo Результаты сохранены в папке test_roles_output/
    echo.
    echo Структура результатов:
    echo   - narrator.wav          (все сегменты нарратора)
    echo   - character_01.wav      (все сегменты персонажа 1)
    echo   - character_02.wav      (все сегменты персонажа 2)
    echo   - roles_info.txt        (информация о ролях)
    echo   - metadata_*.txt        (метаданные каждой роли)
) else (
    echo.
    echo ========================================
    echo ❌ ТЕСТ НЕ ПРОЙДЕН
    echo ========================================
    echo.
    echo Проверьте ошибки выше.
    echo.
    echo Возможные причины:
    echo   - Не установлен токен диаризации
    echo   - Проблемы с зависимостями
    echo   - Недостаточно памяти GPU
    echo.
    echo Для настройки диаризации запустите:
    echo   setup_diarization.bat
)

echo.
pause 