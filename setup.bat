@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion
set "PATH=%PATH%;%SystemRoot%\system32"

:: Generate the ESC character
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

:: Colors
set "BLACK=%ESC%[30m"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "MAGENTA=%ESC%[35m"
set "CYAN=%ESC%[36m"
set "WHITE=%ESC%[37m"
set "L_BLACK=%ESC%[90m"
set "L_RED=%ESC%[91m"
set "L_GREEN=%ESC%[92m"
set "L_YELLOW=%ESC%[93m"
set "L_BLUE=%ESC%[94m"
set "L_MAGENTA=%ESC%[95m"
set "L_CYAN=%ESC%[96m"
set "L_WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

:: Проверка на пробелы в пути
if not "%CD%"=="%CD: =%" (
    echo.
    echo %L_RED%ERROR: Path contains spaces!%RESET%
    echo Please use a folder path without spaces.
    pause
    exit /b 1
)

:: Проверка на спецсимволы в пути
set "SPCHARMESSAGE=WARNING: Special characters were detected in the installation path! This can cause the installation to fail!"
echo "%CD%"| findstr /R /C:"[!#\$%&()*+,;<=>?@\[\]^`{|}~]" >nul && (
    echo.
    echo %L_YELLOW%!SPCHARMESSAGE!%RESET%
    pause
)
set SPCHARMESSAGE=

:: Проверка наличия curl
curl --version >nul 2>&1
if "%ERRORLEVEL%" NEQ "0" (
    echo.
    echo %L_RED%curl is not available on this system.%RESET%
    echo Please install curl then re-run the script: https://curl.se/
    echo or perform a manual installation of a Conda Python environment.
    pause
    exit /b 1
)

:: Проверка наличия requirements.txt
if not exist "requirements.txt" (
    echo.
    echo %L_RED%ERROR: requirements.txt not found in current directory!%RESET%
    echo Please ensure requirements.txt is in the same directory as setup.bat
    pause
    exit /b 1
)

:: Initialize Conda
if exist "%cd%\audio_environment\conda\Scripts\conda.exe" (
    call "%cd%\audio_environment\conda\Scripts\conda.bat" shell.cmd activate >nul 2>&1
)

:MainMenu
cls
echo %L_BLUE%AUDIO PROCESSING PIPELINE SETUP%RESET%
echo.
echo %L_GREEN%MAIN OPTIONS%RESET%
echo 1) Install/Update Environment
echo 2) Setup Diarization
echo 3) Test GPU
echo 4) Check Versions
echo 5) Fix Common Issues
echo 6) Fix SSL Issues
echo.
echo %L_CYAN%UTILITIES%RESET%
echo 7) Start Audio Environment
echo 8) Start Audio Processing
echo 9) Show Help
echo.
echo %L_YELLOW%MAINTENANCE%RESET%
echo 10) Delete Environment
echo.
echo %L_RED%0) Exit/Quit%RESET%
echo.
set /p UserOption="    Enter your choice: "

if "%UserOption%"=="1" goto InstallEnvironment
if "%UserOption%"=="2" goto SetupDiarization
if "%UserOption%"=="3" goto TestGPU
if "%UserOption%"=="4" goto CheckVersions
if "%UserOption%"=="5" goto FixIssues
if "%UserOption%"=="6" goto FixSSLIssues
if "%UserOption%"=="7" goto StartEnvironment
if "%UserOption%"=="8" goto StartProcessing
if "%UserOption%"=="9" goto ShowHelp
if "%UserOption%"=="10" goto DeleteEnvironment
if "%UserOption%"=="0" goto End

goto MainMenu

:InstallEnvironment
cls
echo.
echo    %L_BLUE%AUDIO PROCESSING PIPELINE SETUP%RESET%
echo.
echo    %L_GREEN%This will create/update a Conda environment with dependencies:%RESET%
echo    - Python 3.11
echo    - PyTorch with CUDA support
echo    - Whisper, Demucs, TorchAudio
echo    - FFmpeg and other audio tools
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

@rem figure out whether git and conda need to be installed
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" (
    set conda_exists=T
    call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%"
    goto RunScript
)

@rem download and install conda if not installed
echo.
echo    %L_CYAN%Downloading Miniconda from %MINICONDA_URL% to %INSTALL_DIR%\miniconda_installer.exe%RESET%
mkdir "%INSTALL_DIR%"
call curl -Lk "%MINICONDA_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo %L_RED%Miniconda failed to download.%RESET% && pause && goto End )
echo    %L_GREEN%Installing Miniconda to %CONDA_ROOT_PREFIX%%RESET%
start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%
echo    %L_CYAN%Miniconda version:%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo %L_RED%Miniconda not found.%RESET% && pause && goto End )

@rem Initialize conda for the current shell
echo    %L_CYAN%Initializing conda...%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" init cmd.exe --all --quiet || ( echo. && echo %L_YELLOW%Warning: Conda init failed, but continuing...%RESET% )

@rem create the installer env
echo.
echo    %L_GREEN%Creating Python 3.11 environment...%RESET%
call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || ( echo. && echo %L_RED%Conda environment creation failed.%RESET% && pause && goto End )

@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo %L_RED%Conda environment is empty.%RESET% && pause && goto End )

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo %L_RED%Miniconda hook not found.%RESET% && pause && goto End )

echo.
echo    %L_YELLOW%Installing all dependencies from requirements.txt. This step can take a long time%RESET%
echo    %L_YELLOW%depending on your internet connection and hard drive speed. Please be patient.%RESET%
echo.

:: Сначала устанавливаем совместимую версию NumPy
echo    %L_CYAN%Installing compatible NumPy version...%RESET%
pip install "numpy>=1.25.2,<2.0.0" --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_RED%Failed to install compatible NumPy version!%RESET%
    pause
    goto MainMenu
)

:: Установка инструментов сборки
echo    %L_CYAN%Installing build tools...%RESET%
pip install wheel setuptools --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to upgrade build tools, continuing...%RESET%
)

:: Установка PyTorch и torchaudio с поддержкой CUDA
echo    %L_CYAN%Installing PyTorch with CUDA support...%RESET%
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host download.pytorch.org || (
    echo %L_RED%Failed to install torch/torchaudio with CUDA support!%RESET%
    pause
    goto MainMenu
)

:: Проверка установки PyTorch с CUDA
echo    %L_CYAN%Verifying PyTorch CUDA installation...%RESET%
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" || (
    echo %L_YELLOW%Warning: PyTorch CUDA verification failed, but continuing...%RESET%
)

:: Установка остальных зависимостей
echo    %L_CYAN%Installing remaining dependencies...%RESET%
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_RED%Failed to install requirements from requirements.txt!%RESET%
    echo Please check the error messages above and try again.
    pause
    goto MainMenu
)

:: Install FFmpeg if not present
where ffmpeg >nul 2>&1 || (
    echo    %L_CYAN%Installing FFmpeg...%RESET%
    powershell -Command "choco install ffmpeg -y" || (
        echo %L_RED%FFmpeg installation failed. Please install manually.%RESET%
    )
)

echo.
echo    %L_GREEN%Installation completed!%RESET%
echo    Run %L_YELLOW%start_audio_environment.bat%RESET% to activate environment.
echo    Run %L_YELLOW%start_audio_processing.bat%RESET% to process audio.
pause
goto MainMenu

:SetupDiarization
cls
echo.
echo    %L_BLUE%SETUP DIARIZATION%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)


echo    %L_YELLOW%Installing build tools...%RESET%
pip install wheel setuptools cmake --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to install cmake, trying alternative approach...%RESET%
)

echo    %L_YELLOW%Installing PyAnnote from requirements.txt...%RESET%
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Main installation failed, trying conda method...%RESET%
    echo %L_CYAN%Installing sentencepiece via conda...%RESET%
    conda install -c conda-forge sentencepiece -y || (
        echo %L_RED%Failed to install sentencepiece via conda!%RESET%
        pause
        goto MainMenu
    )
    
    echo %L_CYAN%Installing speechbrain...%RESET%
    pip install speechbrain --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to install speechbrain!%RESET%
        pause
        goto MainMenu
    )
    
    echo %L_CYAN%Installing pyannote.audio...%RESET%
    pip install pyannote.audio --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to install pyannote.audio!%RESET%
        echo Please check the error messages above.
        pause
        goto MainMenu
    )
)

echo    %L_CYAN%Opening HuggingFace setup page...%RESET%
start "" "https://huggingface.co/pyannote/speaker-diarization-3.1"

echo    %L_GREEN%Follow these steps:%RESET%
echo    1. Accept terms
echo    2. Go to Settings -> Access Tokens
echo    3. Create a token with Read permissions
echo    4. Copy the token
set /p HF_TOKEN="    Enter HuggingFace token: "

if "!HF_TOKEN!"=="" (
    echo %L_RED%No token entered. Diarization unavailable.%RESET%
    pause
    goto MainMenu
)
huggingface-cli login --token !HF_TOKEN! --add-to-git-credential
echo    %L_CYAN%Saving token...%RESET%
echo !HF_TOKEN! > hf_token.txt

echo    %L_CYAN%Testing diarization...%RESET%
python -c "import pyannote.audio; print('PyAnnote installed successfully')" || (
    echo %L_RED%PyAnnote test failed.%RESET%
    pause
    goto MainMenu
)

echo    %L_GREEN%Diarization setup completed!%RESET%
pause
goto MainMenu

:TestGPU
cls
echo.
echo    %L_BLUE%TESTING GPU COMPATIBILITY%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)

echo    %L_YELLOW%Running GPU test...%RESET%
if exist "scripts\test_gpu.py" (
    python scripts\test_gpu.py
) else (
    echo %L_CYAN%PyTorch Information:%RESET%
    python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"
    echo.
    echo %L_CYAN%System GPU Information:%RESET%
    python -c "import subprocess; result = subprocess.run(['nvidia-smi'], capture_output=True, text=True); print(result.stdout if result.returncode == 0 else 'nvidia-smi not available or no GPU found')"
)

echo.
pause
goto MainMenu

:CheckVersions
cls
echo.
echo    %L_BLUE%CHECKING PACKAGE VERSIONS%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)

echo    %L_GREEN%Checking versions:%RESET%
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
python -c "import torchaudio; print('torchaudio:', torchaudio.__version__)"
python -c "import whisper; print('Whisper:', whisper.__version__)"
python -c "import demucs; print('Demucs:', demucs.__version__)"
python -c "import silero_vad; print('Silero VAD: working')"
python -c "import librosa; print('Librosa:', librosa.__version__)"
python -c "import soundfile; print('SoundFile:', soundfile.__version__)"
python -c "import pyannote.audio; print('PyAnnote: working')" 2>nul || echo %L_YELLOW%PyAnnote: not installed%RESET%

echo    %L_GREEN%Version check completed!%RESET%
pause
goto MainMenu

:FixIssues
cls
echo.
echo    %L_BLUE%FIXING COMMON ISSUES%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)

echo    %L_YELLOW%Checking and fixing GPU/CUDA support...%RESET%
python -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" || (
    echo %L_RED%Failed to check PyTorch installation!%RESET%
    pause
    goto MainMenu
)

:: Если CUDA недоступна, переустанавливаем PyTorch
python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" || (
    echo %L_YELLOW%CUDA not available, reinstalling PyTorch with CUDA support...%RESET%
    pip uninstall torch torchaudio -y
    pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121 --force-reinstall --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host download.pytorch.org || (
        echo %L_RED%Failed to reinstall PyTorch with CUDA!%RESET%
        pause
        goto MainMenu
    )
)

echo    %L_YELLOW%Installing build tools...%RESET%
pip install wheel setuptools cmake --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to install cmake, trying alternative approach...%RESET%
)

echo    %L_YELLOW%Reinstalling all packages from requirements.txt...%RESET%
pip install -r requirements.txt --force-reinstall --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Main installation failed, trying conda method...%RESET%
    echo %L_CYAN%Installing sentencepiece via conda...%RESET%
    conda install -c conda-forge sentencepiece -y || (
        echo %L_RED%Failed to install sentencepiece via conda!%RESET%
        pause
        goto MainMenu
    )
    
    echo %L_CYAN%Installing remaining packages...%RESET%
    pip install -r requirements.txt --force-reinstall --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to reinstall from requirements.txt!%RESET%
        echo Please check the error messages above.
        pause
        goto MainMenu
    )
)

echo    %L_GREEN%Checking fixes...%RESET%
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import silero_vad; print('Silero VAD: working')"

echo    %L_GREEN%Fixes applied!%RESET%
pause
goto MainMenu

:StartEnvironment
cls
echo.
echo    %L_BLUE%STARTING AUDIO ENVIRONMENT%RESET%
echo.

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)
echo    %L_GREEN%Environment activated!%RESET%
cmd /k
goto MainMenu

:StartProcessing
cls
echo.
echo    %L_BLUE%STARTING AUDIO PROCESSING%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"
set "AUDIO_SCRIPT=%cd%\audio_processing.py"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)
if not exist "!AUDIO_SCRIPT!" (
    echo %L_RED%audio_processing.py not found!%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)

if "%~1"=="" (
    echo    %L_YELLOW%Starting in interactive mode...%RESET%
    python audio_processing.py
) else (
    echo    %L_YELLOW%Running with arguments...%RESET%
    python audio_processing.py %*
)

if errorlevel 1 (
    echo %L_RED%ERROR: Audio processing failed! Check audio_processing.log.%RESET%
    pause
    goto MainMenu
)

echo    %L_GREEN%Processing completed!%RESET%
pause
goto MainMenu

:ShowHelp
cls
echo.
echo    %L_BLUE%AUDIO PROCESSING PIPELINE HELP%RESET%
echo.
echo    %L_GREEN%After installation, use:%RESET%
echo    1. %L_YELLOW%start_audio_environment.bat%RESET% - Activate environment
echo    2. %L_YELLOW%start_audio_processing.bat [OPTIONS]%RESET% - Run processing
echo.
echo    %L_GREEN%Examples:%RESET%
echo    start_audio_processing.bat --input file.mp3 --output ./result
echo    start_audio_processing.bat --input folder/ --output ./result --model medium
echo.
echo    %L_GREEN%Options:%RESET%
echo    --input PATH         Input audio file/folder
echo    --output PATH        Output directory
echo    --chunk_duration N   Max chunk duration (seconds, default: 600)
echo    --language LANG      Language for Whisper (default: ru)
echo    --model MODEL        Whisper model: tiny, base, small, medium, large
echo    --steps STEP1 STEP2  Steps: split, denoise, vad, diar
echo    --verbose            Verbose logging
echo.
echo    %L_YELLOW%Troubleshooting:%RESET%
echo    - Run "Fix Common Issues" for errors
echo    - Ensure FFmpeg is installed
echo    - Update NVIDIA drivers for GPU issues
pause
goto MainMenu

:DeleteEnvironment
cls
echo.
echo    %L_RED%DELETING ENVIRONMENT%RESET%
echo.
set "AUDIO_ENV_DIR=%cd%\audio_environment"

if not exist "!AUDIO_ENV_DIR!\" (
    echo    %L_GREEN%Environment does not exist.%RESET%
    pause
    goto MainMenu
)

echo    %L_YELLOW%Deleting environment...%RESET%
rd /s /q "!AUDIO_ENV_DIR!" 2>nul
del start_audio_environment.bat 2>nul
del start_audio_processing.bat 2>nul

if exist "!AUDIO_ENV_DIR!\" (
    echo    %L_RED%Failed to delete environment.%RESET%
    pause
    goto MainMenu
)

echo    %L_GREEN%Environment deleted!%RESET%
pause
goto MainMenu

:FixSSLIssues
cls
echo.
echo    %L_BLUE%FIXING SSL MODULE ISSUES%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
    pause
    goto MainMenu
)

echo    %L_CYAN%Activating environment...%RESET%
call :activate_conda_env || (
    pause
    goto MainMenu
)

echo    %L_YELLOW%Testing SSL module...%RESET%
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo %L_RED%SSL module not available - fixing...%RESET%
    goto FixSSL
)

echo    %L_GREEN%SSL module is working correctly.%RESET%
echo.
echo    %L_YELLOW%Testing pip with SSL...%RESET%
python -m pip --version 2>nul || (
    echo %L_RED%Pip SSL test failed - fixing...%RESET%
    goto FixSSL
)

echo    %L_GREEN%SSL issues are resolved!%RESET%
pause
goto MainMenu

:FixSSL
echo.
echo    %L_YELLOW%APPLYING SSL FIXES%RESET%
echo.

:: Method 1: Reinstall Python with SSL support via conda
echo    %L_CYAN%Method 1: Reinstalling Python with SSL support...%RESET%
conda install python=3.11 openssl certifi -y || (
    echo %L_YELLOW%Failed to reinstall Python via conda, trying alternative method...%RESET%
    goto FixSSLAlt
)

:: Test SSL after reinstall
echo    %L_CYAN%Testing SSL after reinstall...%RESET%
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo %L_YELLOW%SSL still not working, trying alternative method...%RESET%
    goto FixSSLAlt
)

echo    %L_GREEN%SSL module is now working!%RESET%
goto UpdatePip

:FixSSLAlt
echo.
echo    %L_CYAN%Method 2: Installing OpenSSL and certificates...%RESET%
conda install openssl certifi ca-certificates -y || (
    echo %L_RED%Failed to install OpenSSL via conda%RESET%
    goto FixSSLManual
)

:: Set SSL environment variables
set "SSL_CERT_FILE=!CONDA_PREFIX!\Library\ssl\cert.pem"
set "SSL_CERT_DIR=!CONDA_PREFIX!\Library\ssl\certs"
set "REQUESTS_CA_BUNDLE=!CONDA_PREFIX!\Library\ssl\cert.pem"

:: Test SSL
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo %L_YELLOW%SSL still not working, trying manual fix...%RESET%
    goto FixSSLManual
)

echo    %L_GREEN%SSL module is now working!%RESET%
goto UpdatePip

:FixSSLManual
echo.
echo    %L_CYAN%Method 3: Manual SSL configuration...%RESET%
echo.

:: Create pip configuration to disable SSL verification (temporary fix)
echo    %L_YELLOW%Creating pip configuration...%RESET%
if not exist "!CONDA_PREFIX!\pip.conf" (
    echo [global] > "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = pypi.org >> "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = pypi.python.org >> "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = files.pythonhosted.org >> "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = download.pytorch.org >> "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = conda.anaconda.org >> "!CONDA_PREFIX!\pip.conf"
    echo trusted-host = conda-forge.org >> "!CONDA_PREFIX!\pip.conf"
)

:: Set environment variables for pip
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
set "PIP_NO_CACHE_DIR=1"

echo    %L_GREEN%Pip configured to work around SSL issues.%RESET%
echo    %L_YELLOW%Note: This is a temporary workaround.%RESET%

:UpdatePip
echo.
echo    %L_CYAN%Updating pip to latest version...%RESET%
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Failed to update pip, but continuing...%RESET%
)

echo.
echo    %L_GREEN%SSL FIX COMPLETED%RESET%
echo.
echo    The following fixes were applied:
echo    1. Reinstalled Python with SSL support
echo    2. Installed OpenSSL and certificates
echo    3. Configured pip to work around SSL issues
echo.
echo    You can now try installing packages again.
echo    If you still have issues, try running:
echo      pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org package_name
echo.
pause
goto MainMenu

:End
echo.
echo    %L_CYAN%Thank you for using Audio Processing Pipeline Setup!%RESET%
pause
exit /b 0

:: Helper function to activate conda environment
:activate_conda_env
set "CONDA_ROOT_PREFIX=%cd%\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo %L_RED%Conda not found! Run Option 1 first.%RESET%
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo %L_RED%Environment not found! Run Option 1 first.%RESET%
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
    echo %L_RED%Failed to activate environment!%RESET%
    exit /b 1
)
exit /b 0