@echo off
chcp 65001 >nul
echo ========================================
echo КОНКАТЕНАЦИЯ MP3 ФАЙЛОВ
echo ========================================
echo.

python concatenate_mp3.py --interactive

echo.
echo Нажмите любую клавишу для выхода...
pause >nul 