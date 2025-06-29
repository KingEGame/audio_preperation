@echo off
echo ========================================
echo Audio Processing WITHOUT VAD
echo ========================================
echo.

cd /d "%~dp0.."

echo This version skips VAD (Voice Activity Detection) to avoid CUDA errors.
echo Processing stages: split, denoise, diarization
echo NO silence removal will be performed.
echo.

echo Starting audio processing without VAD...
python scripts\audio_processing.py --interactive

echo.
echo ========================================
echo Processing completed!
echo ========================================
pause 