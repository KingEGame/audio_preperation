@echo off
setlocal enabledelayedexpansion

for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_CYAN=%ESC%[96m"
set "L_BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

echo.
echo    %L_BLUE%SYSTEM TEST%RESET%
echo.

echo    %L_CYAN%1. Environment existence...%RESET%
if exist "audio_environment" (
    echo    [OK] Environment exists
) else (
    echo    [ERROR] Environment not found
    pause
    exit /b 1
)

echo    %L_CYAN%2. Python installation...%RESET%
if exist "audio_environment\env\python.exe" (
    echo    [OK] Python installed
) else (
    echo    [ERROR] Python not found
    pause
    exit /b 1
)

echo    %L_CYAN%3. Environment activation...%RESET%
call system\instructions\activate_environment.bat >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    [OK] Environment activates
) else (
    echo    [ERROR] Environment activation failed
    pause
    exit /b 1
)

echo    %L_CYAN%4. Core packages...%RESET%
call system\instructions\activate_environment.bat
python -c "import sys; print('[OK] Python version:', sys.version.split()[0])" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    [OK] Python works
) else (
    echo    [ERROR] Python not working
    pause
    exit /b 1
)

echo    %L_CYAN%5. PyTorch...%RESET%
python -c "import torch; print('[OK] PyTorch version:', torch.__version__)" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    [OK] PyTorch works
) else (
    echo    [ERROR] PyTorch not working
)

echo    %L_CYAN%6. GPU/CUDA...%RESET%
call system\instructions\test_gpu.bat

echo    %L_CYAN%7. FFmpeg...%RESET%
if exist "system\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" (
    echo    [OK] FFmpeg installed locally
) else (
    echo    [ERROR] FFmpeg not found locally
)
ffmpeg -version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    [OK] FFmpeg available globally
) else (
    echo    [ERROR] FFmpeg not available globally
)

echo    %L_CYAN%8. Diarization token...%RESET%
call system\instructions\test_diarization_token.bat

echo    %L_CYAN%9. All versions...%RESET%
call system\instructions\check_versions.bat

echo    %L_CYAN%10. Core functionality...%RESET%
call system\instructions\activate_environment.bat
python -c "import torch, whisper; print('[OK] Core packages import successfully')" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    [OK] Core functionality works
) else (
    echo    [ERROR] Core functionality failed
)

echo.
echo    %L_GREEN%[OK] System test completed%RESET%
pause 