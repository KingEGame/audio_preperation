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
echo    %L_BLUE%PORTABLE CONDA%RESET%
echo.
echo    %L_GREEN%Installing portable Miniconda:%RESET%
echo    - Portable Miniconda (no system installation)
echo    - Python 3.11 environment
echo    - Ready for package installation
echo.

curl --version >nul 2>&1
if "%ERRORLEVEL%" NEQ "0" (
    echo curl is not available. Please install curl then re-run the script.
    goto end
)
echo "%CD%"| findstr /C:" " >nul && echo This script can not be installed under a path with spaces. Please correct your folder names and re-try installation. && goto exit

set "SPCHARMESSAGE=WARNING: Special characters were detected in the installation path! This can cause the installation to fail!"
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
    call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

set TMP=%cd%\audio_environment
set TEMP=%cd%\audio_environment

set INSTALL_DIR=%cd%\audio_environment
set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\audio_environment\env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe
set conda_exists=F

call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    set conda_exists=T
    call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%"
    goto RunScript
)

echo Downloading Miniconda...
mkdir "%INSTALL_DIR%"
call curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo Miniconda failed to download. && goto end )
echo Installing Miniconda...
start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%
echo Miniconda version:
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo Miniconda not found. && goto end )

echo Creating environment...
call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || ( echo. && echo Conda environment creation failed. && goto end )

echo.
echo    %L_GREEN%[OK] Portable Conda installation completed%RESET%
echo.
echo    %L_CYAN%Files created:%RESET%
echo    - %CONDA_ROOT_PREFIX% (portable conda)
echo    - %INSTALL_ENV_DIR% (python environment)
echo.
echo    %L_YELLOW%Next step: Run install_environment.bat to install packages%RESET%
echo.

:RunScript
:end
:exit
