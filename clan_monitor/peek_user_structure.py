import requests
import json
import os

def peek():
    CONF = json.load(open('config.json', 'r', encoding='utf-8'))
    USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
    BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
    
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    sid = r["data"]["sessionID"]
    hier = r["data"]["clanData"]["clanState"]["hierarchy"]
    ids = [hier['leader']['member']['userId']]
    
    p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": ids})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
    r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2).json()
    user = json.loads(r2["data"]["response"])["Users"][0]
    
    print("ALL KEYS IN USER OBJECT:")
    for k in sorted(user.keys()):
        val_type = type(user[k]).__name__
        val_preview = str(user[k])[:50] + "..." if isinstance(user[k], (str, dict, list)) else user[k]
        print(f" - {k} ({val_type}): {val_preview}")

if __name__ == "__main__":
    peek()
