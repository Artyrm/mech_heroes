@echo off
REM Disable delayed expansion to handle "!" in folder names correctly
setlocal DisableDelayedExpansion

:: Настройка путей
set "BASE_DIR=%~dp0"
set "LOG_DIR=%BASE_DIR%logs"
set "LOG_FILE=%LOG_DIR%\accountant.log"

:: Создаем папку для логов, если её нет
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ------------------------------------------ >> "%LOG_FILE%"
echo [%date% %time%] STARTING PROCESS >> "%LOG_FILE%"

:: 1. Сбор данных
echo [%date% %time%] Running Python script...
echo [%date% %time%] Running Python script... >> "%LOG_FILE%"

cd /d "%BASE_DIR%clan_monitor"
C:\tools\Anaconda3\python.exe clan_accountant.py >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo [!] Python script FAILED. Check logs/accountant.log
    echo [%date% %time%] ERROR: Python script failed with code %errorlevel% >> "%LOG_FILE%"
    goto DONE
)

:: 2. Git синхронизация
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

:: Wait a bit before closing
timeout /t 5
