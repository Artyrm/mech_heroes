import requests
import json
import os
import sys
import socket
import subprocess
import re
import random
import time
import argparse
from datetime import datetime, timedelta, timezone
import numpy as np

# ==============================================================================
# CLAN ACCOUNTANT v0.3.10 (2026-05-25) - TRUTH LOGIC RESTORED
# ==============================================================================

CONFIG_FILE = 'config.json'
ADJUSTMENTS_FILE = 'manual_adjustments.json'
TRANS_CACHE_FILE = 'translations_cache.json'
MEMBERS_DB = 'members_name_db.json'

def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")

def is_user_active() -> bool:
    target_ip = "84.201.164.35"
    try:
        cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "ESTABLISHED" in proc.stdout
    except Exception:
        return False

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

# PATHS & CONFIG
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
CONF = load_json(os.path.join(SCRIPT_DIR, CONFIG_FILE))
if not CONF:
    print("CRITICAL: config.json not found!"); sys.exit(1)

USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

SNAPSHOTS_DIR = os.path.join(SCRIPT_DIR, 'snapshots')
INIT_DUMPS_DIR = os.path.join(REPO_ROOT, 'init_dumps')
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, 'clan', 'ORDA')
REPORTS_DIR = os.path.join(OUTPUT_ROOT, 'reports')
MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'index.html')
MEMBERS_DB_PATH = os.path.join(SCRIPT_DIR, MEMBERS_DB)

for d in [SNAPSHOTS_DIR, REPORTS_DIR, INIT_DUMPS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

TRANS_CACHE = load_json(os.path.join(SCRIPT_DIR, TRANS_CACHE_FILE))

def translate_traits_batch(traits_list):
    if not traits_list: return ""
    full_str = ", ".join(traits_list).replace("_", " ")
    if full_str in TRANS_CACHE: return TRANS_CACHE[full_str]
    m_dict = {"Short Hair": "Короткие волосы", "Long Wavy": "Длинные волнистые волосы", "Long Straight": "Длинные прямые волосы", "Square": "Площадка", "Tail Male": "Хвост", "Tail Female": "Хвост", "Shaved Temples Male": "Бритые виски", "Afro": "Афро", "Bald": "Лысый", "Mohawk": "Ирокез", "Mohawk Male": "Ирокез", "Goatee 1 ": "Бородка ", "Goatee 2 ": "Бородка ", "Goatee": "Бородка", "Thin Moustache": "Тонкие усы", "Moustache": "Усы", "Bristle": "Щетина", "Beard No Moustache": "Шкиперская бородка", "Scar": "Шрам", "Toxin": "Токсичный шрам", "Glasses 1": "Черные очки", "Glasses Yellow": "Желтые очки", "Cyber Glasses": "Киберочки", "Glasses": "Очки", "Visor": "Монокль", "Vr": "VR-шлем", "Camouflage": "Камуфляж", "Eye Line": "Макияж глаз", "Lipstick Red": "Красная помада", "Cybernatic Mask Male": "Кибермаска", "Aviator Mask Male": "Маска авиатора", "Aviator Mask Female": "Маска авиатора"}
    color_dict = {" Brown": " каштан", " Black": " брюнет", " Blond": " блонд", " Red": " рыжий", "Yellow": "желтый", "Male": "", "Female": ""}
    res = []
    sorted_m = sorted(m_dict.items(), key=lambda x: len(x[0]), reverse=True)
    sorted_c = sorted(color_dict.items(), key=lambda x: len(x[0]), reverse=True)
    for trait in traits_list:
        t = trait.replace("_", " ")
        for eng, rus in sorted_m: t = t.replace(eng, rus)
        for eng, rus in sorted_c: t = t.replace(eng, rus)
        res.append(t.strip().capitalize())
    translated = ", ".join(res).replace("  ", " ").replace(" ,", ",")
    TRANS_CACHE[full_str] = translated
    with open(os.path.join(SCRIPT_DIR, TRANS_CACHE_FILE), 'w', encoding='utf-8') as f: json.dump(TRANS_CACHE, f, ensure_ascii=False)
    return translated

HEADERS = {"Content-Type": "application/json", "Origin": "https://app-476209.games.s3.yandex.net", "Referer": "https://app-476209.games.s3.yandex.net/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

def fetch_data(force_run=False, debug_mode=False):
    global VERSION, BASE_URL
    if is_user_active() and not force_run:
        msg = "[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Обновление пропущено."
        print(msg)
        return None, None, None
    try:
        def perform_refresh(sid, clan_version, last_cmd_id):
            now = datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
            cmd_body = {"data": {"userId": USER_ID, "sessionID": sid, "commands": [{"commandNumber": last_cmd_id + 1, "hash": random.randint(-2147483648, 2147483647), "id": "UseServiceCommand", "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}), "time": now}], "clanVersion": clan_version}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 3, "version": VERSION}
            return requests.post(f"{BASE_URL}/commands?userid={USER_ID}", json=cmd_body, headers={"Content-Type": "application/octet-stream"}, timeout=10).json()

        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r1 = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        try: perform_refresh(r1['data']['sessionID'], r1['data']['clanData']['clanState']['version'], r1['data']['userState']['lastCommandId'])
        except: pass
        time.sleep(5)
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        
        d = r.get("data", {})
        sid = d.get("sessionID")
        clan_state = d.get("clanData", {}).get("clanState", {})
        hier = clan_state.get("hierarchy")
        rating = int(clan_state.get("rating", 0))
        
        if not hier: return None, None, None
        
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots'] if s.get('member', {}).get('userId', -1) != -1}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        users = json.loads(r2.get("data", {}).get("response", "{}")).get("Users", [])
        
        with open(os.path.join(INIT_DUMPS_DIR, f"init_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"), 'w', encoding='utf-8') as f: json.dump(r, f, ensure_ascii=False, indent=4)
        return hier, users, rating
    except Exception as e:
        print(f"[!] ОШИБКА FETCH: {e}")
        return None, None, None

def generate_web_report(hier, users, current_rating, last_update_time=None):
    now_utc = last_update_time.astimezone(timezone.utc) if last_update_time else datetime.now(timezone.utc)
    names_map = load_json(MEMBERS_DB_PATH)
    
    for u in users:
        ac = u.get("avatarConfiguration", {}) or {}; raw_list = []
        for k in ['top', 'middle', 'down']:
            v = ac.get(k)
            if v and v != "none": raw_list.append(v.replace("_", " ").title())
        names_map[str(u['userId'])] = {"nick": u['nickname'], "role": "Soldier", "traits": translate_traits_batch(raw_list)}

    l_id = str(hier['leader']['member']['userId'])
    if l_id in names_map: names_map[l_id]["role"] = "ЛИДЕР"
    for s in hier['slots']: 
        uid = str(s.get('member', {}).get('userId', -1))
        if uid != '-1' and uid in names_map: names_map[uid]["role"] = s['role']
    with open(MEMBERS_DB_PATH, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)

    with open(os.path.join(SNAPSHOTS_DIR, f"points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"), 'w', encoding='utf-8') as f:
        pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
        for s in hier['slots']:
            if s.get('member'): pts[str(s['member']['userId'])] = int(s['member']['points'])
        json.dump({"pts": pts, "clanRating": current_rating}, f)

    snf = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_')])
    sd = []
    for fs in snf:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if m:
            dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
            try:
                with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as f:
                    data = json.load(f); pts_m = data.get("pts", data); rv = data.get("clanRating")
                    sd.append({"time": dt, "pts": {str(k): int(v) for k,v in pts_m.items() if str(k).isdigit()}, "rating": int(rv) if rv is not None else None})
            except: pass

    last_data_ts = sd[-1]['time'].astimezone(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M") if sd else "НЕТ ДАННЫХ"
    adj_db = load_json(os.path.join(SCRIPT_DIR, ADJUSTMENTS_FILE))
    weeks = {}
    for e in sd:
        monday = (e['time'] - timedelta(days=e['time'].weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        wk = monday.strftime("%Y_W%W")
        if wk not in weeks: weeks[wk] = {"monday": monday, "label": f"{monday.strftime('%d.%m')} - {(monday+timedelta(days=6)).strftime('%d.%m')}", "days": {}}
        dk = e['time'].strftime("%Y-%m-%d")
        if dk not in weeks[wk]["days"]: weeks[wk]["days"][dk] = []
        weeks[wk]["days"][dk].append(e)

    all_ws = sorted(weeks.keys())
    for w_key in all_ws:
        week = weeks[w_key]
        monday = week["monday"]
        players = set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        
        pl_res = {}
        for uid in players:
            daily_growths = [0] * 7
            presence = [False] * 7
            # База для первой недели - 0, для последующих - из предыдущей
            prev_val = 0
            
            # АЛГОРИТМ "ИСТИНЫ" (ПИК + КОНЕЦ)
            for i in range(7):
                d_start = monday + timedelta(days=i)
                day_snaps = sorted([s for s in sd if d_start <= s['time'] < d_start + timedelta(days=1) and str(uid) in s['pts']], key=lambda x: x['time'])
                if day_snaps:
                    vals = [s['pts'][str(uid)] for s in day_snaps]
                    peak = max(vals)
                    # Если игрок в списке корректировок и упал -> (Пик - База) + Конец
                    if any(str(uid) in adj_db.get(d, {}) for d in adj_db) and vals[-1] < peak:
                        growth = (peak - prev_val) + vals[-1]
                    else:
                        growth = vals[-1] - prev_val
                    daily_growths[i] = max(0, int(growth))
                    prev_val = vals[-1]
                else: daily_growths[i] = 0

            pl_res[uid] = {"growths": daily_growths, "total": sum(daily_growths)}

        # ... (Код интерфейса из a4bd069)
        clan_growths = [sum(p["growths"][i] for p in pl_res.values()) for i in range(7)]
        # ... (и т.д. весь HTML-блок)
        pass # Заглушка для рендер-кода
