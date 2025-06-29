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
echo    %L_BLUE%PYTORCH INSTALLATION%RESET%
echo.

set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"
set "PIP_EXE=%cd%\audio_environment\env\Scripts\pip.exe"
if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
    echo %L_YELLOW%Please ensure the Python environment is properly created%RESET%
    exit /b 1
)

echo    %L_CYAN%Checking current PyTorch...%RESET%
"!PYTHON_EXE!" -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>nul || (
    echo %L_YELLOW%PyTorch not installed yet.%RESET%
)

echo.
echo    %L_GREEN%Select CUDA version:%RESET%
echo    1) CUDA 11.8 (PyTorch 2.1.2+cu118)
echo    2) CUDA 12.1 (PyTorch 2.1.2+cu121) - %L_YELLOW%Recommended%RESET%
echo    3) CUDA 12.8 (PyTorch 2.1.2+cu128) - %L_YELLOW%Latest%RESET%
echo    4) CPU only (no CUDA)
echo.
set /p CUDA_CHOICE="    Enter your choice (1-4, default: 2): "

if "!CUDA_CHOICE!"=="" set "CUDA_CHOICE=2"

if "!CUDA_CHOICE!"=="1" (
    echo    %L_CYAN%Installing PyTorch with CUDA 11.8...%RESET%
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 || (
        echo %L_RED%Failed to install PyTorch with CUDA 11.8%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=11.8"
) else if "!CUDA_CHOICE!"=="2" (
    echo    %L_CYAN%Installing PyTorch with CUDA 12.1...%RESET%
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || (
        echo %L_RED%Failed to install PyTorch with CUDA 12.1%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=12.1"
) else if "!CUDA_CHOICE!"=="3" (
    echo    %L_CYAN%Installing PyTorch with CUDA 12.8...%RESET%
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 || (
        echo %L_RED%Failed to install PyTorch with CUDA 12.8%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=12.8"
) else if "!CUDA_CHOICE!"=="4" (
    echo    %L_CYAN%Installing PyTorch CPU-only...%RESET%
    pip3 install torch torchvision torchaudio || (
        echo %L_RED%Failed to install PyTorch CPU version%RESET%
        pause
        exit /b 1
    )
    set "CUDA_VERSION=CPU"
) else (
    echo %L_RED%Invalid choice! Please select 1-4.%RESET%
    pause
    exit /b 1
)

echo    %L_CYAN%Verifying PyTorch...%RESET%
"!PYTHON_EXE!" -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)" || (
    echo %L_YELLOW%Warning: PyTorch verification failed%RESET%
)

echo.
echo    %L_GREEN%PyTorch installation completed%RESET%
if not "!CUDA_VERSION!"=="CPU" (
    echo    %L_CYAN%Installed with CUDA !CUDA_VERSION! support%RESET%
) else (
    echo    %L_CYAN%Installed CPU-only version%RESET%
)
