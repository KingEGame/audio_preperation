@echo off
cd /D "%~dp0"
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
echo    %L_BLUE%SENTENCEPIECE INSTALLATION FIX%RESET%
echo.
echo    %L_YELLOW%Attempting to install sentencepiece with alternative methods...%RESET%
echo.

:: Set environment variables
call system\instructions\activate_environment.bat

echo    %L_CYAN%Method 1: Trying conda installation (pre-compiled)...%RESET%
conda install -c conda-forge sentencepiece -y
if %errorlevel% equ 0 (
    echo    %L_GREEN%✅ Successfully installed sentencepiece via conda!%RESET%
    goto :end
)

echo    %L_YELLOW%Method 1 failed. Trying Method 2...%RESET%
echo    %L_CYAN%Method 2: Trying pip with pre-compiled wheels...%RESET%
pip install --only-binary=all --no-cache-dir sentencepiece
if %errorlevel% equ 0 (
    echo    %L_GREEN%✅ Successfully installed sentencepiece from pre-compiled wheel!%RESET%
    goto :end
)

echo    %L_YELLOW%Method 2 failed. Trying Method 3...%RESET%
echo    %L_CYAN%Method 3: Trying specific version...%RESET%
pip install sentencepiece==0.1.99
if %errorlevel% equ 0 (
    echo    %L_GREEN%✅ Successfully installed sentencepiece version 0.1.99!%RESET%
    goto :end
)

echo    %L_YELLOW%Method 3 failed. Trying Method 4...%RESET%
echo    %L_CYAN%Method 4: Trying from alternative source...%RESET%
pip install --index-url https://pypi.org/simple/ sentencepiece
if %errorlevel% equ 0 (
    echo    %L_GREEN%✅ Successfully installed sentencepiece from alternative source!%RESET%
    goto :end
)

echo    %L_RED%All installation methods failed!%RESET%
echo.
echo    %L_YELLOW%Manual installation required:%RESET%
echo.
echo    1. Install Visual Studio Build Tools:
echo       - Download from: https://visualstudio.microsoft.com/downloads/
echo       - Install "C++ build tools" workload
echo.
echo    2. Install cmake:
echo       - Download from: https://cmake.org/download/
echo       - Add to PATH during installation
echo.
echo    3. Restart command prompt and run:
echo       pip install sentencepiece
echo.
echo    %L_YELLOW%Note: sentencepiece is optional for basic functionality.%RESET%
echo    %L_YELLOW%The system will work without it, but some advanced features may be limited.%RESET%

:end
echo.
echo    %L_GREEN%Sentencepiece installation attempt completed.%RESET%
echo.
pause 