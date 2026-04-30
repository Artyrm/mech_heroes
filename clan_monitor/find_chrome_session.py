import os
import re

def find_session_in_chrome():
    user_id = "227408"
    # Паттерн для поиска sessionID в бинарных файлах
    pattern = re.compile(rb"227408_[A-Z0-9]{32}")
    chrome_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    
    found_any = False
    print(f"[*] Ищу следы сессии для {user_id} в файлах Chrome...")

    # Список папок, где обычно лежат данные сайтов
    for root, dirs, files in os.walk(chrome_path):
        if "Local Storage" not in root and "IndexedDB" not in root:
            continue
            
        for file in files:
            # LevelDB файлы (.ldb, .log) и LocalStorage (.localstorage)
            if file.endswith((".log", ".ldb", ".localstorage")):
                full_path = os.path.join(root, file)
                try:
                    # Размер файла для оптимизации (не читаем гигантов)
                    if os.path.getsize(full_path) > 50 * 1024 * 1024:
                        continue
                        
                    with open(full_path, "rb") as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        if matches:
                            for m in set(matches):
                                sid = m.decode('utf-8')
                                print(f"[!] НАЙДЕНО: {sid}")
                                print(f"    Файл: {full_path}")
                                found_any = True
                except:
                    continue

    if not found_any:
        print("[-] Ничего не найдено.")

if __name__ == "__main__":
    find_session_in_chrome()
