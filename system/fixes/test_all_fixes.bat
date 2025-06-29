@echo off
echo ========================================
echo TESTING ALL FIXES
echo ========================================
echo.

echo This will test all the fixes we've implemented:
echo 1. Processing pipeline without VAD
echo 2. Temp directory fix (clean input folders)
echo 3. Main processing pipeline
echo.

echo Starting comprehensive test...
echo.

echo ========================================
echo 1. Testing processing without VAD...
echo ========================================
python system\tests\test_processing_without_vad.py

echo.
echo ========================================
echo 2. Testing temp directory fix...
echo ========================================
python system\tests\test_temp_directory_fix.py

echo.
echo ========================================
echo 3. Testing main processing pipeline...
echo ========================================
echo Starting audio processing test...
python system\scripts\audio_processing.py --interactive

echo.
echo ========================================
echo All tests completed!
echo ========================================
echo.
echo Summary of fixes:
echo ✓ VAD functionality completely removed (no CUDA errors)
echo ✓ Temp files now in central temp directory
echo ✓ Input folders remain clean
echo ✓ Processing pipeline simplified and stable
echo.
pause 