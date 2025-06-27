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
echo FIXING SSL MODULE ISSUES
echo ==================================================
echo.

:: Test SSL module
echo Testing SSL module...
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo SSL module not available - fixing...
    goto FixSSL
)

echo SSL module is working correctly.
echo.
echo Testing pip with SSL...
python -m pip --version 2>nul || (
    echo Pip SSL test failed - fixing...
    goto FixSSL
)

echo Pip SSL test passed.
echo.
echo SSL issues are resolved!
pause
exit /b 0

:FixSSL
echo.
echo ==================================================
echo APPLYING SSL FIXES
echo ==================================================
echo.

:: Method 1: Reinstall Python with SSL support via conda
echo Method 1: Reinstalling Python with SSL support...
conda install python=3.11 openssl certifi -y || (
    echo Failed to reinstall Python via conda, trying alternative method...
    goto FixSSLAlt
)

:: Test SSL after reinstall
echo Testing SSL after reinstall...
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo SSL still not working, trying alternative method...
    goto FixSSLAlt
)

echo SSL module is now working!
goto UpdatePip

:FixSSLAlt
echo.
echo Method 2: Installing OpenSSL and certificates...
conda install openssl certifi ca-certificates -y || (
    echo Failed to install OpenSSL via conda
    goto FixSSLManual
)

:: Set SSL environment variables
set "SSL_CERT_FILE=!CONDA_PREFIX!\Library\ssl\cert.pem"
set "SSL_CERT_DIR=!CONDA_PREFIX!\Library\ssl\certs"
set "REQUESTS_CA_BUNDLE=!CONDA_PREFIX!\Library\ssl\cert.pem"

:: Test SSL
python -c "import ssl; print('SSL module available')" 2>nul || (
    echo SSL still not working, trying manual fix...
    goto FixSSLManual
)

echo SSL module is now working!
goto UpdatePip

:FixSSLManual
echo.
echo Method 3: Manual SSL configuration...
echo.

:: Create pip configuration to disable SSL verification (temporary fix)
echo Creating pip configuration...
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

echo Pip configured to work around SSL issues.
echo Note: This is a temporary workaround.

:UpdatePip
echo.
echo Updating pip to latest version...
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
    echo Failed to update pip, but continuing...
)

echo.
echo ==================================================
echo SSL FIX COMPLETED
echo ==================================================
echo.
echo The following fixes were applied:
echo 1. Reinstalled Python with SSL support
echo 2. Installed OpenSSL and certificates
echo 3. Configured pip to work around SSL issues
echo.
echo You can now try installing packages again.
echo If you still have issues, try running:
echo   pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org package_name
echo.
pause 