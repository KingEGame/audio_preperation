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
echo    %L_BLUE%TESTING GPU COMPATIBILITY%RESET%
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

echo    %L_YELLOW%Running GPU test...%RESET%
if exist "scripts\test_gpu.py" (
    python scripts\test_gpu.py
) else (
    echo %L_CYAN%PyTorch Information:%RESET%
    python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"
    echo.
    echo %L_CYAN%System GPU Information:%RESET%
    python -c "import subprocess; result = subprocess.run(['nvidia-smi'], capture_output=True, text=True); print(result.stdout if result.returncode == 0 else 'nvidia-smi not available or no GPU found')"
)

echo.
pause 