@echo off
cd /d "g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor"

echo [%date% %time%] START >> debug_log.txt
C:\tools\Anaconda3\python.exe clan_accountant.py >> debug_log.txt 2>&1
echo [%date% %time%] END >> debug_log.txt
