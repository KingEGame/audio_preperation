@echo off 
set CONDA_ROOT_PREFIX=E:\Project\audio_preperation\audio_environment\conda 
set INSTALL_ENV_DIR=E:\Project\audio_preperation\audio_environment\env 
call "E:\Project\audio_preperation\audio_environment\conda\condabin\conda.bat" activate "E:\Project\audio_preperation\audio_environment\env" 
 
python system\scripts\concatenate_mp3.py 
 
echo [OK] Processing completed 
pause 
