@echo off
echo ========================================
echo AUDIO PROCESSING WITHOUT DIARIZATION
echo ========================================
echo.
echo This version skips diarization to avoid:
echo - FFmpeg concat errors
echo - Speaker separation issues
echo - Complex file organization
echo.
echo Processing stages: split, denoise, vad
echo Output: Clean audio files without speaker separation
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

REM Create a temporary script without diarization
echo Creating temporary script without diarization...
(
echo import sys
echo import os
echo from pathlib import Path
echo.
echo # Add audio module path
echo audio_module_path = Path(__file__).parent / 'scripts' / 'audio'
echo sys.path.append(str(audio_module_path^))
echo.
echo # Import and run main function
echo from audio_processing import main
echo.
echo # Override steps to exclude diarization
echo import sys
echo sys.argv.extend(['--steps', 'split', 'denoise', 'vad']^)
echo.
echo if __name__ == "__main__":
echo     main(^)
) > temp_no_diarization.py

REM Run the temporary script
echo Starting audio processing without diarization...
echo.
python temp_no_diarization.py --interactive

REM Clean up
del temp_no_diarization.py

echo.
echo ========================================
echo PROCESSING COMPLETED
echo ========================================
echo.
echo Results: Clean audio files without speaker separation
echo.
echo If you need speaker separation later:
echo 1. Run: system\fixes\run_ffmpeg_fixed.bat
echo 2. Or run: system\fixes\run_stable_processing.bat
echo.
pause 