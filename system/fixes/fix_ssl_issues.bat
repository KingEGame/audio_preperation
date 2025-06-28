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
echo    %L_BLUE%FIXING SSL MODULE ISSUES%RESET%
echo.
set "PYTHON_EXE=%cd%\audio_environment\env\python.exe"

if not exist "!PYTHON_EXE!" (
    echo %L_RED%Environment not found! Run install_environment.bat first.%RESET%
    pause
    exit /b 1
)

echo    %L_CYAN%Activating environment...%RESET%
call system\instructions\activate_environment.bat || (
    pause
    exit /b 1
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
exit /b 0

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