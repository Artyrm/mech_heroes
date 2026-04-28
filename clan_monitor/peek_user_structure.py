import requests
import json
import os

def peek():
    CONF = json.load(open('config.json', 'r', encoding='utf-8'))
    USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
    BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
    
    HEADERS = {"Content-Type": "application/json"}
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    sid = r["data"]["sessionID"]
    hier = r["data"]["clanData"]["clanState"]["hierarchy"]
    ids = [hier['leader']['member']['userId']] + [s['member']['userId'] for s in hier['slots']]
    
    p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": ids})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
    r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
    users = json.loads(r2["data"]["response"])["Users"]
    
    print("SCANNING ALL MEMBERS FOR NON-EMPTY AVATAR_ID:")
    found = False
    for u in users:
        aid = u.get("avatarId")
        if aid:
            print(f"User: {u.get('nickname')} | AvatarID: {aid}")
            found = True
    if not found:
        print("No non-empty avatarId found in the entire clan.")

if __name__ == "__main__":
    peek()
