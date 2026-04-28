import requests
import json
import os

def peek_clan():
    CONF = json.load(open('config.json', 'r', encoding='utf-8'))
    USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
    BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
    
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    
    clan_state = r.get("data", {}).get("clanData", {}).get("clanState", {})
    print("CLAN STATE DETAILS:")
    print(json.dumps(clan_state, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    peek_clan()
