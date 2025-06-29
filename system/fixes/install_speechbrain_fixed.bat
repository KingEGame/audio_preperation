@echo off
echo ========================================
echo SpeechBrain Installation Fix for Windows
echo ========================================
echo.
echo This script will attempt to install SpeechBrain without compilation issues.
echo.

REM Check Python version
python --version
echo.

REM Step 1: Try to find pre-compiled sentencepiece wheels
echo Step 1: Checking for pre-compiled sentencepiece wheels...
pip install --only-binary=all --no-cache-dir sentencepiece
if %errorlevel% equ 0 (
    echo Successfully installed sentencepiece from pre-compiled wheel!
    goto :install_speechbrain
)

echo.
echo Step 2: Trying alternative sentencepiece installation methods...
echo.

REM Try installing from a different source
echo Attempting to install sentencepiece from conda-forge (if conda available)...
conda install -c conda-forge sentencepiece -y
if %errorlevel% equ 0 (
    echo Successfully installed sentencepiece via conda!
    goto :install_speechbrain
)

echo.
echo Step 3: Installing SpeechBrain without sentencepiece dependency...
echo.

REM Install SpeechBrain without dependencies first
echo Installing SpeechBrain core package without dependencies...
pip install --no-deps speechbrain>=1.0.0,<2.0.0
if %errorlevel% neq 0 (
    echo Failed to install SpeechBrain core package.
    goto :manual_install
)

REM Install known compatible dependencies manually
echo Installing SpeechBrain dependencies manually...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install numpy scipy matplotlib
pip install tqdm h5py scikit-learn pandas
pip install librosa soundfile
pip install transformers huggingface_hub
pip install hyperpyyaml torch-optimizer

echo.
echo SpeechBrain installed successfully without sentencepiece!
echo Note: Some SpeechBrain features that require sentencepiece may not work.
echo.
goto :end

:install_speechbrain
echo.
echo Installing SpeechBrain with sentencepiece...
pip install speechbrain>=1.0.0,<2.0.0
if %errorlevel% equ 0 (
    echo.
    echo SpeechBrain installed successfully with sentencepiece!
) else (
    echo.
    echo SpeechBrain installation failed, trying manual approach...
    goto :manual_install
)
goto :end

:manual_install
echo.
echo ========================================
echo Manual Installation Required
echo ========================================
echo.
echo To install SpeechBrain with full functionality, you need to:
echo.
echo 1. Install cmake:
echo    - Download from: https://cmake.org/download/
echo    - Add to PATH during installation
echo.
echo 2. Install Visual Studio Build Tools:
echo    - Download from: https://visualstudio.microsoft.com/downloads/
echo    - Install "C++ build tools" workload
echo.
echo 3. Restart your command prompt and run:
echo    pip install sentencepiece
echo    pip install speechbrain
echo.
echo Alternative: Use conda environment with pre-compiled packages:
echo    conda create -n speechbrain python=3.9
echo    conda activate speechbrain
echo    conda install -c conda-forge speechbrain
echo.

:end
echo.
echo Installation attempt completed.
echo.
pause 