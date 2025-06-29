@echo off
echo ========================================
echo Fixing VAD CUDA Error
echo ========================================
echo.

cd /d "%~dp0.."

echo The issue is that VAD (Voice Activity Detection) is failing on GPU
echo with CUDA errors. This fix will:
echo 1. Force VAD to use CPU instead of GPU
echo 2. Add automatic fallback from GPU to CPU
echo 3. Continue processing even if VAD fails
echo.

echo Starting audio processing with CPU VAD...
python scripts\audio_processing.py --interactive

echo.
echo ========================================
echo Processing completed!
echo ========================================
pause 