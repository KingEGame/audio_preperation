@echo off
echo ========================================
echo TESTING TEMP DIRECTORY FIX
echo ========================================
echo.

echo This will test that temp files are now created
echo in the central temp directory instead of the input directory.
echo.

echo Testing temp directory fix...
python system\tests\test_temp_directory_fix.py

echo.
echo ========================================
echo Test completed!
echo ========================================
pause 