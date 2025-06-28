@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
set "CONDA_ROOT_PREFIX=%cd%\..\..\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\..\..\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo ERROR: Conda not found! Run setup.bat first.
    pause
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo ERROR: Environment not found! Run setup.bat first.
    pause
    exit /b 1
)

:: Set conda environment variables
set "CONDA_PREFIX=!INSTALL_ENV_DIR!"
set "CONDA_DEFAULT_ENV=audio_env"
set "CONDA_PROMPT_MODIFIER=(audio_env) "

:: Add conda to PATH
set "PATH=!CONDA_ROOT_PREFIX!\Scripts;!CONDA_ROOT_PREFIX!\Library\bin;!CONDA_ROOT_PREFIX!\condabin;!PATH!"

:: Activate the environment
call "!CONDA_ROOT_PREFIX!\condabin\conda.bat" activate "!INSTALL_ENV_DIR!" || (
    echo ERROR: Failed to activate environment!
    pause
    exit /b 1
)

echo.
echo ========================================
echo FFMPEG ISSUES DIAGNOSTICS AND FIXES
echo ========================================
echo.

:: Check if audio file is provided
if "%~1"=="" (
    echo Running general FFmpeg diagnostics...
    python "!CONDA_PREFIX!\Scripts\fix_ffmpeg_issues.py"
) else (
    echo Testing specific audio file: %~1
    python "!CONDA_PREFIX!\Scripts\fix_ffmpeg_issues.py" "%~1"
)

echo.
echo ========================================
echo DIAGNOSTICS COMPLETED
echo ========================================
echo.
echo If issues were found, try the following:
echo.
echo 1. Reinstall FFmpeg:
echo    system\instructions\download_ffmpeg.bat
echo.
echo 2. Try processing with fewer stages:
echo    python audio_processing.py --steps split denoise
echo.
echo 3. Use smaller chunks:
echo    python audio_processing.py --chunk_duration 300
echo.
echo 4. Skip problematic stages:
echo    python audio_processing.py --steps split
echo.
pause 