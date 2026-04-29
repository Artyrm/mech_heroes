import requests
import json
import os
import sys

CONFIG_FILE = 'config.json'

def run_test():
    if not os.path.exists(CONFIG_FILE):
        print(f"Ошибка: {CONFIG_FILE} не найден.")
        return

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        conf = json.load(f)

    user_id = conf.get('USER_ID')
    auth_key = conf.get('AUTH_KEY')
    version = conf.get('VERSION')
    
    base_url = f"https://tanks.ya.patternmasters.ru/{version}"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://app-476209.games.s3.yandex.net",
        "Referer": "https://app-476209.games.s3.yandex.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    payload = {
        "data": {
            "userID": user_id,
            "authKey": auth_key
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 1,
        "version": version
    }

    print(f"[*] Отправка экспериментального /init (версия {version})...")
    try:
        response = requests.post(f"{base_url}/init?userid={user_id}", json=payload, headers=headers)
        r_json = response.json()
        
        if "error" in r_json:
            print(f"[!] Сервер вернул ошибку: {r_json['error']}")
        else:
            new_sid = r_json.get("data", {}).get("sessionID")
            print(f"[+] Успех! Получен новый sessionID: {new_sid[:15]}...")
            print("[*] Теперь проверь игровую вкладку в браузере. Выкинуло?")
            
    except Exception as e:
        print(f"[!] Произошла ошибка при запросе: {e}")

if __name__ == "__main__":
    run_test()
