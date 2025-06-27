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

echo Installing audio processing pipeline without speaker diarization...

:: Install core dependencies
echo Installing core dependencies...
pip install "numpy>=1.25.2,<2.0.0" || (
    echo Failed to install numpy
    pause
    exit /b 1
)

:: Install PyTorch
echo Installing PyTorch...
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121 || (
    echo Failed to install PyTorch
    pause
    exit /b 1
)

:: Install other dependencies (excluding PyAnnote)
echo Installing other dependencies...
pip install scipy>=1.11.4 openai-whisper>=20231117 demucs>=4.0.1 librosa>=0.10.1 soundfile>=0.12.1 ffmpeg-python>=0.2.0 silero-vad>=5.1.2 tqdm>=4.66.1 || (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Installation completed successfully!
echo Note: Speaker diarization (PyAnnote) was not installed due to compilation issues.
echo You can still use all other audio processing features.
pause 