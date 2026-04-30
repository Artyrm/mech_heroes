@echo off
REM Use simple linear logic to avoid "!" issues in paths

echo [*] Starting data collection...
cd /d "%~dp0clan_monitor"
C:\tools\Anaconda3\python.exe clan_accountant.py

if errorlevel 1 goto FAILED

echo.
echo [*] Data collection successful. Syncing with Git...
cd /d "%~dp0"
set GIT_TERMINAL_PROMPT=0

git add -A
git commit -m "Auto-update %date% %time%"
if errorlevel 1 echo [-] No changes to commit. & goto DONE

echo [*] Pushing to repository (please wait)...
git push --progress
if errorlevel 0 echo [*] Git push SUCCESSFUL.
if errorlevel 1 echo [!] Git push FAILED.

goto DONE

:FAILED
echo.
echo [!] Python script FAILED. Skipping Git sync.

:DONE
echo.
echo [*] All tasks finished.
pause
