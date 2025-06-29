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
echo    %L_BLUE%DIARIZATION SETUP%RESET%
echo.

echo    %L_YELLOW%Installing build tools...%RESET%
conda install -c conda-forge wheel setuptools cmake -y || (
    echo %L_YELLOW%Warning: Failed to install cmake via conda, trying pip...%RESET%
    pip install wheel setuptools cmake --upgrade --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_YELLOW%Warning: Failed to install cmake%RESET%
    )
)

echo    %L_YELLOW%Checking PyAnnote...%RESET%
python -c "import pyannote.audio; print('PyAnnote already installed')" 2>nul && (
    echo    %L_GREEN%PyAnnote is already installed%RESET%
) || (
    echo    %L_YELLOW%PyAnnote not found, installing...%RESET%
    echo    %L_CYAN%Installing sentencepiece...%RESET%
    conda install -c conda-forge sentencepiece -y || (
        echo %L_RED%Failed to install sentencepiece%RESET%
        pause
        exit /b 1
    )
    
    echo    %L_CYAN%Installing speechbrain...%RESET%
    pip install speechbrain --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to install speechbrain%RESET%
        pause
        exit /b 1
    )
    
    echo    %L_CYAN%Installing pyannote.audio...%RESET%
    pip install pyannote.audio --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || (
        echo %L_RED%Failed to install pyannote.audio%RESET%
        pause
        exit /b 1
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
    exit /b 1
)

huggingface-cli login --token !HF_TOKEN! --add-to-git-credential
echo    %L_CYAN%Saving token...%RESET%
echo !HF_TOKEN! > hf_token.txt

echo    %L_CYAN%Testing diarization...%RESET%
python -c "import pyannote.audio; print('PyAnnote installed successfully')" || (
    echo %L_RED%PyAnnote test failed%RESET%
    pause
    exit /b 1
)

echo    %L_GREEN%Diarization setup completed%RESET%
