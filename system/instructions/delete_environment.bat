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
echo    %L_RED%DELETING ENVIRONMENT%RESET%
echo.
set "AUDIO_ENV_DIR=%cd%\audio_environment"

if not exist "!AUDIO_ENV_DIR!\" (
    echo    %L_GREEN%Environment does not exist.%RESET%
    pause
    exit /b 0
)

echo    %L_YELLOW%Deleting environment...%RESET%
rd /s /q "!AUDIO_ENV_DIR!" 2>nul
del start_audio_environment.bat 2>nul
del start_audio_processing.bat 2>nul

if exist "!AUDIO_ENV_DIR!\" (
    echo    %L_RED%Failed to delete environment.%RESET%
    pause
    exit /b 1
)

echo    %L_GREEN%Environment deleted!%RESET%
pause 