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

echo ==================================================
echo ИСПРАВЛЕНИЕ GPU/CUDA ПОДДЕРЖКИ
echo ==================================================

:: Check current PyTorch installation
echo Current PyTorch installation:
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

echo.
echo Uninstalling current PyTorch...
pip uninstall torch torchaudio -y

echo.
echo Installing PyTorch with CUDA 12.1 support...
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121 --force-reinstall

echo.
echo Verifying installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo GPU fix completed!
pause 