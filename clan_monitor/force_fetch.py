import json
import os
import requests
import re
from datetime import datetime, timezone

# Load config
with open('clan_monitor/config.json', 'r', encoding='utf-8') as f:
    CONF = json.load(f)

USER_ID = CONF['USER_ID']
AUTH_KEY = CONF['AUTH_KEY']
VERSION = CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch():
    try:
        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if "error" in r:
            print(f"Error: {r['error']}")
            return
            
        d = r.get("data", {})
        hier = d.get("clanData", {}).get("clanState", {}).get("hierarchy")
        rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
        
        pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
        for s in hier['slots']: 
            uid = str(s.get('member', {}).get('userId', -1))
            if uid != '-1':
                pts[uid] = int(s['member']['points'])
        
        now_utc = datetime.now(timezone.utc)
        fn = f"clan_monitor/snapshots/points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump({"pts": pts, "clanRating": rating}, f)
        print(f"Fetched and saved: {fn}")
        print(f"ksotar points: {pts.get('227408')}")
        
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    fetch()
