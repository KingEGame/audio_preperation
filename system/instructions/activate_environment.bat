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

:: Portable Conda Environment Activation

set INSTALL_DIR=%cd%\audio_environment
set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\audio_environment\env
:: Check if portable conda exists
if not exist "!CONDA_ROOT_PREFIX!\_conda.exe" (
    echo %L_RED%Portable Conda not found! Run system\instructions\install_portable_conda.bat first.%RESET%
    exit /b 1
)

:: Check if environment exists
if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo %L_RED%Environment not found! Run system\instructions\install_portable_conda.bat first.%RESET%
    exit /b 1
)

:: Set environment variables

set CONDA_DEFAULT_ENV=audio_env
set CONDA_PROMPT_MODIFIER=(audio_env) 

:: Activate the environment using portable conda
@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

:: Verify we're using the right Python
python -c "import sys; print('Python path:', sys.executable)" | findstr "audio_environment" >nul
if "%ERRORLEVEL%" NEQ "0" (
    echo %L_RED%ERROR: Still using wrong Python!%RESET%
    echo Expected: !INSTALL_ENV_DIR!\python.exe
    echo Actual: 
    python -c "import sys; print(sys.executable)"
    exit /b 1
)

echo %L_GREEN%✅ Portable environment activated successfully!%RESET%
echo %L_CYAN%🐍 Python: !INSTALL_ENV_DIR!\python.exe%RESET%
echo %L_CYAN%📦 Conda: !CONDA_ROOT_PREFIX!\_conda.exe%RESET%
exit /b 0 