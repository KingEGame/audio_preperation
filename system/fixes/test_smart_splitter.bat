@echo off
echo ========================================
echo Smart Multithreaded Splitter Test
echo ========================================
echo.

cd /d "%~dp0.."

echo Testing new smart multithreaded splitter...
python tests/test_smart_splitter.py

echo.
echo ========================================
echo Test completed!
echo ========================================
pause 