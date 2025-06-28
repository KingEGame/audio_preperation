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

:: Helper function to activate conda environment
set "CONDA_ROOT_PREFIX=%cd%\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo %L_RED%Conda not found! Run install_environment.bat first.%RESET%
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
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
    echo %L_RED%Failed to activate environment!%RESET%
    exit /b 1
)

echo %L_GREEN%Environment activated successfully!%RESET%
exit /b 0 