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

echo ========================================
echo Installing FFmpeg Globally
echo ========================================

:: Check if FFmpeg is already installed system-wide
where ffmpeg >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo %L_GREEN%FFmpeg is already installed system-wide!%RESET%
    ffmpeg -version
    pause
    exit /b 0
)

:: Check if FFmpeg exists in our local directory
set "FFMPEG_DIR=%cd%\system\ffmpeg"
if not exist "!FFMPEG_DIR!\ffmpeg.exe" (
    echo %L_RED%FFmpeg not found in !FFMPEG_DIR!%RESET%
    echo %L_YELLOW%Please run download_ffmpeg.bat first!%RESET%
    pause
    exit /b 1
)

echo %L_CYAN%Adding FFmpeg to system PATH...%RESET%

:: Get current PATH
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"

:: Check if FFmpeg path is already in PATH
echo "!CURRENT_PATH!" | findstr /i "!FFMPEG_DIR!" >nul
if "%ERRORLEVEL%" EQU "0" (
    echo %L_YELLOW%FFmpeg path is already in system PATH!%RESET%
    goto TestInstallation
)

:: Add FFmpeg to system PATH
set "NEW_PATH=!CURRENT_PATH!;!FFMPEG_DIR!"
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul 2>&1

if "%ERRORLEVEL%" EQU "0" (
    echo %L_GREEN%FFmpeg added to system PATH successfully!%RESET%
    
    :: Update current session PATH
    set "PATH=!PATH!;!FFMPEG_DIR!"
    
    echo %L_YELLOW%Note: You may need to restart your command prompt or computer for changes to take effect.%RESET%
) else (
    echo %L_RED%Failed to add FFmpeg to system PATH!%RESET%
    echo %L_YELLOW%You may need to run this script as Administrator.%RESET%
    pause
    exit /b 1
)

:TestInstallation
echo.
echo %L_CYAN%Testing FFmpeg installation...%RESET%
ffmpeg -version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo %L_GREEN%FFmpeg is now available globally!%RESET%
    echo %L_CYAN%FFmpeg version:%RESET%
    ffmpeg -version
) else (
    echo %L_YELLOW%FFmpeg not found in PATH yet. Please restart your command prompt.%RESET%
    echo %L_CYAN%You can also use FFmpeg directly from: !FFMPEG_DIR!%RESET%
)

echo.
echo %L_GREEN%Global FFmpeg installation completed!%RESET%
pause 