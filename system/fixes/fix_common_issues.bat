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
echo    %L_BLUE%FIXING COMMON ISSUES%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
    pause
    exit /b 1
)

echo    %L_CYAN%Activating environment...%RESET%
call system\instructions\activate_environment.bat || (
    pause
    exit /b 1
)

echo    %L_YELLOW%Checking and fixing GPU/CUDA support...%RESET%
python -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" || (
    echo %L_RED%Failed to check PyTorch installation!%RESET%
    pause
    exit /b 1
)

:: If CUDA is not available, reinstall PyTorch
python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" || (
    echo %L_YELLOW%CUDA not available, reinstalling PyTorch with CUDA support...%RESET%
    call system\instructions\install_pytorch.bat
)

echo    %L_YELLOW%Installing build tools...%RESET%
pip install wheel setuptools cmake --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to install cmake, trying alternative approach...%RESET%
)

echo    %L_YELLOW%Reinstalling all packages from requirements.txt...%RESET%
pip install -r system\requirements\requirements.txt --force-reinstall --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Main installation failed, trying conda method...%RESET%
    echo %L_CYAN%Installing sentencepiece via conda...%RESET%
    conda install -c conda-forge sentencepiece -y || (
        echo %L_RED%Failed to install sentencepiece via conda!%RESET%
        pause
        exit /b 1
    )
    
    echo %L_CYAN%Installing remaining packages...%RESET%
    pip install -r system\requirements\requirements.txt --force-reinstall --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to reinstall from requirements.txt!%RESET%
        echo Please check the error messages above.
        pause
        exit /b 1
    )
)

echo    %L_GREEN%Checking fixes...%RESET%
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import silero_vad; print('Silero VAD: working')"

echo    %L_GREEN%Fixes applied!%RESET%
pause 