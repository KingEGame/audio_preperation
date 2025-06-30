@echo off
cd /D "%~dp0"
setlocal enabledelayedexpansion

:: Set environment variables
call ..\instructions\activate_environment.bat

echo.
echo ========================================
echo ROLE CLASSIFICATION TEST
echo ========================================
echo.
echo This test checks the new role separation function
echo for audiobooks (narrator + characters).
echo.

:: Check for test file
if not exist "..\tests\test_audio.mp3" (
    echo ERROR: Test file not found!
    echo.
    echo Place test audio file in tests/ folder
    echo with name test_audio.mp3
    echo.
    echo Or specify file path:
    set /p TEST_FILE="Audio file path: "
    if "!TEST_FILE!"=="" (
        echo Test cancelled.
        pause
        exit /b 1
    )
) else (
    set TEST_FILE=..\tests\test_audio.mp3
)

echo ✓ Test file: !TEST_FILE!
echo.

:: Run test
echo Starting role classification test...
echo This may take several minutes...
echo.

python ..\tests\test_role_classification.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ TEST PASSED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Role classification function works correctly.
    echo Results saved in test_roles_output/ folder.
    echo.
    echo Result structure:
    echo   - narrator.wav          (all narrator segments)
    echo   - character_01.wav      (all character 1 segments)
    echo   - character_02.wav      (all character 2 segments)
    echo   - roles_info.txt        (role information)
    echo   - metadata_*.txt        (each role metadata)
) else (
    echo.
    echo ========================================
    echo ❌ TEST FAILED
    echo ========================================
    echo.
    echo Check errors above.
    echo.
    echo Possible causes:
    echo   - Diarization token not installed
    echo   - Dependency problems
    echo   - Insufficient GPU memory
    echo.
    echo To setup diarization run:
    echo   setup_diarization.bat
)

echo.
pause 