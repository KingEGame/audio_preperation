@echo off
echo ========================================
echo SIMPLIFIED AUDIO PROCESSING INTERFACE
echo ========================================
echo.
echo This script will simplify the audio processing to 2 modes:
echo 1. Single-threaded (stable, slower)
echo 2. Multi-threaded (fast, recommended)
echo.
echo All parameters are pre-configured for optimal performance.
echo.

set /p choice="Choose mode (1=single, 2=multithreaded, default=2): "
if "%choice%"=="" set choice=2
if "%choice%"=="1" set mode=single
if "%choice%"=="2" set mode=multithreaded

echo.
echo Mode selected: %mode%
echo.

set /p input="Enter input file or folder: "
set /p output="Enter output folder: "

echo.
echo Starting processing with %mode% mode...
echo Input: %input%
echo Output: %output%
echo.

if "%input%"=="" (
    echo ERROR: Input file/folder is required!
    echo Please run the script again and provide input.
    pause
    exit /b 1
)

if "%output%"=="" (
    echo ERROR: Output folder is required!
    echo Please run the script again and provide output.
    pause
    exit /b 1
)

python system\scripts\audio_processing.py --input "%input%" --output "%output%" --mode %mode%

echo.
echo Processing completed!
pause 