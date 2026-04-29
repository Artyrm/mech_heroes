import requests
import json
import os
from datetime import datetime

CONFIG_FILE = 'config.json'

def check_status():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        conf = json.load(f)

    user_id = conf.get('USER_ID')
    version = conf.get('VERSION')
    
    base_url = f"https://tanks.ya.patternmasters.ru/{version}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # Генерируем фейковый запрос с невалидным sessionID
    payload = {
        "data": {
            "userId": user_id,
            "sessionID": f"{user_id}_DEADBEEF000000000000000000000000",
            "commands": [
                {
                    "commandNumber": 1,
                    "hash": 123456789,
                    "id": "TrackUsageTimeCommand",
                    "paramsStr": "null",
                    "time": datetime.now().strftime("%d/%m/%Y_%H:%M:%S.0000")
                }
            ]
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 999999,
        "version": version
    }

    print(f"[*] Отправка пробного запроса (Offline Test) для ID {user_id}...")
    try:
        response = requests.post(f"{base_url}/commands?userid={user_id}", json=payload, headers=headers)
        print(f"[*] Статус ответа: {response.status_code}")
        print(f"[*] Тело ответа: {response.text}")
        
    except Exception as e:
        print(f"[!] Ошибка: {e}")

if __name__ == "__main__":
    check_status()
