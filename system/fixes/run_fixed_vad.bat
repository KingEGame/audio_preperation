@echo off
echo ========================================
echo Audio Processing with Fixed VAD
echo ========================================
echo.

cd /d "%~dp0.."

echo The VAD device mismatch issue has been fixed:
echo - Models are now properly loaded on the correct device
echo - Audio tensors are moved to the same device as models
echo - Automatic fallback from GPU to CPU if needed
echo - Better error handling and logging
echo.

echo Testing VAD fix first...
python tests\test_vad_fix.py

echo.
echo Starting audio processing with fixed VAD...
python scripts\audio_processing.py --interactive

echo.
echo ========================================
echo Processing completed!
echo ========================================
pause 