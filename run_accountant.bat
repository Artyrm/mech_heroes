@echo off
chcp 65001 >nul
cd /d "%~dp0clan_monitor"
C:\tools\Anaconda3\python.exe clan_accountant.py
exit 0
