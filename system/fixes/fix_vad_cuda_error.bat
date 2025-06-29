@echo off
echo ========================================
echo VAD CUDA ERROR FIX
echo ========================================
echo.

echo The VAD (Voice Activity Detection) has been completely removed
echo to avoid CUDA device mismatch errors.
echo.

echo 1. Process without VAD (recommended - stable)
echo 2. Exit
echo.

set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" (
    echo.
    echo Starting processing without VAD (recommended)...
    python system\scripts\audio_processing.py --interactive
    goto end
)

if "%choice%"=="2" (
    echo Exiting...
    goto end
)

echo Invalid choice. Please try again.
goto end

:end
echo.
echo ========================================
echo Fix completed!
echo ========================================
pause 