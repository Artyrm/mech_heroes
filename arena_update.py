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

def main():
    print("="*50)
    print("      ARENA ANALYTICS GLOBAL UPDATE & DEPLOY")
    print("="*50)

    steps = [
        ("FETCHING LATEST DATA", "arena/fetch_arena.py"),
        ("SYNCING FROM INIT DUMPS", "arena/sync_from_init.py"),
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
    print("   Arena Report: http://ovalhalla.ru/my/mech/arena.html")
    print("="*50)

if __name__ == "__main__":
    main()
