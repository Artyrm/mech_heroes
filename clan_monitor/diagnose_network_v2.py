import socket
import subprocess
import time
import os

def check_game_connection():
    domain = "tanks.ya.patternmasters.ru"
    print(f"[*] Проверка домена {domain}...")
    
    start_time = time.time()
    try:
        target_ip = socket.gethostbyname(domain)
        print(f"[*] IP сервера: {target_ip}")
        
        print("[*] Запуск netstat -n -p TCP...")
        # Используем те же параметры, что планируются для бота
        proc = subprocess.run(['netstat', '-n', '-p', 'TCP'], capture_output=True, text=True, timeout=15)
        
        pattern = f"{target_ip}:443"
        is_active = (pattern in proc.stdout) and ("ESTABLISHED" in proc.stdout)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if is_active:
            print(f"[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ!")
        else:
            print("[*] Соединение не найдено (игра закрыта или в фоне).")
            
        print(f"\n[OK] Время выполнения проверки: {elapsed:.3f} сек.")
        
    except Exception as e:
        print(f"[!] Ошибка: {e}")

if __name__ == "__main__":
    check_game_connection()
