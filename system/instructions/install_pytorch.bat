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
echo    %L_BLUE%INSTALLING PYTORCH WITH CUDA SUPPORT%RESET%
echo.

:: Check if environment exists
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"
set "PIP_EXE=%cd%\audio_environment\env\Scripts\pip.exe"
if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
    pause
    exit /b 1
)

:: Check current PyTorch installation
echo    %L_CYAN%Checking current PyTorch installation...%RESET%
"!PYTHON_EXE!" -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>nul || (
    echo %L_YELLOW%PyTorch not installed yet.%RESET%
)

echo.
echo    %L_GREEN%Select CUDA version for PyTorch installation:%RESET%
echo    1) CUDA 11.8 (PyTorch 2.1.2+cu118)
echo    2) CUDA 12.1 (PyTorch 2.1.2+cu121) - %L_YELLOW%Recommended%RESET%
echo    3) CUDA 12.8 (PyTorch 2.1.2+cu128) - %L_YELLOW%Latest%RESET%
echo    4) CPU only (no CUDA)
echo.
set /p CUDA_CHOICE="    Enter your choice (1-4, default: 2): "

if "!CUDA_CHOICE!"=="" set "CUDA_CHOICE=2"

:: Install PyTorch based on choice using our specific PyTorch files
if "!CUDA_CHOICE!"=="1" (
    echo    %L_CYAN%Installing PyTorch with CUDA 11.8 support...%RESET%
    conda install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 || (
        echo %L_RED%Failed to install PyTorch with CUDA 11.8!%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=11.8"
) else if "!CUDA_CHOICE!"=="2" (
    echo    %L_CYAN%Installing PyTorch with CUDA 12.1 support...%RESET%
    conda install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || (
        echo %L_RED%Failed to install PyTorch with CUDA 12.1!%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=12.1"
) else if "!CUDA_CHOICE!"=="3" (
    echo    %L_CYAN%Installing PyTorch with CUDA 12.8 support...%RESET%
    conda install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 || (
        echo %L_RED%Failed to install PyTorch with CUDA 12.8!%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=12.8"
) else if "!CUDA_CHOICE!"=="4" (
    echo    %L_CYAN%Installing PyTorch CPU-only version...%RESET%
    conda install torch torchvision torchaudio || (
        echo %L_RED%Failed to install PyTorch CPU version!%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=CPU"
) else (
    echo %L_RED%Invalid choice! Please select 1-4.%RESET%
    pause
    exit /b 1
)

:: Verify PyTorch installation
echo    %L_CYAN%Verifying PyTorch installation...%RESET%
"!PYTHON_EXE!" -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)" || (
    echo %L_YELLOW%Warning: PyTorch verification failed, but installation may have succeeded.%RESET%
)

echo.
echo    %L_GREEN%PyTorch installation completed!%RESET%
if not "!CUDA_VERSION!"=="CPU" (
    echo    %L_CYAN%Installed with CUDA !CUDA_VERSION! support%RESET%
) else (
    echo    %L_CYAN%Installed CPU-only version%RESET%
)
