import subprocess
import time

def fast_is_user_active():
    # Прямой IP сервера игры (tanks.ya.patternmasters.ru)
    target_ip = "84.201.164.35"
    
    print(f"[*] Проверка сетевой активности для IP: {target_ip}...")
    start_time = time.time()
    
    try:
        # Запускаем проверку соединений только по этому IP
        cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Если нашли строку с ESTABLISHED - значит игрок в сети
        is_active = ("ESTABLISHED" in proc.stdout)
        
        end_time = time.time()
        print(f"[*] Результат: {'АКТИВЕН' if is_active else 'НЕ АКТИВЕН'}")
        print(f"[*] Время проверки: {end_time - start_time:.3f} сек.")
        return is_active
    except Exception as e:
        print(f"[!] Ошибка: {e}")
        return False

if __name__ == "__main__":
    fast_is_user_active()
