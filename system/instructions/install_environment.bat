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

set INSTALL_DIR=%cd%\audio_environment
set CONDA_ROOT_PREFIX=%cd%\audio_environment\conda
set INSTALL_ENV_DIR=%cd%\audio_environment\env

if not exist "%CONDA_ROOT_PREFIX%\_conda.exe" (
    echo    %L_RED%Portable Conda not found%RESET%
    echo    %L_YELLOW%Installing portable Conda...%RESET%
    call system\instructions\install_portable_conda.bat
    if "%ERRORLEVEL%" NEQ "0" (
        echo    %L_RED%Failed to install portable Conda%RESET%
        pause
        exit /b 1
    )
)

if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo    %L_RED%Python environment not found%RESET%
    echo    %L_YELLOW%Creating environment...%RESET%
    "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || (
        echo    %L_RED%Failed to create environment%RESET%
        pause
        exit /b 1
    )
)

echo    %L_CYAN%Activating environment...%RESET%
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )

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

echo    %L_CYAN%Upgrading pip...%RESET%
python -m pip install --upgrade pip setuptools wheel || (
    echo %L_YELLOW%Warning: Failed to upgrade pip%RESET%
)

echo    %L_CYAN%Installing PyTorch...%RESET%
call system\instructions\install_pytorch.bat

echo    %L_CYAN%Installing diarization...%RESET%
echo    %L_YELLOW%Installing build tools...%RESET%
conda install -c conda-forge wheel setuptools cmake -y || (
    echo %L_YELLOW%Warning: Failed to install cmake via conda, trying pip...%RESET%
    pip install wheel setuptools cmake --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_YELLOW%Warning: Failed to install cmake%RESET%
    )
)

echo    %L_CYAN%Installing sentencepiece...%RESET%
pip install sentencepiece || (
    echo %L_YELLOW%Warning: sentencepiece failed%RESET%
    call system\fixes\install_sentencepiece_fixed.bat
)
echo    %L_CYAN%Installing speechbrain...%RESET%
pip install speechbrain>=1.0.0,<2.0.0 || (
    echo %L_RED%Failed to install speechbrain%RESET%
    call system\fixes\install_speechbrain_fixed.bat
)  
echo    %L_CYAN%Installing remaining dependencies...%RESET%
pip install -r system\requirements\requirements.txt  || (
    echo %L_RED%Failed to install dependencies%RESET%
    pause
)


echo    %L_CYAN%Installing FFmpeg...%RESET%
call system\instructions\download_ffmpeg.bat

echo.
echo    %L_YELLOW%Install FFmpeg globally (add to PATH)?%RESET%
set /p GLOBAL_FFMPEG="    Enter Y/N (default: N): "

if /i "!GLOBAL_FFMPEG!"=="Y" (
    echo    %L_CYAN%Installing FFmpeg globally...%RESET%
    call system\instructions\install_ffmpeg_global.bat
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
echo    - start_processing.bat - Audio processing
echo    - activate_environment.bat - Activate environment
echo    - cleanup_temp.bat - Clean temporary files
echo.

echo    %L_GREEN%[OK] Installation completed%RESET%
pause 