import requests
import json
import sys

# Encoding fix for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Your Identity
USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.0"

BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def test_users_info(session_id, user_ids):
    url = f"{BASE_URL}/directcommand?userid={USER_ID}"
    payload = {
        "data": {
            "userId": USER_ID,
            "sessionID": session_id,
            "type": "GetUsersRawInfos",
            "request": json.dumps({"users": user_ids})
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 100,
        "version": VERSION
    }
    
    print(f"Testing /directcommand (GetUsersRawInfos) for {len(user_ids)} users...")
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        raw_resp = response.json()
        if "data" in raw_resp and "response" in raw_resp["data"]:
            inner = json.loads(raw_resp["data"]["response"])
            return inner.get("Users", [])
    return []

def get_all_ids(obj):
    ids = set()
    if isinstance(obj, dict):
        if "userId" in obj: ids.add(obj["userId"])
        for v in obj.values(): ids.update(get_all_ids(v))
    elif isinstance(obj, list):
        for v in obj: ids.update(get_all_ids(v))
    return ids

def run_test():
    url = f"{BASE_URL}/init?userid={USER_ID}"
    payload = {
        "data": {"userID": USER_ID, "authKey": AUTH_KEY},
        "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
    }
    
    print("Testing /init...")
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"ERROR: /init {response.status_code}")
        return

    full_json = response.json()
    if "error" in full_json:
        print("API Error:", full_json["error"])
        return

    resp_data = full_json.get("data", {})
    sid = resp_data.get("sessionID")
    hierarchy = resp_data.get("clanData", {}).get("clanState", {}).get("hierarchy")
    
    if not hierarchy:
        print("Hierarchy not found in response. Available keys in clanData.clanState:", 
              list(resp_data.get("clanData", {}).get("clanState", {}).keys()))
        return

    all_ids = list(get_all_ids(hierarchy))
    print(f"Success! Found {len(all_ids)} members in hierarchy.")
    
    users_data = test_users_info(sid, all_ids)
    print(f"Fetched details for {len(users_data)} users.")
    
    print("\nSample (First 5):")
    for u in users_data[:5]:
        print(f" - {u['nickname']} (ID: {u['userId']}) | Points: (from hierarchy)")

if __name__ == "__main__":
    run_test()
