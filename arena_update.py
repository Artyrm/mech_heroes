import subprocess
import sys
import os
from datetime import datetime

def run_step(name, command):
    start_time = datetime.now()
    print(f"\n[{start_time.strftime('%H:%M:%S')}] >>> [STEP] {name}")
    print(f"Executing: {command}")
    try:
        # Using sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable] + command.split(), capture_output=False, text=True)
        end_time = datetime.now()
        duration = end_time - start_time
        # Round duration to tenths of a second
        seconds = duration.total_seconds()
        
        if result.returncode == 0:
            print(f"[{end_time.strftime('%H:%M:%S')}] --- [SUCCESS] {name} completed in {seconds:.1f}s")
            return True
        else:
            print(f"[{end_time.strftime('%H:%M:%S')}] --- [ERROR] {name} failed with exit code {result.returncode} after {seconds:.1f}s.")
            return False
    except Exception as e:
        print(f"--- [EXCEPTION] {name}: {e}")
        return False

def is_user_active() -> bool:
    target_ip = "84.201.164.35"
    try:
        cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
        import subprocess as sp
        proc = sp.run(cmd, shell=True, capture_output=True, text=True)
        if "ESTABLISHED" in proc.stdout:
            return True
    except Exception:
        pass
    return False

def main():
    print("="*50)
    print("      ARENA ANALYTICS GLOBAL UPDATE & DEPLOY")
    print("="*50)

    force_run = "--force" in sys.argv
    update_history = "--update_history" in sys.argv
    local_mode = "--local" in sys.argv
    is_active = is_user_active()
    
    if is_active and not force_run:
        print("[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ с сервером игры.")
        print("[*] Скрипты будут использовать локальные дампы, пропуская запросы к API.")

    steps = [
        ("FETCHING LATEST DATA", "arena/fetch_arena.py"),
        ("SYNCING FROM INIT DUMPS", "arena/sync_from_init.py"),
        ("DISTRIBUTING BATTLES", "battle_analytics/fetch_and_store_battles.py"),
        ("GENERATING PERSONAL STATS", "battle_analytics/generate_personal_stats.py"),
        ("FETCHING SQUADS", "arena/fetch_squads.py"),
        ("GENERATING SQUAD REPORTS", "arena/generate_squad_reports.py"),
        ("GENERATING HTML DASHBOARD", "arena/generate_dashboard.py"),
        ("DEPLOYING TO SERVER", "deploy.py")
    ]

    for name, cmd in steps:
        if name == "DEPLOYING TO SERVER" and local_mode:
            print(f"\n>>> [STEP] {name} SKIPPED (local mode)")
            continue

        actual_cmd = cmd
        if force_run and "--force" not in actual_cmd:
            actual_cmd += " --force"
        if update_history and "--update_history" not in actual_cmd:
            actual_cmd += " --update_history"
            
        if not run_step(name, actual_cmd):
            print(f"\n!!! Global update aborted due to errors in step: {name}")
            sys.exit(1)

    print("\n" + "="*50)
    print("   ALL STEPS COMPLETED SUCCESSFULLY!")
    print("   Arena Report: http://ovalhalla.ru/my/mech/dashboard.html")
    print("="*50)

if __name__ == "__main__":
    main()
