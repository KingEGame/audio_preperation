@echo off
setlocal enabledelayedexpansion
cd /D "%~dp0"
echo "%CD%"| findstr /C:" " >nul

for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "L_BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

set CONDA_ROOT_PREFIX=%cd%\..\..\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\..\..\audio_environment\env

if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

python -c "import sys; print('Python path:', sys.executable)" | findstr "audio_environment" >nul
if "%ERRORLEVEL%" NEQ "0" (
    echo %L_RED%ERROR: Wrong Python%RESET%
    echo Expected: !INSTALL_ENV_DIR!\python.exe
    echo Actual: 
    python -c "import sys; print(sys.executable)"
    exit /b 1
)

echo %L_GREEN%[OK] Environment activated%RESET%
echo %L_CYAN%Python: !INSTALL_ENV_DIR!\python.exe%RESET%

:end
