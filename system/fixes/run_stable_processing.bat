@echo off
echo ========================================
echo Stable Audio Processing Pipeline
echo ========================================
echo.

cd /d "%~dp0.."

echo This version uses conservative settings for maximum stability:
echo - Sequential processing (no parallel conflicts)
echo - Word boundary splitting (more stable than smart multithreaded)
echo - CPU VAD (no GPU VAD conflicts)
echo - Shorter chunks (5 minutes)
echo - Better error handling
echo.

echo Starting stable audio processing...
python scripts\audio_processing_stable.py --interactive

echo.
echo ========================================
echo Processing completed!
echo ========================================
pause 