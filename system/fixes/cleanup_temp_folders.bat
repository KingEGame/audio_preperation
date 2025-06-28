@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
set "CONDA_ROOT_PREFIX=%cd%\..\..\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\..\..\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo ERROR: Conda not found! Run setup.bat first.
    pause
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo ERROR: Environment not found! Run setup.bat first.
    pause
    exit /b 1
)

:: Set conda environment variables
set "CONDA_PREFIX=!INSTALL_ENV_DIR!"
set "CONDA_DEFAULT_ENV=audio_env"
set "CONDA_PROMPT_MODIFIER=(audio_env) "

:: Add conda to PATH
set "PATH=!CONDA_ROOT_PREFIX!\Scripts;!CONDA_ROOT_PREFIX!\Library\bin;!CONDA_ROOT_PREFIX!\condabin;!PATH!"

:: Activate the environment
call "!CONDA_ROOT_PREFIX!\condabin\conda.bat" activate "!INSTALL_ENV_DIR!" || (
    echo ERROR: Failed to activate environment!
    pause
    exit /b 1
)

echo.
echo ========================================
echo TEMPORARY FOLDER CLEANUP
echo ========================================
echo.
echo This will remove old temporary processing folders
echo that were created during audio processing.
echo.

:: Check if dry run is requested
if "%~1"=="--dry-run" (
    echo Running in DRY RUN mode - no files will be deleted
    echo.
    python "%~dp0..\scripts\cleanup_temp_folders.py" --dry-run
) else if "%~1"=="--help" (
    echo Usage options:
    echo   cleanup_temp_folders.bat          - Clean up old folders (24h+)
    echo   cleanup_temp_folders.bat --dry-run - Show what would be deleted
    echo   cleanup_temp_folders.bat --help    - Show this help
    echo.
    echo Examples:
    echo   cleanup_temp_folders.bat
    echo   cleanup_temp_folders.bat --dry-run
    echo.
    pause
    exit /b 0
) else (
    echo This will delete temporary folders older than 24 hours.
    echo.
    set /p CONFIRM="Continue with cleanup? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Cleanup cancelled.
        echo.
        echo To see what would be deleted without actually deleting:
        echo   cleanup_temp_folders.bat --dry-run
        pause
        exit /b 0
    )
    
    echo.
    echo Starting cleanup...
    echo.
    
    python "%~dp0..\scripts\cleanup_temp_folders.py"
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo CLEANUP COMPLETED SUCCESSFULLY!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo CLEANUP FAILED!
    echo ========================================
    echo Check the error messages above.
)

echo.
pause 