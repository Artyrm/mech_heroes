import requests
import json

USER_ID = 227408
AUTH_KEY = "2B8ADCBE7A00EE8AF838139813C3ABBB"
VERSION = "1.24.0"
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
}

# 1. Call /init to establish session
init_url = f"{BASE_URL}/init?userid={USER_ID}"
init_payload = {
    "data": {"userID": USER_ID, "authKey": AUTH_KEY},
    "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION
}

print("Calling /init...")
r_init = requests.post(init_url, json=init_payload, headers=HEADERS)
print("Init Status:", r_init.status_code)

if r_init.status_code == 200:
    init_data = r_init.json()
    session_id = init_data.get('data', {}).get('sessionID')
    print("Session ID:", session_id)
    
    if session_id:
        # 2. Call /directcommand
        cmd_url = f"{BASE_URL}/directcommand?userid={USER_ID}"
        cmd_payload = {
            "data": {
                "userId": USER_ID,
                "sessionID": session_id,
                "type": "GetUsersRawInfos",
                "request": json.dumps({"users": [47368]}) # Проповедник
            },
            "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION
        }

        print("Requesting GetUsersRawInfos...")
        r = requests.post(cmd_url, json=cmd_payload, headers=HEADERS)
        print("Status Code:", r.status_code)
        try:
            resp = r.json()
            if "data" in resp and "response" in resp["data"]:
                inner = json.loads(resp["data"]["response"])
                users = inner.get("Users", [])
                if users:
                    print("\nKeys in User object:")
                    print(users[0].keys())
                    
                    # Print without squad to see other fields
                    u_copy = dict(users[0])
                    if 'squad' in u_copy: u_copy['squad'] = "..."
                    print("\nUser data (no squad):")
                    print(json.dumps(u_copy, indent=2, ensure_ascii=False))
                else:
                    print("No users returned")
            else:
                print("Response without data:", resp)
        except Exception as e:
            print("Error parsing:", e)
    else:
        print("No session ID returned")
else:
    print("Init failed")
