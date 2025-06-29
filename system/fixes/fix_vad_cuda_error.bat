@echo off
echo ========================================
echo VAD CUDA ERROR FIX
echo ========================================
echo.

echo The VAD (Voice Activity Detection) is causing CUDA device mismatch errors.
echo This script provides several options to fix this issue:
echo.

echo 1. Test VAD device fix (try to fix the CUDA error)
echo 2. Process without VAD (recommended - stable)
echo 3. Process with VAD enabled (may still have errors)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Testing VAD device fix...
    python system\tests\test_vad_device_fix.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Starting processing without VAD (recommended)...
    python system\scripts\audio_processing.py --interactive
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Starting processing with VAD enabled (may have errors)...
    python system\scripts\audio_processing.py --enable_vad --interactive
    goto end
)

if "%choice%"=="4" (
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