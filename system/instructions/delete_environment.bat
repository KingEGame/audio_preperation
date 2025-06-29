@echo off
setlocal EnableDelayedExpansion

for /F "delims=" %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "RESET=%ESC%[0m"

echo(
echo    %L_RED%ENVIRONMENT REMOVAL%RESET%
echo(
echo    %L_YELLOW%This will remove:%RESET%
echo    - Audio processing environment (Conda + Python)
echo    - All temporary processing folders
echo    - Created batch files
echo(
echo    %L_RED%WARNING: This action cannot be undone%RESET%
echo(
set /P CONFIRM="    Are you sure you want to continue? (y/N): "
if /I not "!CONFIRM!"=="y" (
    echo    %L_YELLOW%Operation cancelled%RESET%
    pause
    goto :EOF
)

echo(
echo    %L_CYAN%Starting removal...%RESET%
echo(

echo    %L_CYAN%1. Removing audio processing environment...%RESET%
rd /s /q "audio_environment"

echo    %L_CYAN%2. Removing temporary processing folders...%RESET%
call system\fixes\cleanup_temp_folders.bat

echo    %L_CYAN%3. Removing created batch files...%RESET%
del ..\..\start_processing.bat
del ..\..\activate_environment.bat
del ..\..\cleanup_temp.bat
del ..\..\hf_token.bat
del ..\..\Access

echo(
echo    %L_GREEN%[OK] Removal completed%RESET%
echo(
echo    %L_CYAN%Press any key to exit...%RESET%
pause >nul
popd
endlocal