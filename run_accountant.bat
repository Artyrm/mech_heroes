@echo off

echo [*] Starting data collection...
cd /d "%~dp0clan_monitor"
C:\tools\Anaconda3\python.exe clan_accountant.py

if %errorlevel% equ 0 (
    echo.
    echo [*] Data collection successful. Syncing with Git...
    cd /d "%~dp0"
    
    set GIT_TERMINAL_PROMPT=0
    
    git add -A
    
    git commit -m "Auto-update %date% %time%"
    if %errorlevel% neq 0 (
        echo [-] No changes or commit failed.
    ) else (
        echo [*] Pushing to repository (please wait)...
        git push --progress
    )
) else (
    echo.
    echo [!] Python script FAILED. Skipping Git sync.
)

echo.
echo [*] All tasks finished.
pause
