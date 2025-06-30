@echo off
echo ============================================================
echo DIARIZATION LOCK FIX TEST
echo ============================================================

echo.
echo Testing diarization lock fix...
echo.

cd /d "%~dp0..\.."

echo Running test script...
python system\fixes\test_diarization_lock_fix.py

echo.
echo ============================================================
echo TEST COMPLETED
echo ============================================================
echo.
echo If the test passed, the diarization lock fix should work.
echo.
echo To test with real audio processing:
echo 1. Run: python system\scripts\audio_processing.py --input your_audio.mp3 --output results
echo 2. Check that diarization runs without "Only one live display" errors
echo.
pause 