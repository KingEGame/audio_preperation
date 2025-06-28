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
echo :: Check if parameters are passed >> start_processing.bat
echo if "%%~1"=="" ^( >> start_processing.bat
echo     echo 📋 Usage: >> start_processing.bat
echo     echo start_processing.bat --input "audio.mp3" --output "results" >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo 📝 Examples: >> start_processing.bat
echo     echo start_processing.bat --input "lecture.mp3" --output "lecture_results" >> start_processing.bat
echo     echo start_processing.bat --input "meeting.mp3" --output "results" --steps split denoise vad diar >> start_processing.bat
echo     echo start_processing.bat --input "audio.mp3" --output "results" --no_duration_limit >> start_processing.bat
echo     echo start_processing.bat --input "audio.mp3" --output "results" --min_speaker_segment 0.1 >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo 🆕 New options: >> start_processing.bat
echo     echo    --no_duration_limit - Process all segments without duration limit >> start_processing.bat
echo     echo    --min_speaker_segment 0.1 - Set minimum segment duration >> start_processing.bat
echo     echo    --parallel - Enable parallel processing >> start_processing.bat
echo     echo. >> start_processing.bat
echo     echo 💡 For detailed help: start_processing.bat --help >> start_processing.bat
echo     echo. >> start_processing.bat
echo     pause >> start_processing.bat
echo     exit /b 0 >> start_processing.bat
echo ^) >> start_processing.bat
echo. >> start_processing.bat
echo :: Start processing >> start_processing.bat
echo echo 🚀 Starting audio processing with new architecture... >> start_processing.bat
echo echo. >> start_processing.bat
echo. >> start_processing.bat
echo python system\scripts\audio_processing.py %%* >> start_processing.bat
echo. >> start_processing.bat
echo echo. >> start_processing.bat
echo echo ✅ Processing completed! >> start_processing.bat
echo echo 📁 Results organized by speakers in the specified folder >> start_processing.bat
echo echo. >> start_processing.bat
echo pause >> start_processing.bat

:: Create start_safe_processing.bat
echo @echo off > start_safe_processing.bat
echo chcp 65001 ^>nul >> start_safe_processing.bat
echo setlocal enabledelayedexpansion >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo echo ======================================== >> start_safe_processing.bat
echo echo 🛡️ Safe Audio Processing Pipeline v2.0 >> start_safe_processing.bat
echo echo ======================================== >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo echo This version includes enhanced error handling and memory management. >> start_safe_processing.bat
echo echo 🆕 New features: >> start_safe_processing.bat
echo echo    - Advanced GPU memory management >> start_safe_processing.bat
echo echo    - Model caching and reuse >> start_safe_processing.bat
echo echo    - Better error recovery >> start_safe_processing.bat
echo echo    - Speaker organization in folders >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo :: Check if environment exists >> start_safe_processing.bat
echo if not exist "audio_environment" ^( >> start_safe_processing.bat
echo     echo ❌ Environment not found! >> start_safe_processing.bat
echo     echo. >> start_safe_processing.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> start_safe_processing.bat
echo     echo. >> start_safe_processing.bat
echo     pause >> start_safe_processing.bat
echo     exit /b 1 >> start_safe_processing.bat
echo ^) >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo :: Check if parameters are passed >> start_safe_processing.bat
echo if "%%~1"=="" ^( >> start_safe_processing.bat
echo     echo 📋 Usage: >> start_safe_processing.bat
echo     echo start_safe_processing.bat "input_file.mp3" "output_folder" >> start_safe_processing.bat
echo     echo. >> start_safe_processing.bat
echo     echo 📝 Examples: >> start_safe_processing.bat
echo     echo start_safe_processing.bat "lecture.mp3" "lecture_results" >> start_safe_processing.bat
echo     echo start_safe_processing.bat "audio_folder" "results" >> start_safe_processing.bat
echo     echo. >> start_safe_processing.bat
echo     echo 💡 This version includes: >> start_safe_processing.bat
echo     echo    - Enhanced file validation >> start_safe_processing.bat
echo     echo    - Better error handling >> start_safe_processing.bat
echo     echo    - Reduced memory usage >> start_safe_processing.bat
echo     echo    - Timeout protection >> start_safe_processing.bat
echo     echo    - GPU memory monitoring >> start_safe_processing.bat
echo     echo    - Model caching system >> start_safe_processing.bat
echo     echo. >> start_safe_processing.bat
echo     pause >> start_safe_processing.bat
echo     exit /b 0 >> start_safe_processing.bat
echo ^) >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo :: Start safe processing >> start_safe_processing.bat
echo echo 🚀 Starting safe audio processing... >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo call system\fixes\run_safe_processing.bat "%%~1" "%%~2" >> start_safe_processing.bat
echo. >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo echo ✅ Safe processing completed! >> start_safe_processing.bat
echo echo 📁 Results organized by speakers in the specified folder >> start_safe_processing.bat
echo echo. >> start_safe_processing.bat
echo pause >> start_safe_processing.bat

:: Create diagnose_ffmpeg.bat
echo @echo off > diagnose_ffmpeg.bat
echo chcp 65001 ^>nul >> diagnose_ffmpeg.bat
echo setlocal enabledelayedexpansion >> diagnose_ffmpeg.bat
echo. >> diagnose_ffmpeg.bat
echo echo. >> diagnose_ffmpeg.bat
echo echo ======================================== >> diagnose_ffmpeg.bat
echo echo 🔍 FFmpeg Diagnostics - Audio Processing Pipeline v2.0 >> diagnose_ffmpeg.bat
echo echo ======================================== >> diagnose_ffmpeg.bat
echo echo. >> diagnose_ffmpeg.bat
echo echo This will diagnose FFmpeg issues and suggest fixes. >> diagnose_ffmpeg.bat
echo echo 🆕 Now includes GPU memory diagnostics. >> diagnose_ffmpeg.bat
echo echo. >> diagnose_ffmpeg.bat
echo. >> diagnose_ffmpeg.bat
echo :: Check if environment exists >> diagnose_ffmpeg.bat
echo if not exist "audio_environment" ^( >> diagnose_ffmpeg.bat
echo     echo ❌ Environment not found! >> diagnose_ffmpeg.bat
echo     echo. >> diagnose_ffmpeg.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> diagnose_ffmpeg.bat
echo     echo. >> diagnose_ffmpeg.bat
echo     pause >> diagnose_ffmpeg.bat
echo     exit /b 1 >> diagnose_ffmpeg.bat
echo ^) >> diagnose_ffmpeg.bat
echo. >> diagnose_ffmpeg.bat
echo :: Check if audio file is provided >> diagnose_ffmpeg.bat
echo if "%%~1"=="" ^( >> diagnose_ffmpeg.bat
echo     echo 📋 Running general FFmpeg and GPU diagnostics... >> diagnose_ffmpeg.bat
echo     echo. >> diagnose_ffmpeg.bat
echo     call system\fixes\fix_ffmpeg_issues.bat >> diagnose_ffmpeg.bat
echo ^) else ^( >> diagnose_ffmpeg.bat
echo     echo 📋 Testing specific audio file: %%1 >> diagnose_ffmpeg.bat
echo     echo. >> diagnose_ffmpeg.bat
echo     call system\fixes\fix_ffmpeg_issues.bat "%%~1" >> diagnose_ffmpeg.bat
echo ^) >> diagnose_ffmpeg.bat
echo. >> diagnose_ffmpeg.bat
echo echo. >> diagnose_ffmpeg.bat
echo echo ✅ Diagnostics completed! >> diagnose_ffmpeg.bat
echo echo 📋 Check the output above for issues and solutions. >> diagnose_ffmpeg.bat
echo echo. >> diagnose_ffmpeg.bat
echo pause >> diagnose_ffmpeg.bat

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
echo :: Check if environment exists >> cleanup_temp.bat
echo if not exist "audio_environment" ^( >> cleanup_temp.bat
echo     echo ❌ Environment not found! >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     pause >> cleanup_temp.bat
echo     exit /b 1 >> cleanup_temp.bat
echo ^) >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo :: Check if dry run is requested >> cleanup_temp.bat
echo if "%%~1"=="--dry-run" ^( >> cleanup_temp.bat
echo     echo 📋 Running in DRY RUN mode - no files will be deleted >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     call system\fixes\cleanup_temp_folders.bat --dry-run >> cleanup_temp.bat
echo ^) else if "%%~1"=="--help" ^( >> cleanup_temp.bat
echo     echo 📋 Usage options: >> cleanup_temp.bat
echo     echo   cleanup_temp.bat          - Clean up old folders (24h+) >> cleanup_temp.bat
echo     echo   cleanup_temp.bat --dry-run - Show what would be deleted >> cleanup_temp.bat
echo     echo   cleanup_temp.bat --help    - Show this help >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     echo 📝 Examples: >> cleanup_temp.bat
echo     echo   cleanup_temp.bat >> cleanup_temp.bat
echo     echo   cleanup_temp.bat --dry-run >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     pause >> cleanup_temp.bat
echo     exit /b 0 >> cleanup_temp.bat
echo ^) else ^( >> cleanup_temp.bat
echo     echo 📋 This will delete temporary folders older than 24 hours. >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     set /p CONFIRM="Continue with cleanup? (y/n): " >> cleanup_temp.bat
echo     if /i not "!CONFIRM!"=="y" ^( >> cleanup_temp.bat
echo         echo Cleanup cancelled. >> cleanup_temp.bat
echo         echo. >> cleanup_temp.bat
echo         echo To see what would be deleted without actually deleting: >> cleanup_temp.bat
echo         echo   cleanup_temp.bat --dry-run >> cleanup_temp.bat
echo         pause >> cleanup_temp.bat
echo         exit /b 0 >> cleanup_temp.bat
echo     ^) >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     echo Starting cleanup... >> cleanup_temp.bat
echo     echo. >> cleanup_temp.bat
echo     call system\fixes\cleanup_temp_folders.bat >> cleanup_temp.bat
echo ^) >> cleanup_temp.bat
echo. >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo echo ✅ Cleanup completed! >> cleanup_temp.bat
echo echo. >> cleanup_temp.bat
echo pause >> cleanup_temp.bat

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
echo echo   python system\scripts\audio_processing.py --help >> activate_environment.bat
echo echo   python system\scripts\test_gpu.py >> activate_environment.bat
echo echo   python system\scripts\test_new_architecture.py >> activate_environment.bat
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
echo echo 🔗 Audio Concatenation - Audio Processing Pipeline v2.0 >> audio_concat.bat
echo echo ======================================== >> audio_concat.bat
echo echo. >> audio_concat.bat
echo echo 🆕 Now supports speaker-organized folders >> audio_concat.bat
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
echo     echo audio_concat.bat "speaker_0001" "speaker1_combined.mp3" >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     echo 💡 Combines all MP3 files from the folder into one file >> audio_concat.bat
echo     echo 🆕 Now works with speaker-organized folders >> audio_concat.bat
echo     echo. >> audio_concat.bat
echo     pause >> audio_concat.bat
echo     exit /b 0 >> audio_concat.bat
echo ^) >> audio_concat.bat
echo. >> audio_concat.bat
echo :: Start concatenation >> audio_concat.bat
echo echo 🚀 Starting audio concatenation... >> audio_concat.bat
echo echo. >> audio_concat.bat
echo. >> audio_concat.bat
echo python system\scripts\concatenate_mp3.py "%%~1" "%%~2" >> audio_concat.bat
echo. >> audio_concat.bat
echo echo. >> audio_concat.bat
echo echo ✅ Concatenation completed! >> audio_concat.bat
echo echo 📁 Result saved in: %%2 >> audio_concat.bat
echo echo. >> audio_concat.bat
echo pause >> audio_concat.bat

:: Create start_ultra_optimized_processing.bat
echo @echo off > start_ultra_optimized_processing.bat
echo chcp 65001 ^>nul >> start_ultra_optimized_processing.bat
echo setlocal enabledelayedexpansion >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo echo ======================================== >> start_ultra_optimized_processing.bat
echo echo 🚀 Ultra-Optimized Audio Processing Pipeline v2.0 >> start_ultra_optimized_processing.bat
echo echo ======================================== >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo echo This version is specifically optimized for parallel diarization performance. >> start_ultra_optimized_processing.bat
echo echo 🆕 New features: >> start_ultra_optimized_processing.bat
echo echo    - Shared model instances across processes >> start_ultra_optimized_processing.bat
echo echo    - Optimized chunk sizes for diarization >> start_ultra_optimized_processing.bat
echo echo    - Better GPU memory management >> start_ultra_optimized_processing.bat
echo echo    - Faster model loading >> start_ultra_optimized_processing.bat
echo echo    - Improved parallel performance >> start_ultra_optimized_processing.bat
echo echo    - Speaker organization in folders >> start_ultra_optimized_processing.bat
echo echo    - No duration limit option >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo :: Check if environment exists >> start_ultra_optimized_processing.bat
echo if not exist "audio_environment" ^( >> start_ultra_optimized_processing.bat
echo     echo ❌ Environment not found! >> start_ultra_optimized_processing.bat
echo     echo. >> start_ultra_optimized_processing.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> start_ultra_optimized_processing.bat
echo     echo. >> start_ultra_optimized_processing.bat
echo     pause >> start_ultra_optimized_processing.bat
echo     exit /b 1 >> start_ultra_optimized_processing.bat
echo ^) >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo :: Check if parameters are passed >> start_ultra_optimized_processing.bat
echo if "%%~1"=="" ^( >> start_ultra_optimized_processing.bat
echo     echo 📋 Usage: >> start_ultra_optimized_processing.bat
echo     echo start_ultra_optimized_processing.bat "input_file.mp3" "output_folder" >> start_ultra_optimized_processing.bat
echo     echo. >> start_ultra_optimized_processing.bat
echo     echo 📝 Examples: >> start_ultra_optimized_processing.bat
echo     echo start_ultra_optimized_processing.bat "lecture.mp3" "lecture_results" >> start_ultra_optimized_processing.bat
echo     echo start_ultra_optimized_processing.bat "audio_folder" "results" >> start_ultra_optimized_processing.bat
echo     echo. >> start_ultra_optimized_processing.bat
echo     echo 💡 This version includes: >> start_ultra_optimized_processing.bat
echo     echo    - Shared model instances across processes >> start_ultra_optimized_processing.bat
echo     echo    - Optimized chunk sizes for diarization >> start_ultra_optimized_processing.bat
echo     echo    - Better GPU memory management >> start_ultra_optimized_processing.bat
echo     echo    - Faster model loading >> start_ultra_optimized_processing.bat
echo     echo    - Improved parallel performance >> start_ultra_optimized_processing.bat
echo     echo    - Speaker organization in folders >> start_ultra_optimized_processing.bat
echo     echo    - No duration limit option >> start_ultra_optimized_processing.bat
echo     echo. >> start_ultra_optimized_processing.bat
echo     pause >> start_ultra_optimized_processing.bat
echo     exit /b 0 >> start_ultra_optimized_processing.bat
echo ^) >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo :: Start ultra-optimized processing >> start_ultra_optimized_processing.bat
echo echo 🚀 Starting ultra-optimized audio processing... >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo call system\fixes\run_ultra_optimized_processing.bat "%%~1" "%%~2" >> start_ultra_optimized_processing.bat
echo. >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo echo ✅ Ultra-optimized processing completed! >> start_ultra_optimized_processing.bat
echo echo 📁 Results organized by speakers in the specified folder >> start_ultra_optimized_processing.bat
echo echo. >> start_ultra_optimized_processing.bat
echo pause >> start_ultra_optimized_processing.bat

:: Create test_new_architecture.bat
echo @echo off > test_new_architecture.bat
echo chcp 65001 ^>nul >> test_new_architecture.bat
echo setlocal enabledelayedexpansion >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo echo ======================================== >> test_new_architecture.bat
echo echo 🧪 Test New Architecture - Audio Processing Pipeline v2.0 >> test_new_architecture.bat
echo echo ======================================== >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo echo This will test the new modular architecture and features. >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo :: Check if environment exists >> test_new_architecture.bat
echo if not exist "audio_environment" ^( >> test_new_architecture.bat
echo     echo ❌ Environment not found! >> test_new_architecture.bat
echo     echo. >> test_new_architecture.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> test_new_architecture.bat
echo     echo. >> test_new_architecture.bat
echo     pause >> test_new_architecture.bat
echo     exit /b 1 >> test_new_architecture.bat
echo ^) >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo :: Activate environment >> test_new_architecture.bat
echo call system\instructions\activate_environment.bat >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo :: Start testing >> test_new_architecture.bat
echo echo 🧪 Testing new architecture... >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo python system\scripts\test_new_architecture.py >> test_new_architecture.bat
echo. >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo echo ✅ Architecture test completed! >> test_new_architecture.bat
echo echo. >> test_new_architecture.bat
echo pause >> test_new_architecture.bat

:: Create test_no_duration_limit.bat
echo @echo off > test_no_duration_limit.bat
echo chcp 65001 ^>nul >> test_no_duration_limit.bat
echo setlocal enabledelayedexpansion >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo echo ======================================== >> test_no_duration_limit.bat
echo echo ⏱️ Test No Duration Limit - Audio Processing Pipeline v2.0 >> test_no_duration_limit.bat
echo echo ======================================== >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo echo This will test the new no duration limit feature. >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo :: Check if environment exists >> test_no_duration_limit.bat
echo if not exist "audio_environment" ^( >> test_no_duration_limit.bat
echo     echo ❌ Environment not found! >> test_no_duration_limit.bat
echo     echo. >> test_no_duration_limit.bat
echo     echo Run setup.bat and select option 1 to install the environment. >> test_no_duration_limit.bat
echo     echo. >> test_no_duration_limit.bat
echo     pause >> test_no_duration_limit.bat
echo     exit /b 1 >> test_no_duration_limit.bat
echo ^) >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo :: Activate environment >> test_no_duration_limit.bat
echo call system\instructions\activate_environment.bat >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo :: Start testing >> test_no_duration_limit.bat
echo echo ⏱️ Testing no duration limit feature... >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo python system\scripts\test_no_duration_limit.py >> test_no_duration_limit.bat
echo. >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo echo ✅ No duration limit test completed! >> test_no_duration_limit.bat
echo echo. >> test_no_duration_limit.bat
echo pause >> test_no_duration_limit.bat

echo    %L_GREEN%✅ Convenient bat files created in root directory!%RESET%
echo.
echo    %L_CYAN%Available commands:%RESET%
echo    - start_processing.bat - Start audio processing (new architecture)
echo    - start_safe_processing.bat - Start safe processing (with error handling)
echo    - start_ultra_optimized_processing.bat - Start ultra-optimized processing (best for parallel diarization)
echo    - diagnose_ffmpeg.bat - Diagnose FFmpeg issues
echo    - cleanup_temp.bat - Clean up temporary folders
echo    - activate_environment.bat - Activate environment
echo    - audio_concat.bat - Concatenate audio files
echo    - test_new_architecture.bat - Test new modular architecture
echo    - test_no_duration_limit.bat - Test no duration limit feature
echo.
echo    %L_CYAN%🆕 New features in v2.0:%RESET%
echo    - Modular architecture with /audio package
echo    - Speaker organization in folders
echo    - Enhanced GPU memory management
echo    - No duration limit option
echo    - Model caching and reuse
echo    - Better error handling and recovery
echo.

echo    %L_GREEN%Installation completed!%RESET%
echo    %L_GREEN%✅ Environment installed with diarization support!%RESET%
pause 