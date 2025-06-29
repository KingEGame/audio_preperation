@echo off
echo ========================================
echo TESTING SIMPLIFIED AUDIO PROCESSING
echo ========================================
echo.
echo Testing the simplified 2-mode interface...
echo.

cd /d "%~dp0\..\.."
python system\tests\test_simplified_interface.py

echo.
echo Test completed!
pause 