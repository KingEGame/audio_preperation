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
echo    %L_BLUE%INSTALLING AUDIO PROCESSING ENVIRONMENT%RESET%
echo.
echo    %L_GREEN%This will install all dependencies in the portable Conda environment:%RESET%
echo    - PyTorch with CUDA support (selectable version)
echo    - Whisper, Demucs, TorchAudio
echo    - FFmpeg and other audio tools
echo    - PyAnnote for speaker diarization
echo.
echo    %L_YELLOW%NOTE: This may take 10-30 minutes.%RESET%
echo.

:: Set environment variables
set INSTALL_DIR=%cd%\audio_environment
set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\audio_environment\env

:: Check if portable conda exists
if not exist "%CONDA_ROOT_PREFIX%\_conda.exe" (
    echo    %L_RED%Portable Conda not found!%RESET%
    echo    %L_YELLOW%Installing portable Conda first...%RESET%
    call system\instructions\install_portable_conda.bat
    if "%ERRORLEVEL%" NEQ "0" (
        echo    %L_RED%Failed to install portable Conda!%RESET%
        pause
        exit /b 1
    )
)

:: Check if environment exists
if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo    %L_RED%Python environment not found!%RESET%
    echo    %L_YELLOW%Creating environment...%RESET%
    "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || (
        echo    %L_RED%Failed to create environment!%RESET%
        pause
        exit /b 1
    )
)

:: Activate environment
echo    %L_CYAN%Activating portable environment...%RESET%
@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

:: Verify we're using the right Python
python -c "import sys; print('Python path:', sys.executable)" | findstr "audio_environment" >nul
if "%ERRORLEVEL%" NEQ "0" (
    echo %L_RED%ERROR: Still using wrong Python!%RESET%
    echo Expected: !INSTALL_ENV_DIR!\python.exe
    echo Actual: 
    python -c "import sys; print(sys.executable)"
    exit /b 1
)

echo    %L_YELLOW%Installing all dependencies. This step can take a long time%RESET%
echo    %L_YELLOW%depending on your internet connection and hard drive speed. Please be patient.%RESET%
echo.

:: Upgrade pip and setuptools first
echo    %L_CYAN%Upgrading pip and setuptools...%RESET%
python -m pip install --upgrade pip setuptools wheel || (
    echo %L_YELLOW%Warning: Failed to upgrade pip, continuing...%RESET%
)

:: Install PyTorch with CUDA support FIRST (before other dependencies)
echo    %L_CYAN%Installing PyTorch with CUDA support (FIRST)...%RESET%
echo    %L_YELLOW%This ensures PyTorch is installed before other packages to avoid conflicts.%RESET%
call system\instructions\install_pytorch.bat


:: Setup diarization automatically
echo    %L_CYAN%Installing diarization packages (optional)...%RESET%
echo    %L_YELLOW%Note: These packages may fail if cmake/C++ compiler is not available.%RESET%
echo.
echo    %L_CYAN%Setting up speaker diarization...%RESET%
echo    %L_YELLOW%This will guide you through HuggingFace token setup.%RESET%
echo.
call system\instructions\setup_diarization.bat || (
    echo %L_YELLOW%Warning: Failed to setup diarization, continuing...%RESET%
    pause
    exit /b 1
)

:: Try to install sentencepiece from pre-built wheels
echo    %L_CYAN%Installing sentencepiece from pre-built wheels...%RESET%
pip install sentencepiece || (
    echo %L_YELLOW%Warning: sentencepiece installation failed.%RESET%
    echo %L_YELLOW%This is normal - will use alternative tokenization.%RESET%
    call system\fixes\install_sentencepiece_fixed.bat
)

:: Install remaining dependencies from main requirements file (excluding PyTorch packages)
echo    %L_CYAN%Installing remaining dependencies...%RESET%
echo    %L_YELLOW%Note: PyTorch was installed first, now installing other dependencies...%RESET%

pip install -r ..\requirements\requirements.txt  || (
    echo %L_RED%Failed to install remaining dependencies!%RESET%
    echo Please check the error messages above and try again.
    pause
)

echo %L_CYAN%Install speechbrain%RESET%
pip install speechbrain>=1.0.0,<2.0.0 || (
    echo %L_RED%Failed to install speechbrain!%RESET%
    echo %L_YELLOW%This is normal - will use alternative tokenization.%RESET%
    call system\fixes\install_speechbrain_fixed.bat
)   

:: Install FFmpeg using our download script
echo    %L_CYAN%Installing FFmpeg...%RESET%
call system\instructions\download_ffmpeg.bat

:: Ask if user wants to install FFmpeg globally
echo.
echo    %L_YELLOW%Do you want to install FFmpeg globally (add to system PATH)?%RESET%
echo    This will make FFmpeg available from any command prompt.
set /p GLOBAL_FFMPEG="    Enter Y/N (default: N): "

if /i "!GLOBAL_FFMPEG!"=="Y" (
    echo    %L_CYAN%Installing FFmpeg globally...%RESET%
    call system\instructions\install_ffmpeg_global.bat
)



:: Create convenient bat files in root directory
echo.
echo    %L_CYAN%Creating convenient bat files in root directory...%RESET%

:: Create start_processing.bat
echo @echo off > start_processing.bat
echo cd /D "%~dp0" >> start_processing.bat
echo set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda >> start_processing.bat
echo set INSTALL_ENV_DIR=%cd%\audio_environment\env >> start_processing.bat
echo call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" >> start_processing.bat
echo. >> start_processing.bat
echo python system\scripts\audio_processing.py >> start_processing.bat
echo. >> start_processing.bat
echo echo. >> start_processing.bat
echo echo ✅ Processing completed! >> start_processing.bat
echo echo 📁 Results organized by speakers in the specified folder >> start_processing.bat
echo echo. >> start_processing.bat
echo pause >> start_processing.bat

:: Create activate_environment.bat
@rem Create start_environment.bat to run AllTalk environment
echo @echo off > start_environment.bat
echo cd /D "%~dp0" >> start_environment.bat
echo set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda >> start_environment.bat
echo set INSTALL_ENV_DIR=%cd%\audio_environment\env >> start_environment.bat
echo call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" >> start_environment.bat


:: Create cleanup_temp.bat
echo @echo off > cleanup_temp.bat
echo chcp 65001 ^>nul >> cleanup_temp.bat
echo setlocal enabledelayedexpansion >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo echo ======================================== >> cleanup_temp.bat
echo echo 🧹 Temporary Folder Cleanup - Audio Processing Pipeline v2.0 >> cleanup_temp.bat
echo echo ======================================== >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo echo This will remove old temporary processing folders. >> cleanup_temp.bat
echo echo 🆕 Now includes GPU memory cleanup. >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo :: Check if dry run is requested >> cleanup_temp.bat
echo echo 📋 This will delete temporary folders older than 24 hours. >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo set /p CONFIRM="Continue with cleanup? (y/n): " >> cleanup_temp.bat
echo if /i not "^!CONFIRM^!"=="y" ^( >> cleanup_temp.bat
echo     echo Cleanup cancelled. >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     echo To see what would be deleted without actually deleting: >> cleanup_temp.bat
echo     echo   cleanup_temp.bat --dry-run >> cleanup_temp.bat
echo     pause >> cleanup_temp.bat
echo     exit /b 0 >> cleanup_temp.bat
echo ^) >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo echo Starting cleanup... >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo call system\fixes\cleanup_temp_folders.bat >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo echo ✅ Cleanup completed >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo pause >> cleanup_temp.bat

echo    %L_GREEN%✅ Convenient bat files created in root directory!%RESET%
echo.
echo    %L_CYAN%Available commands:%RESET%
echo    - start_processing.bat - Start interactive audio processing (guided menu)
echo    - activate_environment.bat - Activate environment (open CMD with activated environment)
echo    - cleanup_temp.bat - Clean up temporary folders and files
echo.
echo    %L_CYAN%🆕 New features in v2.0:%RESET%
echo    - Modular architecture with /audio package
echo    - Speaker organization in folders
echo    - Enhanced GPU memory management
echo    - No duration limit option
echo    - Model caching and reuse
echo    - Better error handling and recovery
echo    - Interactive processing mode
echo.

echo    %L_GREEN%Installation completed!%RESET%
echo    %L_GREEN%✅ Environment installed with diarization support!%RESET%
pause 