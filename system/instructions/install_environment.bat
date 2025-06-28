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
echo    %L_GREEN%This will create/update a Conda environment with dependencies:%RESET%
echo    - Python 3.11
echo    - PyTorch with CUDA support (selectable version)
echo    - Whisper, Demucs, TorchAudio
echo    - FFmpeg and other audio tools
echo    - PyAnnote for speaker diarization
echo.
echo    %L_YELLOW%NOTE: This may take 10-30 minutes.%RESET%
echo.
pause

:: Set environment variables
set "INSTALL_DIR=%cd%\audio_environment"
set "CONDA_ROOT_PREFIX=%cd%\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\audio_environment\env"
set "MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "conda_exists=F"

:: Check if conda already exists
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    set conda_exists=T
    call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%"
    goto RunScript
)

:: Download and install conda if not installed
echo.
echo    %L_CYAN%Downloading Miniconda from %MINICONDA_URL% to %INSTALL_DIR%\miniconda_installer.exe%RESET%
mkdir "%INSTALL_DIR%"
call curl -Lk "%MINICONDA_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || (
    echo. && echo %L_RED%Miniconda failed to download.%RESET% && pause && exit /b 1
)

echo    %L_GREEN%Installing Miniconda to %CONDA_ROOT_PREFIX%%RESET%
start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%

echo    %L_CYAN%Miniconda version:%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || (
    echo. && echo %L_RED%Miniconda not found.%RESET% && pause && exit /b 1
)

:: Initialize conda for the current shell
echo    %L_CYAN%Initializing conda...%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" init cmd.exe --all --quiet || (
    echo. && echo %L_YELLOW%Warning: Conda init failed, but continuing...%RESET%
)

:: Create the installer env
echo.
echo    %L_GREEN%Creating Python 3.11 environment...%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || (
    echo. && echo %L_RED%Conda environment creation failed.%RESET% && pause && exit /b 1
)

:: Check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo. && echo %L_RED%Conda environment is empty.%RESET% && pause && exit /b 1
)

:: Activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || (
    echo. && echo %L_RED%Miniconda hook not found.%RESET% && pause && exit /b 1
)

:RunScript
echo.
echo    %L_YELLOW%Installing all dependencies from requirements.txt. This step can take a long time%RESET%
echo    %L_YELLOW%depending on your internet connection and hard drive speed. Please be patient.%RESET%
echo.

:: Install compatible NumPy version first
echo    %L_CYAN%Installing compatible NumPy version...%RESET%
pip install "numpy>=1.25.2,<2.0.0" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_RED%Failed to install compatible NumPy version!%RESET%
    pause
    exit /b 1
)

:: Install build tools
echo    %L_CYAN%Installing build tools...%RESET%
pip install wheel setuptools --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to upgrade build tools, continuing...%RESET%
)

:: Install PyTorch with CUDA support using separate module
echo    %L_CYAN%Installing PyTorch with CUDA support...%RESET%
call system\instructions\install_pytorch.bat

:: Install remaining dependencies
echo    %L_CYAN%Installing remaining dependencies...%RESET%
pip install -r system\requirements\requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_RED%Failed to install requirements from requirements.txt!%RESET%
    echo Please check the error messages above and try again.
    pause
    exit /b 1
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

:: Setup diarization automatically
echo.
echo    %L_CYAN%Setting up speaker diarization...%RESET%
echo    %L_YELLOW%This will guide you through HuggingFace token setup.%RESET%
echo.
call system\instructions\setup_diarization.bat

:: Create convenient bat files in root directory
echo.
echo    %L_CYAN%Creating convenient bat files in root directory...%RESET%

:: Create start_processing.bat
echo @echo off > start_processing.bat
echo chcp 65001 ^>nul >> start_processing.bat
echo setlocal enabledelayedexpansion >> start_processing.bat
echo. >> start_processing.bat
echo echo. >> start_processing.bat
echo echo ======================================== >> start_processing.bat
echo echo 🎵 Audio Processing Pipeline >> start_processing.bat
echo echo ======================================== >> start_processing.bat
echo echo. >> start_processing.bat
echo. >> start_processing.bat
echo :: Check if environment exists >> start_processing.bat
echo if not exist "audio_environment" ^( >> start_processing.bat
echo     echo ❌ Environment not found! >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> start_processing.bat
echo     echo. >> start_processing.bat
echo     pause >> start_processing.bat
echo     exit /b 1 >> start_processing.bat
echo ^) >> start_processing.bat
echo. >> start_processing.bat
echo :: Activate environment >> start_processing.bat
echo call system\instructions\activate_environment.bat >> start_processing.bat
echo. >> start_processing.bat
echo :: Check if parameters are passed >> start_processing.bat
echo if "%%~1"=="" ^( >> start_processing.bat
echo     echo 📋 Usage: >> start_processing.bat
echo     echo start_processing.bat --input "audio.mp3" --output "results" >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo 📝 Examples: >> start_processing.bat
echo     echo start_processing.bat --input "lecture.mp3" --output "lecture_results" >> start_processing.bat
echo     echo start_processing.bat --input "meeting.mp3" --output "results" --steps split denoise vad diar >> start_processing.bat
echo     echo start_processing.bat --input "audio.mp3" --output "results" --create_final_chunks --final_chunk_duration 30 >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo 💡 For detailed help: start_processing.bat --help >> start_processing.bat
echo     echo. >> start_processing.bat
echo     pause >> start_processing.bat
echo     exit /b 0 >> start_processing.bat
echo ^) >> start_processing.bat
echo. >> start_processing.bat
echo :: Start processing >> start_processing.bat
echo echo 🚀 Starting audio processing... >> start_processing.bat
echo echo. >> start_processing.bat
echo. >> start_processing.bat
echo python scripts\audio_processing.py %%* >> start_processing.bat
echo. >> start_processing.bat
echo echo. >> start_processing.bat
echo echo ✅ Processing completed! >> start_processing.bat
echo echo 📁 Results saved in the specified folder >> start_processing.bat
echo echo. >> start_processing.bat
echo pause >> start_processing.bat

:: Create activate_environment.bat
echo @echo off > activate_environment.bat
echo chcp 65001 ^>nul >> activate_environment.bat
echo setlocal enabledelayedexpansion >> activate_environment.bat
echo. >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo ======================================== >> activate_environment.bat
echo echo 🐍 Activate Environment - Audio Processing Pipeline >> activate_environment.bat
echo echo ======================================== >> activate_environment.bat
echo echo. >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Check if environment exists >> activate_environment.bat
echo if not exist "audio_environment" ^( >> activate_environment.bat
echo     echo ❌ Environment not found! >> activate_environment.bat
echo     echo. >> activate_environment.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> activate_environment.bat
echo     echo. >> activate_environment.bat
echo     pause >> activate_environment.bat
echo     exit /b 1 >> activate_environment.bat
echo ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Activate environment >> activate_environment.bat
echo call system\instructions\activate_environment.bat >> activate_environment.bat
echo. >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo ✅ Environment activated! >> activate_environment.bat
echo echo 🐍 Now you can use Python commands >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo 💡 Example commands: >> activate_environment.bat
echo echo   python scripts\audio_processing.py --help >> activate_environment.bat
echo echo   python scripts\test_gpu.py >> activate_environment.bat
echo echo   python -c "import torch; print(torch.__version__)" >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo 🔄 To deactivate, enter: conda deactivate >> activate_environment.bat
echo echo. >> activate_environment.bat

:: Create audio_concat.bat
echo @echo off > audio_concat.bat
echo chcp 65001 ^>nul >> audio_concat.bat
echo setlocal enabledelayedexpansion >> audio_concat.bat
echo. >> audio_concat.bat
echo echo. >> audio_concat.bat
echo echo ======================================== >> audio_concat.bat
echo echo 🔗 Audio Concatenation - Audio Processing Pipeline >> audio_concat.bat
echo echo ======================================== >> audio_concat.bat
echo echo. >> audio_concat.bat
echo. >> audio_concat.bat
echo :: Check if environment exists >> audio_concat.bat
echo if not exist "audio_environment" ^( >> audio_concat.bat
echo     echo ❌ Environment not found! >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     pause >> audio_concat.bat
echo     exit /b 1 >> audio_concat.bat
echo ^) >> audio_concat.bat
echo. >> audio_concat.bat
echo :: Activate environment >> audio_concat.bat
echo call system\instructions\activate_environment.bat >> audio_concat.bat
echo. >> audio_concat.bat
echo :: Check if parameters are passed >> audio_concat.bat
echo if "%%~1"=="" ^( >> audio_concat.bat
echo     echo 📋 Usage: >> audio_concat.bat
echo     echo audio_concat.bat "input_folder" "output_file.mp3" >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     echo 📝 Examples: >> audio_concat.bat
echo     echo audio_concat.bat "chunks" "combined_audio.mp3" >> audio_concat.bat
echo     echo audio_concat.bat "results" "final_audio.mp3" >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     echo 💡 Combines all MP3 files from the folder into one file >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     pause >> audio_concat.bat
echo     exit /b 0 >> audio_concat.bat
echo ^) >> audio_concat.bat
echo. >> audio_concat.bat
echo :: Start concatenation >> audio_concat.bat
echo echo 🚀 Starting audio concatenation... >> audio_concat.bat
echo echo. >> audio_concat.bat
echo. >> audio_concat.bat
echo python scripts\concatenate_mp3.py "%%~1" "%%~2" >> audio_concat.bat
echo. >> audio_concat.bat
echo echo. >> audio_concat.bat
echo echo ✅ Concatenation completed! >> audio_concat.bat
echo echo 📁 Result saved in: %%2 >> audio_concat.bat
echo echo. >> audio_concat.bat
echo pause >> audio_concat.bat

echo    %L_GREEN%✅ Convenient bat files created in root directory!%RESET%
echo.
echo    %L_CYAN%Available commands:%RESET%
echo    - start_processing.bat - Start audio processing
echo    - activate_environment.bat - Activate environment
echo    - audio_concat.bat - Concatenate audio files
echo.

echo    %L_GREEN%Installation completed!%RESET%
echo    %L_GREEN%✅ Environment installed with diarization support!%RESET%
pause 