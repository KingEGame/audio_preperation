@echo off
echo ========================================
echo Audio Processing Pipeline - Dependencies Installation
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\..\audio_environment" (
    echo ERROR: Virtual environment not found!
    echo Please run install_environment.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "..\..\audio_environment\Scripts\activate.bat"

echo.
echo Choose installation type:
echo.
echo 1. Full installation (recommended) - All features
echo 2. Alternative installation - Conservative versions for compatibility
echo 3. Minimal installation - Basic features only
echo 4. Custom installation - Choose specific features
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Installing full dependencies...
    pip install -r "..\requirements\requirements.txt"
    set requirements_file=requirements.txt
    set install_type=Full
) else if "%choice%"=="2" (
    echo.
    echo Installing alternative dependencies...
    pip install -r "..\requirements\requirements_alternative.txt"
    set requirements_file=requirements_alternative.txt
    set install_type=Alternative
) else if "%choice%"=="3" (
    echo.
    echo Installing minimal dependencies...
    pip install -r "..\requirements\requirements_minimal.txt"
    set requirements_file=requirements_minimal.txt
    set install_type=Minimal
) else if "%choice%"=="4" (
    echo.
    echo Custom installation options:
    echo.
    echo 1. Install Whisper (speech recognition)
    echo 2. Install Demucs (noise removal)
    echo 3. Install PyAnnote (speaker diarization)
    echo 4. Install all optional features
    echo.
    set /p custom_choice="Enter your choice (1-4): "
    
    if "%custom_choice%"=="1" (
        echo Installing Whisper...
        pip install openai-whisper>=20231117
    ) else if "%custom_choice%"=="2" (
        echo Installing Demucs...
        pip install demucs>=4.0.1
    ) else if "%custom_choice%"=="3" (
        echo Installing PyAnnote...
        pip install pyannote.audio>=3.0.0,<4.0.0
        pip install sentencepiece>=0.1.97,<0.2.0
        pip install speechbrain>=1.0.0,<2.0.0
    ) else if "%custom_choice%"=="4" (
        echo Installing all optional features...
        pip install openai-whisper>=20231117
        pip install demucs>=4.0.1
        pip install huggingface_hub[cli]>=0.19.0
        pip install transformers>=4.30.0
        pip install pyannote.audio>=3.0.0,<4.0.0
        pip install sentencepiece>=0.1.97,<0.2.0
        pip install speechbrain>=1.0.0,<2.0.0
    ) else (
        echo Invalid choice for custom installation
        pause
        exit /b 1
    )
    set install_type=Custom
) else (
    echo Invalid choice
    pause
    exit /b 1
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Dependencies installed successfully
) else (
    echo.
    echo ✗ Failed to install dependencies
    echo.
    echo Troubleshooting tips:
    echo 1. Try alternative installation (option 2)
    echo 2. Check internet connection
    echo 3. Update pip: python -m pip install --upgrade pip
    echo 4. Clear pip cache: pip cache purge
    pause
    exit /b 1
)

REM Verify critical dependencies
echo.
echo Verifying critical dependencies...
python -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
python -c "import torchaudio; print(f'✓ TorchAudio {torchaudio.__version__}')"
python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')"
python -c "import psutil; print(f'✓ psutil {psutil.__version__}')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo %install_type% INSTALLATION COMPLETED
    echo ========================================
    echo.
    echo Critical dependencies verified successfully!
    echo.
    if "%install_type%"=="Full" (
        echo Full installation includes:
        echo - Audio processing (Whisper, Demucs, Silero VAD)
        echo - Speaker diarization (PyAnnote)
        echo - Advanced GPU memory management
        echo - All optimization features
    ) else if "%install_type%"=="Alternative" (
        echo Alternative installation includes:
        echo - Conservative versions for better compatibility
        echo - All features with older, stable versions
    ) else if "%install_type%"=="Minimal" (
        echo Minimal installation includes:
        echo - Basic audio processing
        echo - Voice activity detection
        echo - Core utilities
        echo.
        echo Note: Advanced features (Whisper, Demucs, PyAnnote) are not installed
        echo You can install them later using custom installation
    ) else (
        echo Custom installation completed with selected features
    )
    echo.
    echo You can now use the audio processing pipeline!
    echo.
    echo For more information, see: system\guides\MAIN_GUIDE.md
) else (
    echo.
    echo ✗ Dependency verification failed
    echo Some critical dependencies may not be installed correctly
    pause
    exit /b 1
)

pause 