@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
set "CONDA_ROOT_PREFIX=%cd%\audio_environment\conda"
set "INSTALL_ENV_DIR=%cd%\audio_environment\env"

if not exist "!CONDA_ROOT_PREFIX!\condabin\conda.bat" (
    echo ERROR: Conda not found! Run setup.bat first.
    pause
    exit /b 1
)

if not exist "!INSTALL_ENV_DIR!\python.exe" (
    echo ERROR: Environment not found! Run setup.bat first.
    pause
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
    echo ERROR: Failed to activate environment!
    pause
    exit /b 1
)

echo ==================================================
echo TESTING SSL FIX
echo ==================================================
echo.

:: Test 1: SSL module
echo Test 1: SSL module availability...
python -c "import ssl; print('✓ SSL module available')" 2>nul || (
    echo ✗ SSL module not available
    goto TestFailed
)

:: Test 2: Pip with SSL
echo.
echo Test 2: Pip with SSL...
python -m pip --version 2>nul || (
    echo ✗ Pip SSL test failed
    goto TestFailed
)

:: Test 3: Install a simple package
echo.
echo Test 3: Installing a simple package...
pip install requests --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org 2>nul || (
    echo ✗ Package installation failed
    goto TestFailed
)

echo ✓ Package installation successful

:: Test 4: Import the package
echo.
echo Test 4: Importing installed package...
python -c "import requests; print('✓ Package import successful')" 2>nul || (
    echo ✗ Package import failed
    goto TestFailed
)

echo.
echo ==================================================
echo ✓ ALL SSL TESTS PASSED!
echo ==================================================
echo.
echo The SSL fix is working correctly.
echo You can now proceed with installing packages.
echo.
pause
exit /b 0

:TestFailed
echo.
echo ==================================================
echo ✗ SSL TESTS FAILED
echo ==================================================
echo.
echo Please run the SSL fix again:
echo 1. Run setup.bat
echo 2. Choose option 6 (Fix SSL Issues)
echo.
pause
exit /b 1 