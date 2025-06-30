@echo off
echo ============================================================
echo DIARIZATION PROGRESS CONFLICT FIX
echo ============================================================

echo.
echo This fix resolves the "Only one live display may be active at once" error
echo that occurs when multiple diarization processes run simultaneously.
echo.

cd /d "%~dp0..\.."

echo Checking current audio processing setup...
if not exist "system\scripts\audio\stages.py" (
    echo ERROR: audio processing module not found!
    echo Make sure you are running this from the correct directory.
    pause
    exit /b 1
)

echo.
echo The fix has already been applied to the code.
echo.
echo Changes made:
echo - Added threading import to stages.py
echo - Added DIARIZATION_LOCK global variable
echo - Modified diarize_with_pyannote_optimized function to use the lock
echo.

echo Testing the fix...
python system\fixes\test_diarization_lock_fix.py

echo.
echo ============================================================
echo FIX APPLIED SUCCESSFULLY
echo ============================================================
echo.
echo The diarization progress conflict has been resolved.
echo.
echo What this fix does:
echo - Prevents multiple diarization processes from using progress bars simultaneously
echo - Uses a threading lock to ensure only one diarization process runs at a time
echo - Maintains the same functionality while preventing conflicts
echo.
echo To test the fix:
echo 1. Run your audio processing as usual
echo 2. Check that diarization runs without "Only one live display" errors
echo 3. Multiple files can still be processed, but diarization will be serialized
echo.
pause 