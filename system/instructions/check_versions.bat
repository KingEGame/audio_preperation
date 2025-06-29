@echo off
setlocal enabledelayedexpansion

for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "L_BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

echo.
echo    %L_BLUE%PACKAGE VERSIONS%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
    pause
    exit /b 1
)

echo    %L_CYAN%Activating environment...%RESET%
call system\instructions\activate_environment.bat 

echo    %L_GREEN%Versions:%RESET%
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
python -c "import torchaudio; print('torchaudio:', torchaudio.__version__)"
python -c "import whisper; print('Whisper:', whisper.__version__)"
python -c "import demucs; print('Demucs:', demucs.__version__)"
python -c "import silero_vad; print('Silero VAD: working')"
python -c "import librosa; print('Librosa:', librosa.__version__)"
python -c "import soundfile; print('SoundFile:', soundfile.__version__)"
python -c "import pyannote.audio; print('PyAnnote: working')" 2>nul || echo %L_YELLOW%PyAnnote: not installed%RESET%
call system\instructions\test_gpu.bat
echo    %L_GREEN%Version check completed%RESET%
pause 