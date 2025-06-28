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
echo    %L_BLUE%SAFE AUDIO PROCESSING - Audio Processing Pipeline%RESET%
echo.

:: Check if environment exists
if not exist "audio_environment" (
    echo    %L_RED%❌ Environment not found!%RESET%
    echo    Please run setup.bat and select option 1 to install the environment.
    pause
    exit /b 1
)

:: Check parameters
if "%~1"=="" (
    echo    %L_RED%❌ Input file/folder not specified!%RESET%
    echo.
    echo    %L_YELLOW%Usage:%RESET%
    echo    run_safe_processing.bat "input_file.mp3" "output_folder"
    echo.
    echo    %L_YELLOW%Examples:%RESET%
    echo    run_safe_processing.bat "lecture.mp3" "lecture_results"
    echo    run_safe_processing.bat "audio_folder" "results"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo    %L_RED%❌ Output folder not specified!%RESET%
    echo.
    echo    %L_YELLOW%Usage:%RESET%
    echo    run_safe_processing.bat "input_file.mp3" "output_folder"
    pause
    exit /b 1
)

:: Activate environment
echo    %L_CYAN%Activating environment...%RESET%
call ..\instructions\activate_environment.bat

:: Check if input exists
if not exist "%~1" (
    echo    %L_RED%❌ Input file/folder not found: %~1%RESET%
    pause
    exit /b 1
)

:: Create output directory
if not exist "%~2" (
    echo    %L_CYAN%Creating output directory: %~2%RESET%
    mkdir "%~2"
)

echo.
echo    %L_CYAN%Starting safe audio processing...%RESET%
echo    %L_YELLOW%Input: %~1%RESET%
echo    %L_YELLOW%Output: %~2%RESET%
echo.

:: Run safe processing script
python ..\scripts\audio_processing_safe.py --input "%~1" --output "%~2" --verbose

if "%ERRORLEVEL%" EQU "0" (
    echo.
    echo    %L_GREEN%✅ Safe processing completed successfully!%RESET%
    echo    %L_CYAN%Results saved in: %~2%RESET%
) else (
    echo.
    echo    %L_RED%❌ Safe processing failed with error code: %ERRORLEVEL%%RESET%
    echo    %L_YELLOW%Check the error messages above for details.%RESET%
)

echo.
pause 