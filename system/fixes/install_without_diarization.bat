@echo off
setlocal enabledelayedexpansion

:: Generate the ESC character
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

:: Colors
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "L_BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

echo.
echo    %L_BLUE%INSTALL WITHOUT DIARIZATION DEPENDENCIES%RESET%
echo    %L_YELLOW%This installs everything except problematic diarization packages%RESET%
echo.

:: Check environment
if not exist "audio_environment\env\python.exe" (
    echo %L_RED%Environment not found! Run setup.bat option 1 first.%RESET%
    pause
    exit /b 1
)

:: Activate environment
echo    %L_CYAN%Activating environment...%RESET%
call system\instructions\activate_environment.bat || (
    echo %L_RED%Failed to activate environment!%RESET%
    pause
    exit /b 1
)

:: Verify we're in the right environment
echo    %L_CYAN%Verifying environment...%RESET%
python -c "import sys; print('Python executable:', sys.executable)"

:: Upgrade pip and setuptools
echo    %L_CYAN%Upgrading pip and setuptools...%RESET%
python -m pip install --upgrade pip setuptools wheel --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

:: Install PyTorch first
echo    %L_CYAN%Installing PyTorch with CUDA support...%RESET%
pip install -r system\requirements\requirements_cu121.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host download.pytorch.org --verbose

:: Verify PyTorch
echo    %L_CYAN%Verifying PyTorch installation...%RESET%
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

:: Install core packages
echo    %L_CYAN%Installing core packages...%RESET%
pip install "numpy>=1.25.2,<2.0.0" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install scipy>=1.11.4 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Install audio processing packages
echo    %L_CYAN%Installing audio processing packages...%RESET%
pip install openai-whisper>=20231117 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install demucs>=4.0.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install librosa>=0.10.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install soundfile>=0.12.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install ffmpeg-python>=0.2.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Install HuggingFace ecosystem
echo    %L_CYAN%Installing HuggingFace ecosystem...%RESET%
pip install "huggingface_hub[cli]>=0.19.0" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install transformers>=4.30.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Install voice activity detection
echo    %L_CYAN%Installing voice activity detection...%RESET%
pip install silero-vad>=5.1.2 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Install utilities
echo    %L_CYAN%Installing utilities...%RESET%
pip install tqdm>=4.66.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install psutil>=5.9.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install requests>=2.31.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install urllib3>=1.26.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Install audio format support
echo    %L_CYAN%Installing audio format support...%RESET%
pip install pydub>=0.25.1 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose
pip install audioread>=3.0.0 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --verbose

:: Verify installations
echo.
echo    %L_CYAN%Verifying installations...%RESET%
python -c "import torch; print('✅ PyTorch:', torch.__version__)" || echo "❌ PyTorch failed"
python -c "import whisper; print('✅ Whisper:', whisper.__version__)" || echo "❌ Whisper failed"
python -c "import demucs; print('✅ Demucs:', demucs.__version__)" || echo "❌ Demucs failed"
python -c "import librosa; print('✅ Librosa:', librosa.__version__)" || echo "❌ Librosa failed"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)" || echo "❌ NumPy failed"
python -c "import scipy; print('✅ SciPy:', scipy.__version__)" || echo "❌ SciPy failed"

:: Show all installed packages
echo.
echo    %L_CYAN%All installed packages:%RESET%
pip list

echo.
echo    %L_GREEN%Installation completed without diarization dependencies!%RESET%
echo    %L_YELLOW%Note: Speaker diarization features will not be available.%RESET%
echo    %L_YELLOW%All other features (Whisper, Demucs, VAD) will work normally.%RESET%
echo.
pause 