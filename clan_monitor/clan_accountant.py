import requests, json, os, sys, socket, subprocess, re, random, time, argparse, traceback
from datetime import datetime, timedelta, timezone
import numpy as np

# ==============================================================================
# CLAN ACCOUNTANT v0.3.11 (2026-05-25) - CORRECTED TRUTH LOGIC
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

def fetch_data(explicit_dump=None, force_run=False, debug_mode=False):
    global VERSION, BASE_URL
    if explicit_dump:
        if os.path.exists(explicit_dump):
            r = load_json(explicit_dump)
            if "data" in r:
                d = r.get("data", {})
                sid, hier = d.get("sessionID"), d.get("clanData", {}).get("clanState", {}).get("hierarchy")
                rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
                users = r.get("users_raw_infos", [])
                return hier, users, rating
def safe_log(msg):
    import time
    for _ in range(3): # Попробуем записать 3 раза
        try:
            with open(os.path.join(REPO_ROOT, 'logs', 'accountant.log'), 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S,%f')[:-4]}] {msg}\n")
            return
        except PermissionError:
            time.sleep(0.1) # Ждем 100мс перед следующей попыткой
    print(f"FAILED TO LOG: {msg}")

def fetch_data(explicit_dump=None, force_run=False, debug_mode=False):
    global VERSION, BASE_URL
    if explicit_dump:
        if os.path.exists(explicit_dump):
            r = load_json(explicit_dump)
            if "data" in r:
                d = r.get("data", {})
                sid, hier = d.get("sessionID"), d.get("clanData", {}).get("clanState", {}).get("hierarchy")
                rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
                users = r.get("users_raw_infos", [])
                return hier, users, rating
    
    if is_user_active() and not force_run:
        msg = "[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Обновление пропущено."
        print(msg)
        safe_log(msg)
        return None, None, None

    try:
        def perform_refresh(sid, clan_version, last_cmd_id):
            now = datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
            cmd_body = {"data": {"userId": USER_ID, "sessionID": sid, "commands": [{"commandNumber": last_cmd_id + 1, "hash": random.randint(-2147483648, 2147483647), "id": "UseServiceCommand", "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}), "time": now}], "clanVersion": clan_version}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 3, "version": VERSION}
            return requests.post(f"{BASE_URL}/commands?userid={USER_ID}", json=cmd_body, headers={"Content-Type": "application/octet-stream"}, timeout=10).json()

        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r1_resp = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS)
        r1 = r1_resp.json()
        
        # Auto-healing logic
        if r1.get("error", {}).get("code") == 61058:
            new_version = r1["error"]["message"].split("version ")[1].split(". Can")[0].strip()
            print(f"[*] Auto-updating config.json with new game version: {new_version}")
            CONF['VERSION'] = new_version
            with open(os.path.join(SCRIPT_DIR, CONFIG_FILE), 'w') as f: json.dump(CONF, f, indent=4)
            VERSION = new_version
            BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
            p1["version"] = VERSION
            r1_init = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
            r1 = r1_init

        try: perform_refresh(r1['data']['sessionID'], r1['data']['clanData']['clanState']['version'], r1['data']['userState']['lastCommandId'])
        except Exception as e: print(f"DEBUG: perform_refresh failed: {e}")
            
        time.sleep(5)
        r_resp = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS)
        r_resp.raise_for_status()
        r = r_resp.json()
        
        d = r.get("data", {})
        sid = d.get("sessionID")
        clan_state = d.get("clanData", {}).get("clanState", {})
        hier = clan_state.get("hierarchy")
        rating = int(clan_state.get("rating", 0))
        
        if not hier:
            print(f"[DEBUG] Иерархия не найдена. Ответ API (первые 500 симв.): {str(r)[:500]}")
            return None, None, None
        
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots'] if s.get('member', {}).get('userId', -1) != -1}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        
        response_data = r2.get("data", {})
        if not response_data:
             print(f"[DEBUG] Пустой data в ответе GetUsersRawInfos. Полный ответ: {r2}")
             return None, None, None
             
        users = json.loads(response_data.get("response", "{}")).get("Users", [])
        if not users:
            print(f"[DEBUG] Пользователи не получены. Ответ: {r2}")
        
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
        translated = translate_traits_batch(raw_list); aid = u.get("avatarId")
        if aid and aid != "default": translated = f"{translated} | Фон: {aid}" if translated else f"Фон: {aid}"
        names_map[str(u['userId'])] = {"nick": u['nickname'], "role": "Soldier", "traits": translated}

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
        is_current_week = (w_key == all_ws[-1])
        players = set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        
        # Глобальный список игроков со сбросами
        reset_players = set()
        for d_str in adj_db:
            reset_players.update(adj_db[d_str].keys())
        
        # Prepare player_resets with automatic detection
        player_resets = {}
        # 1. Add manual adjustments
        for date, users_data in adj_db.items():
            for uid, vals in users_data.items():
                if uid == "burned_override": continue
                if uid not in player_resets: player_resets[uid] = {}
                # Keep existing format but maybe store as dict with time if possible
                player_resets[uid][f"{date} 00:00 (manual)"] = vals
        
        # 2. Detect automatic resets from all snapshots (sd)
        # Sort all snapshots by time
        sorted_sd = sorted(sd, key=lambda x: x['time'])
        for i in range(1, len(sorted_sd)):
            prev_s = sorted_sd[i-1]
            curr_s = sorted_sd[i]
            # Skip weekly Monday 03:00 MSK reset (00:00 UTC)
            msk_time = curr_s['time'].astimezone(timezone(timedelta(hours=3)))
            is_monday_reset = msk_time.weekday() == 0 and msk_time.hour == 3
            if is_monday_reset: continue
            
            for uid, curr_pts in curr_s['pts'].items():
                if uid in prev_s['pts']:
                    prev_pts = prev_s['pts'][uid]
                    # Reset detected if current < previous
                    if curr_pts < prev_pts:
                        msk_time = curr_s['time'].astimezone(timezone(timedelta(hours=3))).strftime("%d.%m %H:%M")
                        if uid not in player_resets: player_resets[uid] = {}
                        if msk_time not in player_resets[uid]:
                            player_resets[uid][msk_time] = [prev_pts, curr_pts]
                        else:
                            player_resets[uid][msk_time].append(curr_pts)
        
        resets_json = json.dumps(player_resets)

        pl_res = {}
        for uid in players:
            daily_growths = [0] * 7
            presence = [False] * 7
            prev_day_end = 0
            use_reset_logic = str(uid) in reset_players

            for i in range(7):
                d_start = monday + timedelta(days=i)
                d_end = d_start + timedelta(days=1)
                day_snaps = sorted([s for s in sd if d_start <= s['time'] < d_end and str(uid) in s['pts']], key=lambda x: x['time'])
                
                # Понедельник всегда база 0
                if i == 0: prev_day_end = 0

                if day_snaps:
                    vals = [s['pts'][str(uid)] for s in day_snaps]
                    
                    if use_reset_logic:
                        # Продвинутая логика накопления (Truth Logic)
                        day_growth = 0
                        last_v = prev_day_end
                        
                        # Учет ручной правки как потенциального пика
                        d_key = d_start.strftime("%Y-%m-%d")
                        manual_vals = adj_db.get(d_key, {}).get(str(uid), [])
                        if not isinstance(manual_vals, list): manual_vals = [manual_vals]
                        
                        for v in vals:
                            # Если есть ручная правка, и она больше текущего зафиксированного пика перед сбросом
                            effective_v = v
                            if v < last_v and manual_vals:
                                last_v = max(last_v, max(manual_vals))
                            
                            if effective_v >= last_v:
                                day_growth += (effective_v - last_v)
                            else:
                                # Сброс обнаружен
                                day_growth += effective_v
                            last_v = effective_v
                        daily_growths[i] = int(day_growth)
                    else:
                        # Обычная логика для стабильных игроков
                        daily_growths[i] = max(0, vals[-1] - prev_day_end)
                    
                    prev_day_end = vals[-1]
                else:
                    daily_growths[i] = 0
                
                d_str = d_start.strftime("%Y-%m-%d")
                ex = adj_db.get(d_str, {}).get(str(uid), [])
                if not isinstance(ex, list): ex = [ex]
                presence[i] = (any(str(uid) in s['pts'] for s in week["days"].get(d_str, [])) if d_str in week["days"] else False) or bool(ex)

            pl_res[uid] = {"growths": daily_growths, "total": sum(daily_growths), "presence": presence, "first_p": next((idx for idx, p in enumerate(presence) if p), 999), "last_p": next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)}

        clan_growths = [sum(p["growths"][i] for p in pl_res.values()) for i in range(7)]
        clan_rats = [None] * 7
        for i in range(7):
            ds = [s for s in sd if (monday+timedelta(days=i)) <= s['time'] < (monday+timedelta(days=i+1)) and s.get('rating') is not None]    
            if ds: clan_rats[i] = ds[-1]['rating']
        
        pre_week_sn_rat = [e for e in sd if e['time'] < monday]
        prev_r = pre_week_sn_rat[-1]['rating'] if pre_week_sn_rat else 11199931
        clan_stats = []        
        for i in range(7):
            curr_r = clan_rats[i]; d_str = (monday + timedelta(days=i)).strftime("%Y-%m-%d"); mb = adj_db.get(d_str, {}).get("burned_override")
            if curr_r is not None and prev_r is not None:
                fch = int(curr_r) - int(prev_r); brn = int(mb) if mb is not None else max(0, clan_growths[i] - fch)
                clan_stats.append({"rating": curr_r, "fact": fch, "burned": brn}); prev_r = curr_r
            else:
                brn = int(mb) if mb is not None else 0
                clan_stats.append({"rating": curr_r or 0, "fact": 0, "burned": brn}); prev_r = curr_r or prev_r

        sorted_ids = sorted(players, key=lambda x: pl_res[x]['total'], reverse=True)
        dupes = {names_map.get(u, {}).get('nick'): u for u in players if [names_map.get(x, {}).get('nick') for x in players].count(names_map.get(u, {}).get('nick')) > 1}
        nav = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==w_key else ""}">{weeks[wk]["label"]}</a>' for wk in all_ws])
        tr = current_rating if w_key == all_ws[-1] else (next((r['rating'] for r in reversed(clan_stats) if r['rating']), 0))
        today_idx = datetime.now(timezone.utc).weekday()
        
        c_cells = [f'<td style="text-align:center"><div class="fact-grow">{"+"+fmt(s["fact"]) if s["fact"]>=0 else "-"+fmt(-s["fact"])}</div><div class="burned">🔥 -{fmt(s["burned"])}</div></td>' if s["rating"] else f'<td style="text-align:center; color:#30363d">{"-" if i<=today_idx else ""}</td>' for i, s in enumerate(clan_stats)]
        s_cells = [f'<td style="text-align:center"><span class="day-growth">+{fmt(cg)}</span></td>' for cg in clan_growths]

        html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>ОРДА | {week['label']}</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    :root {{ --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --error: #f85149; --border: #30363d; --text: #c9d1d9; }}
    body {{ background: #0d1117; color: var(--text); font-family: 'Inter', sans-serif; margin: 25px; font-size: 16px; overflow-x: hidden; }}
    header {{ text-align: center; margin-bottom: 30px; }}
    h1 {{ font-family: 'Orbitron'; font-size: 3rem; color: #fff; margin: 0; letter-spacing: 12px; }}
    .subtitle {{ color: var(--gold); letter-spacing: 6px; font-size: 0.9rem; text-transform: uppercase; font-weight: 500; }}
    .update-time {{ font-size: 1rem; color: #fff; text-align: center; padding: 12px; background: rgba(0,0,0,0.5); border-bottom: 2px solid var(--accent); font-family: 'Roboto Mono'; letter-spacing: 2px; font-weight: 700; }}
    nav {{ display: flex; gap: 10px; justify-content: center; margin-bottom: 25px; flex-wrap: wrap; }}
    nav a {{ text-decoration: none; color: #8b949e; padding: 8px 16px; border-radius: 6px; background: var(--card); border: 1px solid var(--border); font-size: 0.9rem; transition: 0.3s; }}
    nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .table-container {{ background: var(--card); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
    th {{ background: #0b0e14; padding: 12px; color: #8b949e; font-size: 0.65rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
    .clan-row {{ background: #1c2128; font-weight: 700; }}
    .clan-row td {{ border-bottom: 2px solid var(--border); padding: 10px; }}
    .summary-row {{ background: rgba(88, 166, 255, 0.1); }}
    .summary-row td {{ padding: 25px 20px; color: var(--accent); font-weight: 700; border-bottom: 3px solid var(--accent); }}
    .clan-score {{ font-size: 1.4rem; font-family: 'Roboto Mono'; display: block; }}
    .burned {{ color: var(--error); font-size: 0.7rem; font-family: 'Roboto Mono'; opacity: 0.8; }}
    .fact-grow {{ color: var(--accent); font-size: 0.9rem; font-family: 'Roboto Mono'; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); border-right: 1px solid rgba(48, 54, 61, 0.3); }}
    .nick-cell {{ display: flex; flex-direction: column; gap: 6px; }}
    .nick {{ color: #fff; font-weight: 700; font-size: 0.9rem; cursor: pointer; }}
    .trait {{ color: var(--gold); font-size: 0.68rem; font-weight: 500; font-style: italic; opacity: 0.7; }}
    .role {{ font-size: 0.58rem; color: #8b949e; border: 1px solid var(--border); padding: 1px 3px; border-radius: 3px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 0.9rem; color: var(--green); font-weight: 700; }}
    .absent {{ color: var(--error); font-weight: 900; font-size: 1.1rem; font-family: 'Orbitron'; }}
    .no-growth {{ color: #484f58; opacity: 0.4; font-family: 'Roboto Mono'; text-align: center; }}
    .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }}
    .modal-content {{ background: var(--card); margin: 15% auto; padding: 20px; border: 1px solid var(--border); width: 400px; border-radius: 8px; color: var(--text); }}
</style>
<script>
    const playerResets = {resets_json};
    function showResets(nick, uid) {{
        const resets = playerResets[uid];
        const modal = document.getElementById('resetsModal');
        const content = document.getElementById('resetsContent');
        if (!resets) {{ content.innerHTML = `<h3>${{nick}}</h3><p>Нет записей о сбросах.</p>`; }}
        else {{
            // Convert to array of {{date_str, timestamp, info}} for sorting
            const resetEntries = Object.entries(resets).map(([date, vals]) => {{
                // Try to parse date from string (e.g., "11.06 14:27" or "2026-06-04 00:00 (manual)")
                let timestamp = 0;
                if (date.includes("(manual)")) {{
                    timestamp = new Date(date.split(" ")[0]).getTime();
                }} else {{
                    const [d, t] = date.split(" ");
                    const [day, mon] = d.split(".");
                    timestamp = new Date(2026, mon-1, day, ...t.split(":").map(Number)).getTime();
                }}
                return {{ date, timestamp, vals }};
            }});
            
            // Filter last 7 days and sort reverse chronologically
            const now = new Date().getTime();
            const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
            
            const filteredResets = resetEntries
                .filter(e => e.timestamp >= sevenDaysAgo)
                .sort((a, b) => b.timestamp - a.timestamp);

            let html = `<h3>${{nick}} - История сбросов (последние 7 дней)</h3><ul>`;
            if (filteredResets.length === 0) {{
                html += `<li>Нет записей за последние 7 дней.</li>`;
            }} else {{
                filteredResets.forEach(e => {{
                    html += `<li>${{e.date}}: ${{e.vals.join(', ')}}</li>`;
                }});
            }}
            html += `</ul>`;
            content.innerHTML = html;
        }}
        modal.style.display = 'block';
    }}
    function closeModal() {{ document.getElementById('resetsModal').style.display = 'none'; }}
</script>
</head><body>
<div id="resetsModal" class="modal" onclick="closeModal()"><div class="modal-content" onclick="event.stopPropagation()"><div id="resetsContent"></div><button onclick="closeModal()">Закрыть</button></div></div>
<header>
<h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE</div></header>
<nav>{nav}</nav>
<div class="table-container"><div class="update-time">ДАННЫЕ ОТ: {last_data_ts} (MSK)</div><table>
    <thead><tr><th style="width:30px">№</th><th>Участник</th><th>Звание</th><th style="text-align:center">Всего</th>
    {" ".join([f'<th>{(monday+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
    <tbody>
    <tr class="clan-row"><td style="text-align:center; color:#58a6ff">--</td><td colspan="2">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td><td style="text-align:center"><span class="main-score" style="color:#fff">{fmt(tr)}</span></td>{" ".join(c_cells)}</tr>
    <tr class="clan-row" style="background:#0d1117; height: 45px;"><td style="text-align:center; color:var(--green)">--</td><td colspan="2" style="color:var(--green); font-size: 0.8rem;">СУММАРНЫЙ ЗАРАБОТОК</td><td style="text-align:center"><span class="main-score" style="color:var(--green); font-size: 0.95rem;">{fmt(sum(clan_growths))}</span></td>{" ".join(s_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = names_map.get(uid, {"nick": f"ID:{uid}", "role": "Soldier"}); p_res = pl_res[uid]; nick_sec = f"<div class='nick-cell'><span class='nick' onclick='showResets(\"{p['nick']}\", \"{uid}\")'>{p['nick']}</span>"
            if p.get('nick') in dupes: nick_sec += f"<span class='trait'>({p.get('traits','') if p.get('traits','') else 'Без особых примет'})</span>"
            nick_sec += "</div>"
            html += f"<tr><td style='text-align:center; color:#484f58; font-family:\"Roboto Mono\"; font-size: 0.7rem;'>{count}</td><td>{nick_sec}</td><td><span class='role'>{p['role']}</span></td><td style='text-align:center'><span class='main-score'>{fmt(p_res['total'])}</span></td>"
            for i, g in enumerate(p_res['growths']):
                if is_current_week and i > today_idx: html += '<td style="text-align:center; color:#30363d">-</td>'
                elif g > 0: html += f"<td style='text-align:center'><span class='day-growth'>+{fmt(g)}</span></td>"
                elif i < p_res['first_p']: html += '<td style="text-align:center; color:#8b949e">-</td>'
                elif i > p_res['last_p']: html += '<td style="text-align:center"><span class="absent" title="Покинул клан">X</span></td>'
                else: html += '<td style="text-align:center; color:#484f58; font-size: 0.85rem;">0</td>'
            html += "</tr>"
        html += "</tbody></table></div></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{w_key}.html"), 'w', encoding='utf-8') as f: f.write(html)
    with open(MAIN_REPORT, 'w', encoding='utf-8') as f:
        latest_wk = sorted(weeks.keys())[-1]
        f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{latest_wk}.html"></head></html>')

if __name__ == "__main__":
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), 'replace')
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach(), 'replace')
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force API fetch even if user is active")
    parser.add_argument("--dump", help="Path to a specific JSON dump to process")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    h, u, r = fetch_data(force_run=args.force, debug_mode=args.debug)
    if h is not None:
        if h:
            generate_web_report(h, u, r, last_update_time=datetime.now())
            print("[*] ОТЧЕТ УСПЕШНО ОБНОВЛЕН (API Sync).")
            sys.exit(0)
        else:
            print("[*] ОБНОВЛЕНИЕ НЕ ТРЕБУЕТСЯ (Использован актуальный кэш).")
            sys.exit(2) 
    else:
        print("[!] ОШИБКА ОБНОВЛЕНИЯ: Не удалось получить данные.")
        sys.exit(1)
