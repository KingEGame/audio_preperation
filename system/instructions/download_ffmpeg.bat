@echo off
setlocal enabledelayedexpansion

for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "L_BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

echo ========================================
echo Downloading and Installing FFmpeg
echo ========================================

where ffmpeg >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo %L_GREEN%FFmpeg is already installed system-wide%RESET%
    ffmpeg -version
    pause
    exit /b 0
)

cd system\ffmpeg

echo %L_CYAN%Downloading latest FFmpeg for Windows 64-bit...%RESET%
curl -L -o ffmpeg.zip "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

if exist "ffmpeg.zip" (
    echo %L_CYAN%Extracting FFmpeg archive...%RESET%
    tar -xf ffmpeg.zip
    
    echo %L_CYAN%Moving FFmpeg executables...%RESET%
    if exist "ffmpeg-master-latest-win64-gpl\bin" (
        move ffmpeg-master-latest-win64-gpl\bin\* .
        rmdir /s /q ffmpeg-master-latest-win64-gpl
    )
    
    echo %L_CYAN%Cleaning up archive...%RESET%
    del ffmpeg.zip
    
    set "PATH=%cd%;%PATH%"
    
    echo %L_CYAN%Testing FFmpeg installation...%RESET%
    ffmpeg -version >nul 2>&1
    if "%ERRORLEVEL%" EQU "0" (
        echo %L_GREEN%FFmpeg installed successfully%RESET%
        echo %L_CYAN%FFmpeg version:%RESET%
        ffmpeg -version
        echo.
        echo %L_YELLOW%FFmpeg is now available in: %cd%%RESET%
        echo %L_YELLOW%To use FFmpeg, run scripts from this directory or add to PATH manually%RESET%
    ) else (
        echo %L_RED%FFmpeg installation failed%RESET%
    )
) else (
    echo %L_RED%Failed to download FFmpeg%RESET%
)

cd ..\..

echo.
echo %L_CYAN%FFmpeg setup completed%RESET%
echo %L_YELLOW%Note: FFmpeg is installed locally in system\ffmpeg\%RESET%
echo %L_YELLOW%To use FFmpeg globally, add system\ffmpeg to your PATH environment variable%RESET%
pause 