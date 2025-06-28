@echo off
chcp 65001 >nul
title Универсальный Audio Processing Pipeline

echo.
echo ========================================
echo УНИВЕРСАЛЬНЫЙ AUDIO PROCESSING PIPELINE
echo ========================================
echo.

echo Выберите режим обработки:
echo 1. Safe Mode (Безопасный - медленно, стабильно)
echo 2. Optimized Mode (Оптимизированный - по умолчанию)
echo 3. Ultra-Optimized Mode (Ультра-оптимизированный - быстро)
echo.

set /p mode_choice="Введите номер режима (1-3, по умолчанию 2): "

if "%mode_choice%"=="1" (
    set MODE=safe
    echo Выбран Safe Mode
) else if "%mode_choice%"=="3" (
    set MODE=ultra_optimized
    echo Выбран Ultra-Optimized Mode
) else (
    set MODE=optimized
    echo Выбран Optimized Mode (по умолчанию)
)

echo.
echo Введите путь к аудио файлу или папке:
echo Примеры:
echo   - audio.mp3
echo   - C:\path\to\audio.mp3
echo   - audio_folder
echo   - C:\path\to\audio_folder
echo.

set /p input_path="Введите путь: "

echo.
echo Введите папку для сохранения результатов:
echo Примеры:
echo   - results
echo   - C:\path\to\results
echo.

set /p output_path="Введите путь: "

echo.
echo Дополнительные настройки:
echo.

set /p chunk_duration="Длительность чанка в секундах (по умолчанию авто): "
if "%chunk_duration%"=="" set chunk_duration=

set /p min_segment="Минимальная длительность сегмента спикера в секундах (по умолчанию 1.5): "
if "%min_segment%"=="" set min_segment=1.5

echo.
echo Этапы обработки:
echo 1. split - разделение на части
echo 2. denoise - шумоподавление
echo 3. vad - удаление тишины
echo 4. diar - разделение по спикерам
echo.

set /p steps_choice="Выберите этапы (1-4 через пробел, по умолчанию все): "
if "%steps_choice%"=="" (
    set STEPS=split denoise vad diar
) else (
    set STEPS=
    for %%i in (%steps_choice%) do (
        if "%%i"=="1" set STEPS=!STEPS! split
        if "%%i"=="2" set STEPS=!STEPS! denoise
        if "%%i"=="3" set STEPS=!STEPS! vad
        if "%%i"=="4" set STEPS=!STEPS! diar
    )
)

echo.
echo Метод разделения:
echo 1. simple - простое разделение по времени
echo 2. word_boundary - разделение на границах слов (рекомендуется)
echo.

set /p split_method="Выберите метод (1-2, по умолчанию 2): "
if "%split_method%"=="1" (
    set SPLIT_METHOD=simple
) else (
    set SPLIT_METHOD=word_boundary
)

echo.
echo Параллельная обработка:
echo 1. Да (рекомендуется для нескольких файлов)
echo 2. Нет (для одного файла)
echo.

set /p parallel_choice="Выберите (1-2, по умолчанию 1): "
if "%parallel_choice%"=="2" (
    set PARALLEL=
) else (
    set PARALLEL=--parallel
)

echo.
echo Подробное логирование:
echo 1. Да
echo 2. Нет (по умолчанию)
echo.

set /p verbose_choice="Выберите (1-2, по умолчанию 2): "
if "%verbose_choice%"=="1" (
    set VERBOSE=--verbose
) else (
    set VERBOSE=
)

echo.
echo ========================================
echo ПАРАМЕТРЫ ОБРАБОТКИ
echo ========================================
echo Режим: %MODE%
echo Входной файл/папка: %input_path%
echo Выходная папка: %output_path%
if not "%chunk_duration%"=="" echo Длительность чанка: %chunk_duration% сек
echo Минимальная длительность сегмента: %min_segment% сек
echo Этапы: %STEPS%
echo Метод разделения: %SPLIT_METHOD%
echo Параллельная обработка: %PARALLEL%
echo Подробное логирование: %VERBOSE%
echo.

set /p confirm="Начать обработку? (y/n): "
if /i not "%confirm%"=="y" (
    echo Обработка отменена.
    pause
    exit /b
)

echo.
echo Запуск обработки...
echo.

cd /d "%~dp0"

python audio_processing_universal.py ^
    --input "%input_path%" ^
    --output "%output_path%" ^
    --mode %MODE% ^
    --min_speaker_segment %min_segment% ^
    --steps %STEPS% ^
    --split_method %SPLIT_METHOD% ^
    %PARALLEL% ^
    %VERBOSE%

if "%chunk_duration%"=="" (
    echo.
) else (
    python audio_processing_universal.py ^
        --input "%input_path%" ^
        --output "%output_path%" ^
        --mode %MODE% ^
        --chunk_duration %chunk_duration% ^
        --min_speaker_segment %min_segment% ^
        --steps %STEPS% ^
        --split_method %SPLIT_METHOD% ^
        %PARALLEL% ^
        %VERBOSE%
)

echo.
echo Обработка завершена!
echo Результаты сохранены в: %output_path%
echo.
pause 