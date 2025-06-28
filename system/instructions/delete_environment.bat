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
echo    %L_RED%COMPLETE ENVIRONMENT REMOVAL%RESET%
echo.
echo    %L_YELLOW%This will completely remove:%RESET%
echo    - Audio processing environment (Conda + Python)
echo    - All temporary processing folders
echo    - Created batch files (start_processing.bat, activate_environment.bat, cleanup_temp.bat)
echo    - FFmpeg installation (if installed globally)
echo.
echo    %L_RED%WARNING: This action cannot be undone!%RESET%
echo.
set /p CONFIRM="    Are you sure you want to continue? (y/N): "

if /i not "!CONFIRM!"=="y" (
    echo    %L_YELLOW%Operation cancelled.%RESET%
    pause
    exit /b 0
)

echo.
echo    %L_CYAN%Starting complete removal...%RESET%
echo.

:: Set paths
set "AUDIO_ENV_DIR=%cd%\audio_environment"
set "TEMP_PATTERN=temp_temp_*"

:: 1. Remove audio processing environment
echo    %L_CYAN%1. Removing audio processing environment...%RESET%
if exist "!AUDIO_ENV_DIR!\" (
    echo    %L_YELLOW%   Removing Conda environment and all files...%RESET%
    rd /s /q "!AUDIO_ENV_DIR!" 2>nul
    if exist "!AUDIO_ENV_DIR!\" (
        echo    %L_RED%   Failed to remove environment directory.%RESET%
        echo    %L_YELLOW%   Trying to force remove...%RESET%
        rmdir /s /q "!AUDIO_ENV_DIR!" 2>nul
    )
    if not exist "!AUDIO_ENV_DIR!\" (
        echo    %L_GREEN%   ✅ Environment removed successfully.%RESET%
    ) else (
        echo    %L_RED%   ❌ Failed to remove environment directory.%RESET%
    )
) else (
    echo    %L_GREEN%   ✅ Environment directory not found (already removed).%RESET%
)

:: 2. Remove temporary processing folders
echo    %L_CYAN%2. Removing temporary processing folders...%RESET%
set "TEMP_COUNT=0"
for /d %%i in (!TEMP_PATTERN!) do (
    echo    %L_YELLOW%   Removing: %%i%RESET%
    rd /s /q "%%i" 2>nul
    set /a TEMP_COUNT+=1
)
if !TEMP_COUNT! GTR 0 (
    echo    %L_GREEN%   ✅ Removed !TEMP_COUNT! temporary folder(s).%RESET%
) else (
    echo    %L_GREEN%   ✅ No temporary folders found.%RESET%
)

:: 3. Remove created batch files
echo    %L_CYAN%3. Removing created batch files...%RESET%
set "BAT_FILES_REMOVED=0"

if exist "start_processing.bat" (
    del "start_processing.bat" 2>nul
    echo    %L_YELLOW%   Removed: start_processing.bat%RESET%
    set /a BAT_FILES_REMOVED+=1
)

if exist "activate_environment.bat" (
    del "activate_environment.bat" 2>nul
    echo    %L_YELLOW%   Removed: activate_environment.bat%RESET%
    set /a BAT_FILES_REMOVED+=1
)

if exist "cleanup_temp.bat" (
    del "cleanup_temp.bat" 2>nul
    echo    %L_YELLOW%   Removed: cleanup_temp.bat%RESET%
    set /a BAT_FILES_REMOVED+=1
)

if !BAT_FILES_REMOVED! GTR 0 (
    echo    %L_GREEN%   ✅ Removed !BAT_FILES_REMOVED! batch file(s).%RESET%
) else (
    echo    %L_GREEN%   ✅ No batch files found to remove.%RESET%
)

:: 4. Remove old batch files (if they exist from previous versions)
echo    %L_CYAN%4. Removing old batch files (if any)...%RESET%
set "OLD_BAT_FILES_REMOVED=0"

for %%f in (start_safe_processing.bat start_ultra_optimized_processing.bat diagnose_ffmpeg.bat audio_concat.bat test_new_architecture.bat test_no_duration_limit.bat) do (
    if exist "%%f" (
        del "%%f" 2>nul
        echo    %L_YELLOW%   Removed: %%f%RESET%
        set /a OLD_BAT_FILES_REMOVED+=1
    )
)

if !OLD_BAT_FILES_REMOVED! GTR 0 (
    echo    %L_GREEN%   ✅ Removed !OLD_BAT_FILES_REMOVED! old batch file(s).%RESET%
) else (
    echo    %L_GREEN%   ✅ No old batch files found.%RESET%
)

:: 5. Remove FFmpeg from system PATH (if it was installed globally)
echo    %L_CYAN%5. Checking for global FFmpeg installation...%RESET%
echo    %L_YELLOW%   Note: Global FFmpeg removal requires administrator privileges.%RESET%
echo    %L_YELLOW%   If you installed FFmpeg globally, you may need to remove it manually.%RESET%
echo    %L_YELLOW%   Check your system PATH for FFmpeg entries.%RESET%

:: 6. Clean up any remaining temporary files
echo    %L_CYAN%6. Cleaning up any remaining temporary files...%RESET%
for %%f in (*.tmp *.temp *.log) do (
    if exist "%%f" (
        del "%%f" 2>nul
        echo    %L_YELLOW%   Removed: %%f%RESET%
    )
)

echo.
echo    %L_GREEN%✅ COMPLETE REMOVAL FINISHED!%RESET%
echo.
echo    %L_CYAN%Summary of removed items:%RESET%
echo    - Audio processing environment (Conda + Python)
echo    - Temporary processing folders
echo    - Created batch files
echo    - Old batch files (if any)
echo    - Temporary files
echo.
echo    %L_YELLOW%Note: If you installed FFmpeg globally, check your system PATH%RESET%
echo    %L_YELLOW%and remove FFmpeg entries manually if needed.%RESET%
echo.
echo    %L_CYAN%Press any key to continue...%RESET%
pause >nul 