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
echo    %L_BLUE%SELECTIVE FIXES - Audio Processing Pipeline%RESET%
echo.
echo    %L_GREEN%Choose what to fix:%RESET%
echo.
echo    1) Fix NumPy conflicts (NumPy version issues)
echo    2) Fix SSL/HTTPS issues (download problems)
echo    3) Fix PyTorch installation (CUDA/CPU issues)
echo    4) Fix FFmpeg installation (audio processing issues)
echo    5) Fix Diarization token (HuggingFace access)
echo    6) Fix Environment activation (conda issues)
echo    7) Fix GPU detection (CUDA problems)
echo    8) Fix Dependencies conflicts (package conflicts)
echo.
echo    %L_CYAN%ADVANCED FIXES%RESET%
echo    9) Fix GPU/CUDA support (advanced GPU fix)
echo    10) Fix Diarization access (advanced diarization fix)
echo    11) Install optimized dependencies (performance fix)
echo    12) Install without diarization (minimal setup)
echo    13) Force Install Requirements (force reinstall main requirements)
echo.
echo    %L_CYAN%DIAGNOSTICS%RESET%
echo    14) Check what's broken (diagnose issues)
echo    15) Test everything (full system test)
echo    16) Diagnose FFmpeg issues (FFmpeg error 4294967268)
echo    17) Clean up temporary folders (free disk space)
echo.
echo    %L_RED%0) Back to main menu%RESET%
echo.
set /p UserChoice="    Enter your choice: "

if "%UserChoice%"=="1" goto FixNumPy
if "%UserChoice%"=="2" goto FixSSL
if "%UserChoice%"=="3" goto FixPyTorch
if "%UserChoice%"=="4" goto FixFFmpeg
if "%UserChoice%"=="5" goto FixDiarization
if "%UserChoice%"=="6" goto FixEnvironment
if "%UserChoice%"=="7" goto FixGPU
if "%UserChoice%"=="8" goto FixDependencies
if "%UserChoice%"=="9" goto FixGPUAdvanced
if "%UserChoice%"=="10" goto FixDiarizationAdvanced
if "%UserChoice%"=="11" goto InstallOptimized
if "%UserChoice%"=="12" goto InstallWithoutDiarization
if "%UserChoice%"=="13" goto ForceInstallRequirements
if "%UserChoice%"=="14" goto DiagnoseIssues
if "%UserChoice%"=="15" goto TestEverything
if "%UserChoice%"=="16" goto DiagnoseFFmpeg
if "%UserChoice%"=="17" goto CleanupTempFolders
if "%UserChoice%"=="0" goto End

echo    %L_RED%Invalid choice!%RESET%
pause
goto End

:FixNumPy
echo.
echo    %L_CYAN%Fixing NumPy conflicts...%RESET%
echo    %L_YELLOW%This will reinstall NumPy with compatible version%RESET%
echo.
call system\instructions\activate_environment.bat
echo.
echo    %L_CYAN%Uninstalling current NumPy...%RESET%
pip uninstall numpy -y
echo.
echo    %L_CYAN%Installing compatible NumPy version...%RESET%
pip install "numpy>=1.25.2,<2.0.0" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
echo.
echo    %L_GREEN%✅ NumPy conflicts fixed!%RESET%
pause
goto End

:FixSSL
echo.
echo    %L_CYAN%Fixing SSL/HTTPS issues...%RESET%
echo    %L_YELLOW%This will fix download and connection problems%RESET%
echo.
call system\fixes\fix_ssl_issues.bat
echo.
echo    %L_GREEN%✅ SSL issues fixed!%RESET%
pause
goto End

:FixPyTorch
echo.
echo    %L_CYAN%Fixing PyTorch installation...%RESET%
echo    %L_YELLOW%This will reinstall PyTorch with proper CUDA support%RESET%
echo.
call system\instructions\install_pytorch.bat
echo.
echo    %L_GREEN%✅ PyTorch installation fixed!%RESET%
pause
goto End

:FixFFmpeg
echo.
echo    %L_CYAN%Fixing FFmpeg installation...%RESET%
echo    %L_YELLOW%This will reinstall FFmpeg locally%RESET%
echo.
call system\instructions\download_ffmpeg.bat
echo.
echo    %L_GREEN%✅ FFmpeg installation fixed!%RESET%
pause
goto End

:FixDiarization
echo.
echo    %L_CYAN%Fixing Diarization token...%RESET%
echo    %L_YELLOW%This will help you set up HuggingFace token properly%RESET%
echo.
call system\instructions\setup_diarization.bat
echo.
echo    %L_GREEN%✅ Diarization token fixed!%RESET%
pause
goto End

:FixEnvironment
echo.
echo    %L_CYAN%Fixing Environment activation...%RESET%
echo    %L_YELLOW%This will check and fix conda environment issues%RESET%
echo.
if not exist "audio_environment" (
    echo    %L_RED%❌ Environment not found!%RESET%
    echo    Please run setup.bat and choose option 1 to install environment first.
    pause
    goto End
)
echo    %L_CYAN%Checking environment...%RESET%
call system\instructions\activate_environment.bat
echo.
echo    %L_CYAN%Testing environment activation...%RESET%
python -c "import sys; print('✅ Python version:', sys.version.split()[0])"
if "%ERRORLEVEL%" NEQ "0" (
    echo    %L_RED%❌ Environment activation failed!%RESET%
    echo    Try reinstalling the environment with setup.bat option 1.
) else (
    echo    %L_GREEN%✅ Environment activation fixed!%RESET%
)
pause
goto End

:FixGPU
echo.
echo    %L_CYAN%Fixing GPU detection...%RESET%
echo    %L_YELLOW%This will check and fix CUDA/GPU issues%RESET%
echo.
call system\instructions\test_gpu.bat
echo.
echo    %L_CYAN%Checking PyTorch CUDA support...%RESET%
call system\instructions\activate_environment.bat
python -c "import torch; print('🔥 PyTorch version:', torch.__version__); print('🎮 CUDA available:', torch.cuda.is_available()); print('🎮 CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
echo.
if "%ERRORLEVEL%" NEQ "0" (
    echo    %L_RED%❌ GPU detection failed!%RESET%
    echo    Try fixing PyTorch installation (option 3).
) else (
    echo    %L_GREEN%✅ GPU detection fixed!%RESET%
)
pause
goto End

:FixDependencies
echo.
echo    %L_CYAN%Fixing Dependencies conflicts...%RESET%
echo    %L_YELLOW%This will reinstall conflicting packages%RESET%
echo.
call system\instructions\activate_environment.bat
echo.
echo    %L_CYAN%Upgrading pip and setuptools...%RESET%
pip install --upgrade pip setuptools wheel --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
echo.
echo    %L_CYAN%Reinstalling core dependencies...%RESET%
pip install --force-reinstall --no-deps torch torchaudio --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
echo.
echo    %L_CYAN%Installing missing dependencies...%RESET%
pip install -r system\requirements\requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
echo.
echo    %L_GREEN%✅ Dependencies conflicts fixed!%RESET%
pause
goto End

:FixGPUAdvanced
echo.
echo    %L_CYAN%Advanced GPU/CUDA fix...%RESET%
echo    %L_YELLOW%This will use specialized GPU fix from /fixes folder%RESET%
echo.
call system\fixes\fix_gpu.bat
echo.
echo    %L_GREEN%✅ Advanced GPU fix completed!%RESET%
pause
goto End

:FixDiarizationAdvanced
echo.
echo    %L_CYAN%Advanced Diarization fix...%RESET%
echo    %L_YELLOW%This will use specialized diarization fix from /fixes folder%RESET%
echo.
call system\fixes\fix_diarization_access.bat
echo.
echo    %L_GREEN%✅ Advanced Diarization fix completed!%RESET%
pause
goto End

:InstallOptimized
echo.
echo    %L_CYAN%Installing optimized dependencies...%RESET%
echo    %L_YELLOW%This will install performance-optimized versions%RESET%
echo.
call system\fixes\install_optimized_dependencies.bat
echo.
echo    %L_GREEN%✅ Optimized dependencies installed!%RESET%
pause
goto End

:InstallWithoutDiarization
echo.
echo    %L_CYAN%Installing without diarization...%RESET%
echo    %L_YELLOW%This will create minimal setup without diarization%RESET%
echo.
call system\fixes\install_without_diarization.bat
echo.
echo    %L_GREEN%✅ Minimal setup installed!%RESET%
pause
goto End

:DiagnoseIssues
echo.
echo    %L_CYAN%Diagnosing issues...%RESET%
echo    %L_YELLOW%This will check what's broken in your system%RESET%
echo.
echo    %L_CYAN%1. Checking environment existence...%RESET%
if exist "audio_environment" (
    echo    ✅ Environment exists
) else (
    echo    ❌ Environment not found - run setup.bat option 1
)
echo.
echo    %L_CYAN%2. Checking Python installation...%RESET%
if exist "audio_environment\env\python.exe" (
    echo    ✅ Python installed
) else (
    echo    ❌ Python not found - run setup.bat option 1
)
echo.
echo    %L_CYAN%3. Checking FFmpeg...%RESET%
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
echo.
echo    %L_CYAN%4. Testing environment activation...%RESET%
call system\instructions\activate_environment.bat >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ Environment activates successfully
) else (
    echo    ❌ Environment activation failed
)
echo.
echo    %L_CYAN%5. Checking PyTorch...%RESET%
call system\instructions\activate_environment.bat
python -c "import torch; print('✅ PyTorch version:', torch.__version__)" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ PyTorch works
) else (
    echo    ❌ PyTorch not working
)
echo.
echo    %L_CYAN%6. Checking CUDA...%RESET%
python -c "import torch; print('✅ CUDA available:', torch.cuda.is_available())" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ CUDA check works
) else (
    echo    ❌ CUDA check failed
)
echo.
echo    %L_CYAN%7. Checking diarization token...%RESET%
if exist "%USERPROFILE%\.cache\huggingface\token" (
    echo    ✅ HuggingFace token exists
) else (
    echo    ❌ HuggingFace token not found
)
echo.
echo    %L_GREEN%✅ Diagnosis completed!%RESET%
echo    %L_YELLOW%Use the specific fix options above to resolve issues.%RESET%
pause
goto End

:TestEverything
echo.
echo    %L_CYAN%Testing everything...%RESET%
echo    %L_YELLOW%This will run comprehensive tests%RESET%
echo.
echo    %L_CYAN%1. Testing GPU...%RESET%
call system\instructions\test_gpu.bat
echo.
echo    %L_CYAN%2. Testing diarization token...%RESET%
call system\fixes\test_diarization_token.bat
echo.
echo    %L_CYAN%3. Checking all versions...%RESET%
call system\instructions\check_versions.bat
echo.
echo    %L_CYAN%4. Testing environment...%RESET%
call system\instructions\activate_environment.bat
python -c "import sys, torch, whisper; print('✅ All core packages work')" >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    echo    ✅ Environment test passed
) else (
    echo    ❌ Environment test failed
)
echo.
echo    %L_GREEN%✅ All tests completed!%RESET%
pause
goto End

:DiagnoseFFmpeg
echo.
echo    %L_CYAN%Diagnosing FFmpeg issues...%RESET%
echo    %L_YELLOW%This will check for FFmpeg error 4294967268 and other issues%RESET%
echo.
if not exist "audio_environment" (
    echo    %L_RED%❌ Environment not found!%RESET%
    echo    Please run setup.bat and choose option 1 to install environment first.
    pause
    goto End
)
echo    %L_CYAN%Running FFmpeg diagnostics...%RESET%
call system\fixes\fix_ffmpeg_issues.bat
echo.
echo    %L_GREEN%✅ FFmpeg diagnostics completed!%RESET%
echo    %L_YELLOW%Check the output above for issues and solutions.%RESET%
pause
goto End

:CleanupTempFolders
echo.
echo    %L_CYAN%Cleaning up temporary folders...%RESET%
echo    %L_YELLOW%This will free up disk space by removing old temporary folders%RESET%
echo.
if not exist "audio_environment" (
    echo    %L_RED%❌ Environment not found!%RESET%
    echo    Please run setup.bat and choose option 1 to install environment first.
    pause
    goto End
)
echo    %L_CYAN%First, let's see what would be deleted...%RESET%
call system\fixes\cleanup_temp_folders.bat --dry-run
echo.
echo    %L_YELLOW%Do you want to proceed with cleanup?%RESET%
set /p CONFIRM_CLEANUP="    Enter Y/N (default: N): "
if /i "!CONFIRM_CLEANUP!"=="Y" (
    echo    %L_CYAN%Proceeding with cleanup...%RESET%
    call system\fixes\cleanup_temp_folders.bat
    echo    %L_GREEN%✅ Temporary folders cleaned up!%RESET%
) else (
    echo    %L_YELLOW%Cleanup cancelled.%RESET%
)
pause
goto End

:ForceInstallRequirements
echo.
echo    %L_CYAN%Force installing main requirements...%RESET%
echo    %L_YELLOW%This will reinstall main requirements%RESET%
echo.
call system\fixes\force_install_requirements.bat
echo.
echo    %L_GREEN%✅ Main requirements installed!%RESET%
pause
goto End

:End
echo.
echo    %L_CYAN%Returning to main menu...%RESET% 