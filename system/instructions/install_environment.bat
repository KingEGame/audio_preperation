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
pause

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
call system\instructions\activate_environment.bat || (
    echo    %L_RED%Failed to activate environment!%RESET%
    pause
    exit /b 1
)

echo    %L_YELLOW%Installing all dependencies. This step can take a long time%RESET%
echo    %L_YELLOW%depending on your internet connection and hard drive speed. Please be patient.%RESET%
echo.

:: Upgrade pip and setuptools first
echo    %L_CYAN%Upgrading pip and setuptools...%RESET%
"%INSTALL_ENV_DIR%\python.exe" -m pip install --upgrade pip setuptools wheel --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Failed to upgrade pip, continuing...%RESET%
)

:: Install PyTorch with CUDA support FIRST (before other dependencies)
echo    %L_CYAN%Installing PyTorch with CUDA support (FIRST)...%RESET%
echo    %L_YELLOW%This ensures PyTorch is installed before other packages to avoid conflicts.%RESET%
call system\instructions\install_pytorch.bat

:: Install remaining dependencies from main requirements file (excluding PyTorch packages)
echo    %L_CYAN%Installing remaining dependencies...%RESET%
echo    %L_YELLOW%Note: PyTorch was installed first, now installing other dependencies...%RESET%

"%INSTALL_ENV_DIR%\Scripts\pip.exe" install -r system\requirements\requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_RED%Failed to install remaining dependencies!%RESET%
    echo Please check the error messages above and try again.
    pause
    exit /b 1
)

:: Install diarization packages separately (optional, may fail)
echo    %L_CYAN%Installing diarization packages (optional)...%RESET%
echo    %L_YELLOW%Note: These packages may fail if cmake/C++ compiler is not available.%RESET%

:: Try to install PyAnnote and SpeechBrain
"%INSTALL_ENV_DIR%\Scripts\pip.exe" install -r system\requirements\requirements_diarization.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: Some diarization packages failed to install.%RESET%
    echo %L_YELLOW%This is normal if cmake/C++ compiler is not available.%RESET%
    echo %L_YELLOW%Diarization will work with limited functionality.%RESET%
)

:: Try to install sentencepiece from pre-built wheels
echo    %L_CYAN%Installing sentencepiece from pre-built wheels...%RESET%
"%INSTALL_ENV_DIR%\Scripts\pip.exe" install sentencepiece --only-binary=all --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo %L_YELLOW%Warning: sentencepiece installation failed.%RESET%
    echo %L_YELLOW%This is normal - will use alternative tokenization.%RESET%
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
echo echo 🎵 Audio Processing Pipeline v2.0 >> start_processing.bat
echo echo ======================================== >> start_processing.bat
echo echo. >> start_processing.bat
echo echo 🆕 New features: >> start_processing.bat
echo echo    - Modular architecture with /audio package >> start_processing.bat
echo echo    - Speaker organization in folders >> start_processing.bat
echo echo    - Enhanced GPU memory management >> start_processing.bat
echo echo    - No duration limit option >> start_processing.bat
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
echo :: Start interactive processing >> start_processing.bat
echo echo 🚀 Starting interactive audio processing... >> start_processing.bat
echo echo. >> start_processing.bat
echo echo 💡 The script will guide you through the process interactively. >> start_processing.bat
echo echo. >> start_processing.bat
echo. >> start_processing.bat
echo python system\scripts\audio_processing.py >> start_processing.bat
echo. >> start_processing.bat
echo echo. >> start_processing.bat
echo echo ✅ Processing completed! >> start_processing.bat
echo echo 📁 Results organized by speakers in the specified folder >> start_processing.bat
echo echo. >> start_processing.bat
echo pause >> start_processing.bat

:: Create activate_environment.bat
echo @echo off > activate_environment.bat
echo chcp 65001 ^>nul >> activate_environment.bat
echo setlocal enabledelayedexpansion >> activate_environment.bat
echo. >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo ======================================== >> activate_environment.bat
echo echo 🐍 Activate Environment - Audio Processing Pipeline v2.0 >> activate_environment.bat
echo echo ======================================== >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo 🆕 New modular architecture with /audio package >> activate_environment.bat
echo echo. >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Generate the ESC character >> activate_environment.bat
echo for /F %%%%a in ^('echo prompt $E ^| cmd'^) do set "ESC=%%%%a" >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Colors >> activate_environment.bat
echo set "L_RED=%%ESC%%[91m" >> activate_environment.bat
echo set "L_GREEN=%%ESC%%[92m" >> activate_environment.bat
echo set "L_YELLOW=%%ESC%%[93m" >> activate_environment.bat
echo set "L_CYAN=%%ESC%%[96m" >> activate_environment.bat
echo set "L_BLUE=%%ESC%%[94m" >> activate_environment.bat
echo set "RESET=%%ESC%%[0m" >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Portable Conda Environment Activation >> activate_environment.bat
echo. >> activate_environment.bat
echo set INSTALL_DIR=%%cd%%\..\audio_environment >> activate_environment.bat
echo set CONDA_ROOT_PREFIX=%%cd%%\audio_environment\conda >> activate_environment.bat
echo set INSTALL_ENV_DIR=%%cd%%\audio_environment\env >> activate_environment.bat
echo :: Check if portable conda exists >> activate_environment.bat
echo if not exist "^!CONDA_ROOT_PREFIX^!\_conda.exe" ^( >> activate_environment.bat
echo     echo %%L_RED%%Portable Conda not found^! Run system\instructions\install_portable_conda.bat first.%%RESET%% >> activate_environment.bat
echo     exit /b 1 >> activate_environment.bat
echo ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Check if environment exists >> activate_environment.bat
echo if not exist "^!INSTALL_ENV_DIR^!\python.exe" ^( >> activate_environment.bat
echo     echo %%L_RED%%Environment not found^! Run system\instructions\install_portable_conda.bat first.%%RESET%% >> activate_environment.bat
echo     exit /b 1 >> activate_environment.bat
echo ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Set environment variables >> activate_environment.bat
echo. >> activate_environment.bat
echo set CONDA_DEFAULT_ENV=audio_env >> activate_environment.bat
echo set CONDA_PROMPT_MODIFIER=^(audio_env^) >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Activate the environment using portable conda >> activate_environment.bat
echo @rem check if conda environment was actually created >> activate_environment.bat
echo if not exist "%%INSTALL_ENV_DIR%%\python.exe" ^( echo. ^&^& echo Conda environment is empty. ^&^& goto end ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo @rem activate installer env >> activate_environment.bat
echo call "%%CONDA_ROOT_PREFIX%%\condabin\conda.bat" activate "%%INSTALL_ENV_DIR%%" ^|^| ^( echo. ^&^& echo Miniconda hook not found. ^&^& goto end ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo :: Verify we're using the right Python >> activate_environment.bat
echo python -c "import sys; print^('Python path:', sys.executable^)" ^| findstr "audio_environment" ^>nul >> activate_environment.bat
echo if "%%ERRORLEVEL%%" NEQ "0" ^( >> activate_environment.bat
echo     echo %%L_RED%%ERROR: Still using wrong Python^!%%RESET%% >> activate_environment.bat
echo     echo Expected: ^!INSTALL_ENV_DIR^!\python.exe >> activate_environment.bat
echo     echo Actual:  >> activate_environment.bat
echo     python -c "import sys; print^(sys.executable^)" >> activate_environment.bat
echo     exit /b 1 >> activate_environment.bat
echo ^) >> activate_environment.bat
echo. >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo ✅ Environment activated >> activate_environment.bat
echo echo 🐍 Now you can use Python commands >> activate_environment.bat
echo echo. >> activate_environment.bat
echo echo. >> activate_environment.bat
echo cmd /K >> activate_environment.bat

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