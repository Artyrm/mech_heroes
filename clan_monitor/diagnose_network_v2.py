import socket
import subprocess
import time

def check_game_connection():
    domain = "tanks.ya.patternmasters.ru"
    
    # --- Шаг 1: DNS ---
    print(f"[*] Шаг 1: DNS резолвинг {domain}...")
    s1 = time.time()
    try:
        target_ip = socket.gethostbyname(domain)
        dns_time = time.time() - s1
        print(f"[OK] DNS определил IP: {target_ip} за {dns_time:.3f} сек.")
    except Exception as e:
        target_ip = "84.201.164.35"
        dns_time = time.time() - s1
        print(f"[!] DNS ОШИБКА ({e}), используем fallback IP за {dns_time:.3f} сек.")

    # --- Шаг 2: NETSTAT ---
    print(f"[*] Шаг 2: Запуск netstat -n -p TCP | findstr {target_ip}...")
    s2 = time.time()
    cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    netstat_time = time.time() - s2
    
    is_active = ("ESTABLISHED" in proc.stdout)
    print(f"[OK] Netstat отработал за {netstat_time:.3f} сек.")
    
    if is_active:
        print("[!] ИГРА АКТИВНА.")
    else:
        print("[*] Игра не найдена.")

    print(f"\n[ИТОГО] Общее время: {dns_time + netstat_time:.3f} сек.")

if __name__ == "__main__":
    check_game_connection()
