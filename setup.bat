@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion
set "PATH=%PATH%;%SystemRoot%\system32"

:: Generate the ESC character
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

:: Colors
set "BLACK=%ESC%[30m"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "MAGENTA=%ESC%[35m"
set "CYAN=%ESC%[36m"
set "WHITE=%ESC%[37m"
set "L_BLACK=%ESC%[90m"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_BLUE=%ESC%[94m"
set "L_MAGENTA=%ESC%[95m"
set "L_CYAN=%ESC%[96m"
set "L_WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

:: Check for spaces in path
if not "%CD%"=="%CD: =%" (
    echo.
    echo %L_RED%ERROR: Path contains spaces!%RESET%
    echo Please use a folder path without spaces.
    pause
    exit /b 1
)

:: Check for special characters in path
set "SPCHARMESSAGE=WARNING: Special characters were detected in the installation path! This can cause the installation to fail!"
echo "%CD%"| findstr /R /C:"[!#\$%&()*+,;<=>?@\[\]^`{|}~]" >nul && (
    echo.
    echo %L_YELLOW%!SPCHARMESSAGE!%RESET%
    pause
)
set SPCHARMESSAGE=

:: Check for curl
curl --version >nul 2>&1
if "%ERRORLEVEL%" NEQ "0" (
    echo.
    echo %L_RED%curl is not available on this system.%RESET%
    echo Please install curl then re-run the script: https://curl.se/
    echo or perform a manual installation of a Conda Python environment.
    pause
    exit /b 1
)

:: Check for requirements.txt
if not exist "system\requirements\requirements.txt" (
    echo.
    echo %L_RED%ERROR: requirements.txt not found in system\requirements!%RESET%
    echo Please ensure requirements.txt is in the system\requirements directory
    pause
    exit /b 1
)

:MainMenu
cls
echo %L_BLUE%AUDIO PROCESSING PIPELINE SETUP%RESET%
echo.
echo %L_GREEN%MAIN OPTIONS%RESET%
echo 1) Install/Update Environment (everything needed for the project)
echo 2) Test Everything (testing everything that was installed)
echo 3) Check Dependencies Versions (checklist of dependency versions)
echo 4) Fix Issues (troubleshooting)
echo 5) Help (help)
echo.
echo %L_RED%MAINTENANCE%RESET%
echo 6) Delete Environment (delete environment and everything installed)
echo.
echo %L_RED%0) Exit/Quit%RESET%
echo.
set /p UserOption="    Enter your choice: "

if "%UserOption%"=="1" goto InstallEnvironment
if "%UserOption%"=="2" goto TestEverything
if "%UserOption%"=="3" goto CheckVersions
if "%UserOption%"=="4" goto FixIssues
if "%UserOption%"=="5" goto ShowHelp
if "%UserOption%"=="6" goto DeleteEnvironment
if "%UserOption%"=="0" goto End

goto MainMenu

:InstallEnvironment
echo.
echo    %L_CYAN%Installing complete environment with all dependencies...%RESET%
echo    %L_YELLOW%This includes: Portable Miniconda, Python, PyTorch, Whisper, Demucs, FFmpeg%RESET%
echo.
echo    %L_GREEN%Using portable Conda installation - no system changes required!%RESET%
echo    %L_YELLOW%This creates a self-contained environment in the project folder.%RESET%
echo.
call system\instructions\install_environment.bat
goto MainMenu

:TestEverything
echo.
echo    %L_CYAN%Testing everything that was installed...%RESET%
echo    %L_YELLOW%This will test: GPU, CUDA, PyTorch, FFmpeg, and Diarization%RESET%
echo.
call system\instructions\test_everything.bat
goto MainMenu

:CheckVersions
echo.
echo    %L_CYAN%Checking versions of all dependencies...%RESET%
echo.
call system\instructions\check_versions.bat
goto MainMenu

:FixIssues
echo.
echo    %L_CYAN%Opening selective fixes menu...%RESET%
echo    %L_YELLOW%Choose specific issues to fix instead of fixing everything%RESET%
echo.
call system\instructions\fix_selective.bat
goto MainMenu

:ShowHelp
cls
echo.
echo    %L_BLUE%AUDIO PROCESSING PIPELINE HELP%RESET%
echo.
echo    %L_GREEN%After installation (option 1), you can use:%RESET%
echo.
echo    %L_YELLOW%start_processing.bat%RESET% - Start audio processing
echo    Usage: start_processing.bat --input "audio.mp3" --output "results"
echo.
echo    %L_YELLOW%start_safe_processing.bat%RESET% - Start safe processing (with error handling)
echo    Usage: start_safe_processing.bat "audio.mp3" "results"
echo.
echo    %L_YELLOW%start_ultra_optimized_processing.bat%RESET% - Start ultra-optimized processing (best for parallel diarization)
echo    Usage: start_ultra_optimized_processing.bat "audio.mp3" "results"
echo.
echo    %L_YELLOW%diagnose_ffmpeg.bat%RESET% - Diagnose FFmpeg issues
echo    Usage: diagnose_ffmpeg.bat [audio_file]
echo.
echo    %L_YELLOW%cleanup_temp.bat%RESET% - Clean up temporary folders
echo    Usage: cleanup_temp.bat [--dry-run] [--help]
echo.
echo    %L_YELLOW%activate_environment.bat%RESET% - Activate environment
echo    Usage: activate_environment.bat
echo.
echo    %L_YELLOW%audio_concat.bat%RESET% - Concatenate audio files
echo    Usage: audio_concat.bat "input_folder" "output_file.mp3"
echo.
echo    %L_GREEN%Examples:%RESET%
echo    start_processing.bat --input lecture.mp3 --output results
echo    start_processing.bat --input meeting.mp3 --output results --steps split denoise vad diar
echo    start_safe_processing.bat "audio.mp3" "results"
echo    start_ultra_optimized_processing.bat "audio_folder" "results"
echo    diagnose_ffmpeg.bat "problematic_audio.mp3"
echo    cleanup_temp.bat --dry-run
echo    audio_concat.bat "chunks" "combined_audio.mp3"
echo.
echo    %L_GREEN%Main Options:%RESET%
echo    --input PATH         Input audio file/folder
echo    --output PATH        Output directory
echo    --chunk_duration N   Max chunk duration (seconds, default: 600)
echo    --final_chunk_duration N  Final chunk duration (seconds, default: 30)
echo    --steps STEP1 STEP2  Steps: split, denoise, vad, diar
echo    --create_final_chunks  Create final chunks
echo    --verbose            Verbose logging
echo.
echo    %L_YELLOW%Performance Optimization:%RESET%
echo    - Use start_ultra_optimized_processing.bat for best parallel diarization performance
echo    - For RTX 5080: use 4 workers, 300s chunks
echo    - For RTX 4070: use 3 workers, 240s chunks
echo    - For GTX 1660: use 2 workers, 180s chunks
echo.
echo    %L_YELLOW%Troubleshooting:%RESET%
echo    - Use option 4 to fix common issues
echo    - Use option 2 to test everything
echo    - Use diagnose_ffmpeg.bat for FFmpeg error 4294967268
echo    - Use cleanup_temp.bat to free disk space
echo    - Check GPU drivers for performance issues
echo    - Ensure internet connection for model downloads
echo.
echo    %L_CYAN%For detailed guides, see system\guides\ folder%RESET%
pause
goto MainMenu

:DeleteEnvironment
echo.
echo    %L_RED%WARNING: This will delete the entire environment and all installed files!%RESET%
echo    %L_YELLOW%This includes: Python environment, FFmpeg, and all dependencies%RESET%
echo.
set /p ConfirmDelete="    Are you sure? Type 'YES' to confirm: "
if /i not "%ConfirmDelete%"=="YES" (
    echo    %L_GREEN%Deletion cancelled.%RESET%
    pause
    goto MainMenu
)
echo.
echo    %L_CYAN%Deleting environment and all installed files...%RESET%
echo.
call system\instructions\delete_environment.bat
echo.
echo    %L_GREEN%✅ Environment deleted successfully!%RESET%
echo.
echo    %L_CYAN%Press any key to return to main menu...%RESET%
pause >nul
goto MainMenu

:End
echo.
echo    %L_CYAN%Thank you for using Audio Processing Pipeline Setup!%RESET%
pause
exit /b 0