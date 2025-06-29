@echo off 
chcp 65001 >nul 
setlocal enabledelayedexpansion 
 
echo. 
echo ======================================== 
echo 🧹 Temporary Folder Cleanup - Audio Processing Pipeline v2.0 
echo ======================================== 
echo. 
echo This will remove old temporary processing folders. 
echo 🆕 Now includes GPU memory cleanup. 
echo. 
 
:: Check if dry run is requested 
echo 📋 This will delete temporary folders older than 24 hours. 
echo. 
set /p CONFIRM="Continue with cleanup? (y/n): " 
if /i not "!CONFIRM!"=="y" ( 
    echo Cleanup cancelled. 
    echo. 
    echo To see what would be deleted without actually deleting: 
    echo   cleanup_temp.bat --dry-run 
    pause 
    exit /b 0 
) 
echo. 
echo Starting cleanup... 
echo. 
call system\fixes\cleanup_temp_folders.bat 
 
echo. 
echo ✅ Cleanup completed 
echo. 
pause 
