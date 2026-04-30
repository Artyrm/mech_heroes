import os
import socket
import subprocess
import re

def check_network_activity():
    domain = "tanks.ya.patternmasters.ru"
    print(f"[*] Проверка сетевой активности для {domain}...")
    
    try:
        # 1. Получаем IP домена
        target_ip = socket.gethostbyname(domain)
        print(f"[*] IP сервера: {target_ip}")
        
        # 2. Выполняем netstat и ищем установленные соединения
        # Флаг -n (числа), -o (PID), -a (все)
        result = subprocess.run(['netstat', '-n', '-o'], capture_output=True, text=True)
        
        # Ищем строку с нашим IP и статусом ESTABLISHED
        pattern = rf"{re.escape(target_ip)}:443\s+ESTABLISHED"
        matches = re.findall(pattern, result.stdout)
        
        if matches:
            print(f"[!] НАЙДЕНО {len(matches)} активных соединений с сервером игры!")
            print("[!] Пользователь СЕЙЧАС в игре или сессия активна.")
            return True
        else:
            print("[-] Активных соединений не обнаружено. Можно безопасно запускать бота.")
            return False
            
    except Exception as e:
        print(f"[!] Ошибка при проверке сети: {e}")
        return None

if __name__ == "__main__":
    check_network_activity()
