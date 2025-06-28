@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
set "CONDA_ROOT_PREFIX=%cd%\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\audio_environment\env"

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

echo Installing PyAnnote with conda dependencies...

:: Install sentencepiece via conda (pre-compiled)
echo Installing sentencepiece via conda...
conda install -c conda-forge sentencepiece -y || (
    echo Failed to install sentencepiece via conda
    pause
    exit /b 1
)

:: Install speechbrain
echo Installing speechbrain...
pip install speechbrain || (
    echo Failed to install speechbrain
    pause
    exit /b 1
)

:: Install pyannote.audio
echo Installing pyannote.audio...
pip install pyannote.audio || (
    echo Failed to install pyannote.audio
    pause
    exit /b 1
)

echo PyAnnote installation completed successfully!
pause 