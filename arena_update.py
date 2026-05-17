import subprocess
import sys
import os

def run_step(name, command):
    print(f"\n>>> [STEP] {name}")
    print(f"Executing: {command}")
    try:
        # Using sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable] + command.split(), capture_output=False, text=True)
        if result.returncode == 0:
            print(f"--- [SUCCESS] {name} completed.")
            return True
        else:
            print(f"--- [ERROR] {name} failed with exit code {result.returncode}.")
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
    if is_user_active() and not force_run:
        print("[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ с сервером игры. Пропуск обновления.")
        print("[*] Используйте флаг --force для принудительного обновления.")
        sys.exit(0)

    steps = [
        ("FETCHING LATEST DATA", "arena/fetch_arena.py"),
        ("SYNCING FROM INIT DUMPS", "arena/sync_from_init.py"),
        ("DISTRIBUTING BATTLES", "battle_analytics/fetch_and_store_battles.py"),
        ("FETCHING SQUADS", "arena/fetch_squads.py"),
        ("GENERATING SQUAD REPORTS", "arena/generate_squad_reports.py"),
        ("GENERATING HTML DASHBOARD", "arena/generate_dashboard.py"),
        ("DEPLOYING TO SERVER", "deploy.py")
    ]

    for name, cmd in steps:
        if not run_step(name, cmd):
            print("\n!!! Global update aborted due to errors.")
            sys.exit(1)

    print("\n" + "="*50)
    print("   ALL STEPS COMPLETED SUCCESSFULLY!")
    print("   Arena Report: http://ovalhalla.ru/my/mech/dashboard.html")
    print("="*50)

if __name__ == "__main__":
    main()
