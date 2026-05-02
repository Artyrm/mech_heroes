@echo off
chcp 65001 >nul
setlocal DisableDelayedExpansion

:: --- SETTINGS ---
set "BASE_DIR=%~dp0"
set "LOG_DIR=%BASE_DIR%logs"
set "LOG_FILE=%LOG_DIR%\accountant.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ------------------------------------------ >> "%LOG_FILE%"
echo [%date% %time%] STARTING PROCESS >> "%LOG_FILE%"

:: --- 1. DATA FETCH ---
echo [%date% %time%] Running Python script (clan_accountant.py)...
echo [%date% %time%] Running Python script... >> "%LOG_FILE%"

cd /d "%BASE_DIR%clan_monitor"

:: Direct redirection to avoid background hangs in Session 0
C:\tools\Anaconda3\python.exe -u clan_accountant.py >> "%LOG_FILE%" 2>&1
set PY_ERROR=%errorlevel%

if NOT "%PY_ERROR%"=="0" (
    echo.
    echo [!] PYTHON SCRIPT FAILED WITH CODE %PY_ERROR%
    echo [%date% %time%] ERROR: Python script failed with code %PY_ERROR% >> "%LOG_FILE%"
    goto DONE
)

:: --- 2. GIT SYNC ---
echo [%date% %time%] Syncing with Git...
echo [%date% %time%] Syncing with Git... >> "%LOG_FILE%"

cd /d "%BASE_DIR%"
set GIT_TERMINAL_PROMPT=0

git add -A >> "%LOG_FILE%" 2>&1
git commit -m "Auto-update %date% %time%" >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo [-] No changes to commit.
    echo [%date% %time%] INFO: No changes to commit. >> "%LOG_FILE%"
    goto DONE
)

echo [%date% %time%] Pushing to repository...
echo [%date% %time%] Pushing to repository... >> "%LOG_FILE%"
git push --progress >> "%LOG_FILE%" 2>&1

if errorlevel 0 (
    echo [*] Success!
    echo [%date% %time%] SUCCESS: Data pushed to Git. >> "%LOG_FILE%"
) else (
    echo [!] Git push FAILED.
    echo [%date% %time%] ERROR: Git push failed. >> "%LOG_FILE%"
)

:DONE
echo [%date% %time%] PROCESS FINISHED >> "%LOG_FILE%"
echo [%date% %time%] All tasks finished.

timeout /t 5
