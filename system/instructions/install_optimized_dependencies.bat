@echo off
echo ========================================
echo Installing Optimized Dependencies
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "..\..\audio_environment" (
    echo ERROR: Virtual environment not found!
    echo Please run install_environment.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "..\..\audio_environment\Scripts\activate.bat"

REM Install psutil for system monitoring
echo.
echo Installing psutil for system monitoring...
pip install psutil>=5.9.0

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ psutil installed successfully
) else (
    echo.
    echo ✗ Failed to install psutil
    pause
    exit /b 1
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import psutil; print(f'✓ psutil {psutil.__version__} installed successfully')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo OPTIMIZED DEPENDENCIES INSTALLED
    echo ========================================
    echo.
    echo The audio processing pipeline has been optimized with:
    echo - Advanced GPU memory management
    echo - Model caching and reuse
    echo - Improved multiprocessing
    echo - Better error handling
    echo - System resource monitoring
    echo.
    echo You can now use the optimized pipeline with better performance!
    echo.
    echo For more information, see: system\guides\OPTIMIZATION_GUIDE.md
) else (
    echo.
    echo ✗ Installation verification failed
    pause
    exit /b 1
)

pause 