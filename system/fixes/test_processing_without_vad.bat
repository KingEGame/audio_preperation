@echo off
echo ========================================
echo TESTING AUDIO PROCESSING WITHOUT VAD
echo ========================================
echo.

echo This will test audio processing with VAD disabled
echo to avoid CUDA device mismatch errors.
echo.

echo Starting audio processing without VAD...
python system\scripts\audio_processing.py --interactive

echo.
echo ========================================
echo Test completed!
echo ========================================
pause 