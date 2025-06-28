@echo off
chcp 65001 >nul
echo ========================================
echo УСТАНОВКА ЗАВИСИМОСТЕЙ ДЛЯ ОПТИМИЗИРОВАННОЙ ВЕРСИИ
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

echo ✓ Python найден
python --version

REM Проверяем наличие pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: pip не найден!
    pause
    exit /b 1
)

echo ✓ pip найден
echo.

REM Обновляем pip
echo Обновление pip...
python -m pip install --upgrade pip --quiet

REM Устанавливаем основные зависимости PyTorch с CUDA
echo.
echo ========================================
echo УСТАНОВКА PYTORCH С CUDA ПОДДЕРЖКОЙ
echo ========================================
echo Установка PyTorch для RTX 5080...

REM Проверяем версию CUDA
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: NVIDIA GPU не найден
    echo Устанавливаем CPU версию PyTorch
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
) else (
    echo ✓ NVIDIA GPU обнаружен
    echo Устанавливаем CUDA версию PyTorch...
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --quiet
)

echo ✓ PyTorch установлен
echo.

REM Устанавливаем основные библиотеки для аудио-обработки
echo ========================================
echo УСТАНОВКА БИБЛИОТЕК АУДИО-ОБРАБОТКИ
echo ========================================

echo Установка Demucs (шумоподавление)...
pip install demucs --quiet
echo ✓ Demucs установлен

echo Установка Whisper (транскрипция)...
pip install openai-whisper --quiet
echo ✓ Whisper установлен

echo Установка Silero VAD (удаление тишины)...
pip install silero-vad==5.1.2 --quiet
echo ✓ Silero VAD установлен

echo Установка PyAnnote (диаризация)...
pip install pyannote.audio --quiet
echo ✓ PyAnnote установлен

echo.

REM Устанавливаем дополнительные зависимости для оптимизации
echo ========================================
echo УСТАНОВКА ДОПОЛНИТЕЛЬНЫХ ЗАВИСИМОСТЕЙ
echo ========================================

echo Установка psutil (мониторинг системы)...
pip install psutil --quiet
echo ✓ psutil установлен

echo Установка GPUtil (мониторинг GPU)...
pip install GPUtil --quiet
echo ✓ GPUtil установлен

echo Установка tqdm (прогресс-бары)...
pip install tqdm --quiet
echo ✓ tqdm установлен

echo Установка huggingface_hub (для моделей)...
pip install huggingface_hub --quiet
echo ✓ huggingface_hub установлен

echo Установка ffmpeg-python (для аудио)...
pip install ffmpeg-python --quiet
echo ✓ ffmpeg-python установлен

echo.

REM Проверяем установку
echo ========================================
echo ПРОВЕРКА УСТАНОВКИ
echo ========================================

echo Проверка PyTorch...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA доступен: {torch.cuda.is_available()}'); print(f'CUDA версия: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo Проверка других библиотек...
python -c "import demucs; print('✓ Demucs работает')" 2>nul || echo "✗ Проблема с Demucs"
python -c "import whisper; print('✓ Whisper работает')" 2>nul || echo "✗ Проблема с Whisper"
python -c "import silero_vad; print('✓ Silero VAD работает')" 2>nul || echo "✗ Проблема с Silero VAD"
python -c "import psutil; print('✓ psutil работает')" 2>nul || echo "✗ Проблема с psutil"
python -c "import GPUtil; print('✓ GPUtil работает')" 2>nul || echo "✗ Проблема с GPUtil"

echo.

REM Проверяем GPU
echo ========================================
echo ПРОВЕРКА GPU
echo ========================================

if torch.cuda.is_available() (
    echo ✓ CUDA доступен
    python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'Память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')"
) else (
    echo ⚠ CUDA недоступен - обработка будет на CPU
)

echo.

REM Создаем тестовый скрипт
echo ========================================
echo СОЗДАНИЕ ТЕСТОВОГО СКРИПТА
echo ========================================

echo Создание test_optimized_setup.py...
(
echo import torch
echo import demucs
echo import whisper
echo import silero_vad
echo import psutil
echo import GPUtil
echo.
echo print\("=== ТЕСТ ОПТИМИЗИРОВАННОЙ УСТАНОВКИ ==="\)
echo print\(f"PyTorch: {torch.__version__}"\)
echo print\(f"CUDA доступен: {torch.cuda.is_available\(\)}"\)
echo if torch.cuda.is_available\(\):
echo     print\(f"GPU: {torch.cuda.get_device_name\(0\)}"\)
echo     print\(f"Память GPU: {torch.cuda.get_device_properties\(0\).total_memory / 1024**3:.1f} GB"\)
echo.
echo print\(f"CPU ядер: {psutil.cpu_count\(\)}"\)
echo print\(f"RAM: {psutil.virtual_memory\(\).total / 1024**3:.1f} GB"\)
echo.
echo print\("Все библиотеки установлены успешно!"\)
) > test_optimized_setup.py

echo ✓ Тестовый скрипт создан

echo.
echo ========================================
echo УСТАНОВКА ЗАВЕРШЕНА
echo ========================================
echo.
echo Для проверки установки запустите:
echo   python test_optimized_setup.py
echo.
echo Для запуска оптимизированной обработки:
echo   run_optimized_processing.bat
echo.
echo Документация: README_OPTIMIZED.md
echo.

pause 