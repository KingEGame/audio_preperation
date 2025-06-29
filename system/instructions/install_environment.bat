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
echo    %L_BLUE%AUDIO PROCESSING ENVIRONMENT%RESET%
echo.
echo    %L_GREEN%Installing dependencies:%RESET%
echo    - PyTorch with CUDA support
echo    - Whisper, Demucs, TorchAudio
echo    - FFmpeg and audio tools
echo    - PyAnnote for speaker diarization
echo.
echo    %L_YELLOW%Note: This installation may take 10-30 minutes%RESET%
echo    %L_YELLOW%Please do not close this window during installation%RESET%
echo.

set INSTALL_DIR=%cd%\audio_environment
set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\audio_environment\env

if not exist "%CONDA_ROOT_PREFIX%\_conda.exe" (
    echo    %L_RED%Portable Conda not found%RESET%
    echo    %L_YELLOW%Installing portable Conda...%RESET%
    call system\instructions\install_portable_conda.bat
    if "%ERRORLEVEL%" NEQ "0" (
        echo    %L_RED%Failed to install portable Conda%RESET%
        echo    %L_YELLOW%Please check your internet connection and try again%RESET%
        exit /b 1
    )
)

if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo    %L_RED%Python environment not found%RESET%
    echo    %L_YELLOW%Creating environment...%RESET%
    "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || (
        echo    %L_RED%Failed to create environment%RESET%
        echo    %L_YELLOW%Please check available disk space and try again%RESET%
        exit /b 1
    )
)

echo    %L_CYAN%Activating environment...%RESET%
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( 
    echo. 
    echo %L_RED%Miniconda hook not found%RESET%
    echo %L_YELLOW%Please check conda installation%RESET%
    exit /b 1 
)

python -c "import sys; print('Python path:', sys.executable)" | findstr "audio_environment" >nul
if "%ERRORLEVEL%" NEQ "0" (
    echo %L_RED%ERROR: Wrong Python%RESET%
    echo Expected: !INSTALL_ENV_DIR!\python.exe
    echo Actual: 
    python -c "import sys; print(sys.executable)"
    exit /b 1
)

echo    %L_YELLOW%Installing dependencies (10-30 minutes)...%RESET%
echo.
echo    %L_CYAN%[1/6] Upgrading pip...%RESET%
python -m pip install --upgrade pip setuptools wheel || (
    echo %L_YELLOW%Warning: Failed to upgrade pip%RESET%
)

echo    %L_CYAN%[2/6] Installing PyTorch...%RESET%
call system\instructions\install_pytorch.bat

echo    %L_CYAN%[3/6] Installing diarization dependencies...%RESET%
echo    %L_YELLOW%Installing build tools...%RESET%

REM Try pip first for build tools to avoid conda warnings
echo    %L_CYAN%Installing build tools via pip...%RESET%
pip install wheel setuptools cmake --upgrade --quiet --disable-pip-version-check 2>nul && (
    echo    %L_GREEN%Build tools installed successfully via pip%RESET%
) || (
    echo %L_YELLOW%Warning: Failed to install cmake via pip, trying conda...%RESET%
    echo %L_CYAN%Continuing with conda installation...%RESET%
    conda install -c conda-forge wheel setuptools cmake -y --quiet --no-deps 2>nul && (
        echo    %L_GREEN%Build tools installed successfully via conda%RESET%
    ) || (
        echo %L_YELLOW%Warning: Failed to install cmake, continuing anyway...%RESET%
        echo %L_CYAN%Some packages may fail to install without cmake%RESET%
    )
)

echo    %L_CYAN%[4/6] Installing sentencepiece...%RESET%
pip install sentencepiece --quiet --disable-pip-version-check 2>nul && (
    echo    %L_GREEN%Sentencepiece installed successfully%RESET%
) || (
    echo %L_YELLOW%Warning: sentencepiece failed, trying alternative installation...%RESET%
    call system\fixes\install_sentencepiece_fixed.bat
    echo %L_CYAN%Continuing with next package...%RESET%
)
echo    %L_CYAN%[5/6] Installing speechbrain...%RESET%
pip install speechbrain>=1.0.0,<2.0.0 --quiet --disable-pip-version-check 2>nul && (
    echo    %L_GREEN%Speechbrain installed successfully%RESET%
) || (
    echo %L_RED%Failed to install speechbrain, trying alternative installation...%RESET%
    call system\fixes\install_speechbrain_fixed.bat
    echo %L_CYAN%Continuing with next package...%RESET%
)  
echo    %L_CYAN%[6/6] Installing remaining dependencies...%RESET%
pip install -r system\requirements\requirements.txt --quiet --disable-pip-version-check 2>nul && (
    echo    %L_GREEN%All dependencies installed successfully%RESET%
) || (
    echo %L_RED%Failed to install some dependencies%RESET%
    echo %L_YELLOW%Some packages may not work correctly%RESET%
    echo %L_CYAN%Continuing with installation...%RESET%
)


echo    %L_CYAN%Installing FFmpeg...%RESET%
call system\instructions\download_ffmpeg.bat

echo.
echo    %L_YELLOW%Install FFmpeg globally (add to PATH)?%RESET%
echo    %L_CYAN%This will make FFmpeg available system-wide%RESET%
set /p GLOBAL_FFMPEG="    Enter Y/N (default: N): "

if /i "!GLOBAL_FFMPEG!"=="Y" (
    echo    %L_CYAN%Installing FFmpeg globally...%RESET%
    call system\instructions\install_ffmpeg_global.bat
) else (
    echo    %L_CYAN%FFmpeg will be available only in this environment%RESET%
)

echo.
echo    %L_CYAN%Creating convenience files...%RESET%

echo @echo off > start_processing.bat
echo set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda >> start_processing.bat
echo set INSTALL_ENV_DIR=%cd%\audio_environment\env >> start_processing.bat
echo call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" >> start_processing.bat
echo. >> start_processing.bat
echo python system\scripts\audio_processing.py >> start_processing.bat
echo. >> start_processing.bat
echo echo [OK] Processing completed >> start_processing.bat
echo pause >> start_processing.bat

echo @echo off > start_concatenate.bat
echo set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda >> start_concatenate.bat
echo set INSTALL_ENV_DIR=%cd%\audio_environment\env >> start_concatenate.bat
echo call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" >> start_concatenate.bat
echo. >> start_concatenate.bat
echo python system\scripts\concatenate_mp3.py >> start_concatenate.bat
echo. >> start_concatenate.bat
echo echo [OK] Processing completed >> start_concatenate.bat
echo pause >> start_concatenate.bat

echo @echo off > start_environment.bat
echo set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda >> start_environment.bat
echo set INSTALL_ENV_DIR=%cd%\audio_environment\env >> start_environment.bat
echo call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" >> start_environment.bat

echo @echo off > cleanup_temp.bat
echo chcp 65001 ^>nul >> cleanup_temp.bat
echo setlocal enabledelayedexpansion >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo echo Temporary Folder Cleanup >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo set /p CONFIRM="Continue with cleanup? (y/n): " >> cleanup_temp.bat
echo if /i not "^!CONFIRM^!"=="y" ^( >> cleanup_temp.bat
echo     echo Cleanup cancelled. >> cleanup_temp.bat
echo     pause >> cleanup_temp.bat
echo     exit /b 0 >> cleanup_temp.bat
echo ^) >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo call system\fixes\cleanup_temp_folders.bat >> cleanup_temp.bat
echo echo [OK] Cleanup completed >> cleanup_temp.bat
echo pause >> cleanup_temp.bat

echo    %L_GREEN%[OK] Files created%RESET%
echo.
echo    %L_CYAN%Available commands:%RESET%
echo    - start_processing.bat - Audio processing (main tool)
echo    - start_concatenate.bat - Concatenate MP3 files
echo    - start_environment.bat - Activate environment manually
echo    - cleanup_temp.bat - Clean temporary files
echo.
echo    %L_CYAN%Next steps:%RESET%
echo    1. Run start_processing.bat to begin audio processing
echo    2. Place your audio files in the input folder

echo    %L_GREEN%[OK] Installation completed successfully!%RESET%
echo    %L_CYAN%You can now use the audio processing tools.%RESET%
echo.
echo    %L_YELLOW%Press any key to close this window...%RESET%
pause >nul 