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

:: Set environment variables
set "CONDA_ROOT_PREFIX=%cd%\..\..\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\..\..\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo %L_RED%ERROR: Conda not found! Run setup.bat first.%RESET%
    pause
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo %L_RED%ERROR: Environment not found! Run setup.bat first.%RESET%
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
    echo %L_RED%ERROR: Failed to activate environment!%RESET%
    pause
    exit /b 1
)

echo.
echo ========================================
echo FORCE INSTALL MAIN REQUIREMENTS
echo ========================================
echo.
echo This will force reinstall all main requirements
echo from the main requirements.txt file.
echo.
echo %L_YELLOW%WARNING: This will overwrite existing packages!%RESET%
echo.
set /p CONFIRM="Continue with force install? (y/n): "
if /i not "!CONFIRM!"=="y" (
    echo %L_YELLOW%Operation cancelled.%RESET%
    pause
    exit /b 0
)

echo.
echo %L_CYAN%Starting force installation of main requirements...%RESET%
echo.

:: Upgrade pip first
echo %L_CYAN%1. Upgrading pip...%RESET%
pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
if %ERRORLEVEL% NEQ 0 (
    echo %L_RED%Failed to upgrade pip!%RESET%
    pause
    exit /b 1
)

:: Install PyTorch first (to avoid conflicts)
echo %L_CYAN%2. Installing PyTorch first (to avoid conflicts)...%RESET%
call "%~dp0..\instructions\install_pytorch.bat"
if %ERRORLEVEL% NEQ 0 (
    echo %L_RED%Failed to install PyTorch!%RESET%
    pause
    exit /b 1
)

:: Force install main requirements (excluding PyTorch)
echo %L_CYAN%3. Force installing main requirements (excluding PyTorch)...%RESET%
pip install --force-reinstall --no-deps -r "%~dp0..\requirements\requirements.txt" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
if %ERRORLEVEL% NEQ 0 (
    echo %L_RED%Failed to install main requirements!%RESET%
    pause
    exit /b 1
)

:: Install any missing dependencies
echo %L_CYAN%4. Installing missing dependencies...%RESET%
pip install -r "%~dp0..\requirements\requirements.txt" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
if %ERRORLEVEL% NEQ 0 (
    echo %L_RED%Failed to install missing dependencies!%RESET%
    pause
    exit /b 1
)

echo.
echo %L_GREEN%✅ Main requirements force installed successfully!%RESET%
echo.
echo %L_CYAN%Summary:%RESET%
echo - Pip upgraded to latest version
echo - PyTorch installed first (to avoid conflicts)
echo - Main requirements force reinstalled
echo - Missing dependencies installed
echo.
echo %L_YELLOW%Note: PyTorch was installed with the selected CUDA version.%RESET%
echo %L_YELLOW%If you need to change CUDA version, run setup.bat → option 4 → option 3%RESET%
echo.
pause 