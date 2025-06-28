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
echo    %L_BLUE%COMPREHENSIVE SYSTEM TEST%RESET%
echo    %L_YELLOW%Testing everything that was installed...%RESET%
echo.

:: Test 1: Environment existence
echo    %L_CYAN%1. Testing environment existence...%RESET%
if exist "audio_environment" (
    echo    ✅ Environment exists
) else (
    echo    ❌ Environment not found - run setup.bat option 1
    pause
    exit /b 1
)

:: Test 2: Python installation
echo    %L_CYAN%2. Testing Python installation...%RESET%
if exist "audio_environment\env\python.exe" (
    echo    ✅ Python installed
) else (
    echo    ❌ Python not found - run setup.bat option 1
    pause
    exit /b 1
)

:: Test 3: Environment activation
echo    %L_CYAN%3. Testing environment activation...%RESET%
call system\instructions\activate_environment.bat >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ Environment activates successfully
) else (
    echo    ❌ Environment activation failed
    pause
    exit /b 1
)

:: Test 4: Core packages
echo    %L_CYAN%4. Testing core packages...%RESET%
call system\instructions\activate_environment.bat
python -c "import sys; print('✅ Python version:', sys.version.split()[0])" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ Python works
) else (
    echo    ❌ Python not working
    pause
    exit /b 1
)

:: Test 5: PyTorch
echo    %L_CYAN%5. Testing PyTorch...%RESET%
python -c "import torch; print('✅ PyTorch version:', torch.__version__)" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ PyTorch works
) else (
    echo    ❌ PyTorch not working
)

:: Test 6: GPU/CUDA
echo    %L_CYAN%6. Testing GPU/CUDA...%RESET%
call system\instructions\test_gpu.bat

:: Test 7: FFmpeg
echo    %L_CYAN%7. Testing FFmpeg...%RESET%
if exist "system\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" (
    echo    ✅ FFmpeg installed locally
) else (
    echo    ❌ FFmpeg not found locally
)
ffmpeg -version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ FFmpeg available globally
) else (
    echo    ❌ FFmpeg not available globally
)

:: Test 8: Diarization token
echo    %L_CYAN%8. Testing diarization token...%RESET%
call system\instructions\test_diarization_token.bat

:: Test 9: All versions
echo    %L_CYAN%9. Checking all versions...%RESET%
call system\instructions\check_versions.bat

:: Test 10: Core functionality
echo    %L_CYAN%10. Testing core functionality...%RESET%
call system\instructions\activate_environment.bat
python -c "import torch, whisper; print('✅ Core packages import successfully')" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ Core functionality works
) else (
    echo    ❌ Core functionality failed
)

echo.
echo    %L_GREEN%✅ Comprehensive system test completed!%RESET%
echo    %L_YELLOW%If any tests failed, use setup.bat option 4 to fix specific issues.%RESET%
pause 