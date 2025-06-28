@echo off
setlocal EnableDelayedExpansion

rem ─── базовые переменные ────────────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

for /F "delims=" %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "RESET=%ESC%[0m"

echo(
echo    %L_RED%COMPLETE ENVIRONMENT REMOVAL (SIMPLE VERSION)%RESET%
echo(
echo    %L_YELLOW%This will completely remove:%RESET%
echo    - Audio processing environment (Conda + Python)
echo    - All temporary processing folders
echo    - Created batch files
echo(
echo    %L_RED%WARNING: This action cannot be undone!%RESET%
echo(
set /P CONFIRM="    Are you sure you want to continue? (y/N): "
if /I not "!CONFIRM!"=="y" (
    echo    %L_YELLOW%Operation cancelled.%RESET%
    pause
    goto :EOF
)

echo(
echo    %L_CYAN%Starting complete removal...%RESET%
echo(

rem ─── 1. Удаляем среду ──────────────────────────────────────────────────────
echo    %L_CYAN%1. Removing audio processing environment...%RESET%
if exist "%SCRIPT_DIR%audio_environment\" (
    rd /s /q "%SCRIPT_DIR%audio_environment"
    if exist "%SCRIPT_DIR%audio_environment\" (
        echo    %L_RED%   ❌ Failed to remove environment directory.%RESET%
    ) else (
        echo    %L_GREEN%   ✅ Environment removed successfully.%RESET%
    )
) else (
    echo    %L_GREEN%   ✅ Environment directory not found.%RESET%
)

rem ─── 2. Удаляем временные папки ────────────────────────────────────────────
echo    %L_CYAN%2. Removing temporary processing folders...%RESET%
set "FOUND_TEMP=0"
for /D %%i in ("%SCRIPT_DIR%temp_temp_*") do (
    set "FOUND_TEMP=1"
    echo    %L_YELLOW%   Removing: %%~nxi%RESET%
    rd /s /q "%%i"
)
if !FOUND_TEMP! EQU 0 (
    echo    %L_GREEN%   ✅ No temporary folders found.%RESET%
) else (
    echo    %L_GREEN%   ✅ Temporary folders removed.%RESET%
)

rem ─── 3. Удаляем созданные batch-файлы ───────────────────────────────────────
echo    %L_CYAN%3. Removing created batch files...%RESET%
set "BAT_COUNT=0"
for %%f in (
    start_processing.bat
    activate_environment.bat
    cleanup_temp.bat
) do (
    if exist "%SCRIPT_DIR%%%f" (
        del /q "%SCRIPT_DIR%%%f"
        echo    %L_YELLOW%   Removed: %%f%RESET%
        set /A BAT_COUNT+=1
    )
)
if !BAT_COUNT! EQU 0 (
    echo    %L_GREEN%   ✅ No batch files found to remove.%RESET%
) else (
    echo    %L_GREEN%   ✅ Removed !BAT_COUNT! batch file(s).%RESET%
)

rem ─── завершение ────────────────────────────────────────────────────────────
echo(
echo    %L_GREEN%✅ COMPLETE REMOVAL FINISHED!%RESET%
echo(
echo    %L_CYAN%Press any key to exit...%RESET%
pause >nul
popd
endlocal