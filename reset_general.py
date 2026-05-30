import requests
import json
import datetime
import random
import time
import sys
import os

# ==============================================================================
# GENERAL RESET TOOL v1.0.0
# ==============================================================================

CONFIG_FILE = os.path.join('clan_monitor', 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"CRITICAL: {CONFIG_FILE} not found!")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_init_data(conf):
    user_id = conf['USER_ID']
    auth_key = conf['AUTH_KEY']
    version = conf['VERSION']
    base_url = f"https://tanks.ya.patternmasters.ru/{version}"
    
    url = f"{base_url}/init?userid={user_id}"
    payload = {
        "data": {"userID": user_id, "authKey": auth_key},
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 1,
        "version": version
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://app-476209.games.s3.yandex.net",
        "Referer": "https://app-476209.games.s3.yandex.net/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    resp = r.json()
    
    if "error" in resp:
        print(f"API Error: {resp['error']}")
        sys.exit(1)
        
    data = resp.get("data", {})
    user_state_raw = data.get("userState", "{}")
    user_state = json.loads(user_state_raw) if isinstance(user_state_raw, str) else user_state_raw
    
    return {
        "sessionID": data.get("sessionID"),
        "clanVersion": data.get("clanData", {}).get("clanState", {}).get("version", 0),
        "lastCommandId": data.get("userState", {}).get("lastCommandId", 0) if isinstance(data.get("userState"), dict) else user_state.get("lastCommandId", 0),
        "generals": user_state.get("generals", {}),
        "version": version,
        "base_url": base_url
    }

def reset_general(conf, init_data, general_id):
    user_id = conf['USER_ID']
    sid = init_data['sessionID']
    clan_version = init_data['clanVersion']
    last_cmd_id = init_data['lastCommandId']
    base_url = init_data['base_url']
    version = init_data['version']
    
    # Find stateId
    general_data = init_data['generals'].get(general_id)
    if not general_data:
        print(f"WARNING: General '{general_id}' not found in player data. Using StateID=0.")
        state_id = 0
    else:
        state_id = general_data.get('stateId', 0)
        print(f"Found General '{general_id}' with StateID: {state_id}, Level: {general_data.get('level')}")

    now = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
    
    command_payload = {
        "data": {
            "userId": user_id,
            "sessionID": sid,
            "commands": [{
                "commandNumber": last_cmd_id + 1,
                "hash": random.randint(-2147483648, 2147483647),
                "id": "ResetGeneralCommand",
                "paramsStr": json.dumps({"ID": general_id, "StateID": state_id}),
                "time": now
            }],
            "clanVersion": clan_version
        },
        "locale": "ru",
        "platform": "YandexGamesDesktop",
        "requestId": 2,
        "version": version
    }
    
    url = f"{base_url}/commands?userid={user_id}"
    print(f"Sending ResetGeneralCommand for '{general_id}'...")
    
    r = requests.post(url, json=command_payload, headers={"Content-Type": "application/octet-stream"}, timeout=10)
    print(f"Status Code: {r.status_code}")
    try:
        resp_json = r.json()
        
        # API level error
        if "error" in resp_json:
            print(f"API Error: {resp_json['error']}")
            return

        # Command level error
        cmd_results = resp_json.get("data", {}).get("data", [])
        if cmd_results and "error" in cmd_results[0]:
            cmd_error = cmd_results[0]["error"]
            print(f"Reset FAILED (Server Side): {cmd_error.get('message')}")
            if "inner" in cmd_error:
                print(f"Details: {cmd_error['inner'].get('message')}")
        elif cmd_results:
            print(f"Reset SUCCESSFUL for '{general_id}'!")
            # print(f"Response: {json.dumps(resp_json, indent=2)}")
        else:
            print("Unexpected response format (no command results).")
            print(f"Response: {json.dumps(resp_json, indent=2)}")
            
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Response text: {r.text}")

if __name__ == "__main__":
    conf = load_config()
    
    if len(sys.argv) < 2:
        print("Usage: python reset_general.py <general_id>")
        print("Example: python reset_general.py eva")
        print("\nAvailable generals (from dictionary): kali, eva, chong, olaf, toxic, brain, mantiss, frosty, gans, levsha, suriya, sky")
        sys.exit(0)
        
    target_gen = sys.argv[1].lower()
    
    print("[*] Synchronizing with game server...")
    init_data = get_init_data(conf)
    
    reset_general(conf, init_data, target_gen)
