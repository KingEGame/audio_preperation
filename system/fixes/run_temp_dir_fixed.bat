@echo off
echo ========================================
echo TEMP DIRECTORY FIXED AUDIO PROCESSING
echo ========================================
echo.
echo This version includes fixes for:
echo - Temporary directories created in correct location
echo - No temp files left in source directories
echo - FFmpeg concat errors in speaker creation
echo - Multiple fallback methods for audio processing
echo - Better error handling and recovery
echo.
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if FFmpeg is available
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed or not in PATH
    echo Audio processing may fail without FFmpeg
    echo.
    echo To install FFmpeg:
    echo 1. Download from https://ffmpeg.org/download.html
    echo 2. Add to PATH or place in system/ffmpeg/
    echo.
    pause
)

REM Activate conda environment if available
if exist "audio_environment\Scripts\activate.bat" (
    echo Activating audio environment...
    call audio_environment\Scripts\activate.bat
    echo.
) else (
    echo WARNING: Audio environment not found
    echo Please run setup.bat first to create the environment
    echo.
)

REM Test temp directory fix
echo Testing temp directory fix...
python system\tests\test_temp_dir_fix.py
if errorlevel 1 (
    echo.
    echo WARNING: Temp directory fix test failed
    echo Processing may still work but temporary files might be created in wrong locations
    echo.
    pause
) else (
    echo.
    echo ✓ Temp directory fix test passed
    echo.
)

REM Test FFmpeg fix
echo Testing FFmpeg fix...
python system\tests\test_ffmpeg_fix.py
if errorlevel 1 (
    echo.
    echo WARNING: FFmpeg fix test failed
    echo Processing may still work but with reduced reliability
    echo.
    pause
) else (
    echo.
    echo ✓ FFmpeg fix test passed
    echo.
)

REM Run the main processing script
echo Starting temp directory fixed audio processing...
echo.
python system\scripts\audio_processing.py --interactive

echo.
echo ========================================
echo PROCESSING COMPLETED
echo ========================================
echo.
echo If you encountered any issues:
echo 1. Check the log file: audio_processing.log
echo 2. Run: system\fixes\test_temp_dir_fix.py
echo 3. Run: system\fixes\test_ffmpeg_fix.py
echo 4. Try the stable version: system\fixes\run_stable_processing.bat
echo.
pause 