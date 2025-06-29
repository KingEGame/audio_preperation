@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
call system\instructions\activate_environment.bat

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
    python ..\scripts\cleanup_temp_folders.py --dry-run
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
    
    python ..\scripts\cleanup_temp_folders.py
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