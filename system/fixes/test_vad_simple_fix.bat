@echo off
echo ========================================
echo Simplified VAD Fix Test
echo ========================================
echo.

cd /d "%~dp0.."

echo Testing simplified VAD implementation...
python tests/test_vad_simple_fix.py

echo.
echo ========================================
echo Test completed!
echo ========================================
pause 