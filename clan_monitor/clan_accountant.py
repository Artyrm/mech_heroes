import requests
import json
import os
import sys
import socket
import subprocess
import re
import random
import time
from datetime import datetime, timedelta, timezone
import numpy as np

# ==============================================================================
# CLAN ACCOUNTANT v0.2.9 (2026-05-17)
# ==============================================================================

CONFIG_FILE = 'config.json'
ADJUSTMENTS_FILE = 'manual_adjustments.json'
TRANS_CACHE_FILE = 'translations_cache.json'
REPORTS_DIR = 'reports'
MAIN_REPORT = 'index.html'
VERSION_NUM = "0.2.9"

def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")

def is_user_active() -> bool:
    target_ip = "84.201.164.35"
    try:
        cmd = f'netstat -n -p TCP | findstr "{target_ip}"'
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if "ESTABLISHED" in proc.stdout:
            print(f"[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ с сервером игры.")
            return True
    except Exception:
        pass
    return False

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

CONF = load_json(CONFIG_FILE)
if not CONF:
    print("CRITICAL: config.json not found!"); sys.exit(1)

USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

SNAPSHOTS_DIR, SCRIPT_DIR = 'snapshots', os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
INIT_DUMPS_DIR = os.path.join(REPO_ROOT, 'init_dumps')
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, 'clan', 'ORDA')
REPORTS_DIR, MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'reports'), os.path.join(OUTPUT_ROOT, 'index.html')
MEMBERS_DB = 'members_name_db.json'

for d in [SNAPSHOTS_DIR, REPORTS_DIR, INIT_DUMPS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

TRANS_CACHE = load_json(TRANS_CACHE_FILE)

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
    with open(TRANS_CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(TRANS_CACHE, f, ensure_ascii=False)
    return translated

HEADERS = {"Content-Type": "application/json", "Origin": "https://app-476209.games.s3.yandex.net", "Referer": "https://app-476209.games.s3.yandex.net/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

def fetch_data(explicit_dump=None, force_run=False, debug_mode=False):
    global VERSION, BASE_URL
    
    # ПРОВЕРКА СЕССИИ перед любым запросом к API
    if is_user_active() and not force_run:
        msg = "[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Обновление пропущено (работаем с кэшем)."
        print(msg)
        with open(os.path.join(REPO_ROOT, 'logs', 'accountant.log'), 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S,%f')[:-4]}] {msg}\n")
        
        # Если игра запущена, берем самый свежий дамп, если он есть
        dumps = sorted(glob.glob(os.path.join(INIT_DUMPS_DIR, "init_*.json")))
        if dumps:
            r = load_json(dumps[-1])
            if "data" in r:
                d = r.get("data", {})
                sid, hier = d.get("sessionID"), d.get("clanData", {}).get("clanState", {}).get("hierarchy")
                rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
                users = r.get("users_raw_infos", [])
                return hier, users, rating
        return None, None, None

    try:
        # Принудительная синхронизация
        def perform_refresh(sid, clan_version, last_cmd_id):
            now = datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
            cmd_body = {
                "data": {
                    "userId": USER_ID, "sessionID": sid,
                    "commands": [{"commandNumber": last_cmd_id + 1, "hash": random.randint(-2147483648, 2147483647), "id": "UseServiceCommand", 
                                 "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}), 
                                 "time": now}],
                    "clanVersion": clan_version
                },
                "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 3, "version": VERSION
            }
            return requests.post(f"{BASE_URL}/commands?userid={USER_ID}", json=cmd_body, headers={"Content-Type": "application/octet-stream"}, timeout=10).json()
            
        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        # 1. Запрос
        r1 = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        print(f"[DEBUG] INIT 1: Session={r1.get('data', {}).get('sessionID')}, LastCmd={r1.get('data', {}).get('userState', {}).get('lastCommandId')}")
        
        # 2. Пин
        try:
            refresh_resp = perform_refresh(r1['data']['sessionID'], r1['data']['clanData']['clanState']['version'], r1['data']['userState']['lastCommandId'])
            err = refresh_resp.get('data', {}).get('data', [{}])[0].get('error')
            print(f"[DEBUG] REFRESH: {'SUCCESS' if not err else 'ERROR: ' + str(err.get('code'))}")
        except Exception as e:
            print(f"[DEBUG] Refresh failed: {e}")
        
        # Задержка для того, чтобы сервер успел обработать Refresh
        print("[DEBUG] Waiting 5 seconds for server sync...")
        time.sleep(5)
        
        # 3. Финал: выполняем init и работаем с его результатом
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        arena = r.get('data', {}).get('userState', {}).get('arena', {})
        history = arena.get('battlesHistory', [])
        latest_battle = history[0].get('fightTime') if history else 'None'
        print(f"[DEBUG] INIT 2: LastBattle={latest_battle}, ArenaTime={arena.get('leaderboards', {}).get('lastUpdateTime')}")
        
        # Извлекаем данные из r (который теперь содержит актуальный результат)
        d = r.get("data", {})
        sid = d.get("sessionID")
        clan_data = d.get("clanData", {})
        clan_state = clan_data.get("clanState", {})
        hier = clan_state.get("hierarchy")
        rating = int(clan_state.get("rating", 0))
        
        if not hier:
            print("[!] ОШИБКА: Иерархия не найдена в ответе.")
            return None, None, None
            
        # Получение актуальных данных о пользователях
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots'] if s.get('member', {}).get('userId', -1) != -1}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        
        users = json.loads(r2.get("data", {}).get("response", "{}")).get("Users", [])
        
        # Сохранение дампа
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dump_path = os.path.join(INIT_DUMPS_DIR, f'init_{timestamp}.json')
        with open(dump_path, 'w', encoding='utf-8') as f: json.dump(r, f, ensure_ascii=False, indent=4)
        
        # Исправление версии, если сервер требует обновления
        if "error" in r and isinstance(r.get('error'), dict) and r['error'].get('code') == 61058:
            m = re.search(r"later version (\d+\.\d+\.\d+)", r['error'].get('message', ''))
            if m:
                new_v = m.group(1); CONF['VERSION'] = new_v
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(CONF, f, indent=4)
                VERSION = new_v; BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
                return fetch_data(explicit_dump, force_run, debug_mode)

        return hier, users, rating
    except Exception as e:
        print(f"[!] ФАТАЛЬНАЯ ОШИБКА FETCH: {e}")
        return None, None, None
    except Exception as e:
        return None, None, None

def generate_web_report(hier, users, current_rating, last_update_time=None):
    now_utc = last_update_time.astimezone(timezone.utc) if last_update_time else datetime.now(timezone.utc)
    now_mskq = now_utc.astimezone(timezone(timedelta(hours=3)))
    # Используем UTC для индекса дня, так как недели считаются по UTC.
    # Это предотвращает преждевременное скрытие данных за прошедшую неделю в период с 00:00 до 03:00 МСК.
    today_idx = now_utc.weekday()
    names_map = load_json(MEMBERS_DB)
    cur_ids = {str(hier['leader']['member']['userId'])} | {str(s['member']['userId']) for s in hier['slots'] if s.get('member', {}).get('userId', -1) != -1}
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
    with open(MEMBERS_DB, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    roles_snap_path = os.path.join(SNAPSHOTS_DIR, f"roles_{now_utc.strftime('%Y')}_W{now_utc.strftime('%W')}.json")
    with open(roles_snap_path, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
    for s in hier['slots']: pts[str(s['member']['userId'])] = int(s['member']['points'])
    with open(os.path.join(SNAPSHOTS_DIR, f"points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"), 'w', encoding='utf-8') as f: json.dump({"pts": pts, "clanRating": current_rating}, f)

    snf = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_')])
    sd = []
    for fs in snf:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if m:
            dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
            try:
                with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as f:
                    d = json.load(f); pts_m = d.get("pts", d); r_val = d.get("clanRating")
                    try: r_int = int(r_val) if r_val is not None else None
                    except: r_int = None
                    sd.append({"time": dt, "pts": {k: int(v) for k,v in pts_m.items() if k.isdigit()}, "rating": r_int})
            except: pass

    last_data_ts = "НЕТ ДАННЫХ"
    if sd: last_data_ts = sd[-1]['time'].astimezone(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M")

    adj_db, weeks = load_json(ADJUSTMENTS_FILE), {}
    for e in sd:
        m_dt = (e['time'] - timedelta(days=e['time'].weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        wk = m_dt.strftime("%Y_W%W")
        if wk not in weeks: weeks[wk] = {"monday": m_dt, "label": f"{m_dt.strftime('%d.%m')} - {(m_dt+timedelta(days=6)).strftime('%d.%m')}", "days": {}}
        dk = e['time'].strftime("%Y-%m-%d")
        if dk not in weeks[wk]["days"]: weeks[wk]["days"][dk] = []
        weeks[wk]["days"][dk].append(e)

    all_ws = sorted(weeks.keys())
    for w_key in all_ws:
        is_current_week = (w_key == all_ws[-1]); roles_snap = os.path.join(SNAPSHOTS_DIR, f"roles_{w_key}.json")
        week_names_map = load_json(roles_snap) if os.path.exists(roles_snap) else names_map
        week, players = weeks[w_key], set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        pl_res, monday = {}, week["monday"]
        
        for uid in players:
            daily_growths, presence = [0] * 7, [False] * 7
            # Начало недели - 0 очков
            stream_times, stream_vals = [monday.timestamp()], [0]
            banked, prev_val = 0, 0
            
            sn_list = sorted([s for s in sd if monday <= s['time'] < monday + timedelta(days=7) and uid in s['pts']], key=lambda x: x['time'])
            
            for sn in sn_list:
                ts_val, val = sn['time'], sn['pts'][uid]
                if val < prev_val:
                    # Сброс до 0 зафиксирован. Пик перед сбросом добавляется в банк.
                    peak = prev_val
                    d_str = ts_val.strftime("%Y-%m-%d")
                    mv = adj_db.get(d_str, {}).get(uid, 0)
                    if isinstance(mv, list): mv = max(mv) if mv else 0
                    peak = max(peak, int(mv))
                    
                    banked += peak
                    stream_times.append(ts_val.timestamp() - 1) 
                    stream_vals.append(banked)
                
                stream_times.append(ts_val.timestamp())
                stream_vals.append(banked + val)
                prev_val = val

            # Обеспечиваем данные до конца воскресенья
            week_end_ts = (monday + timedelta(days=7)).timestamp()
            ts_arr, vs_arr = np.array(stream_times), np.array(stream_vals)
            if ts_arr[-1] < week_end_ts:
                ts_arr = np.append(ts_arr, week_end_ts)
                vs_arr = np.append(vs_arr, vs_arr[-1])

            boundary_vals = []
            for i in range(8):
                bt = (monday + timedelta(days=i)).timestamp()
                v_i = np.interp(bt, ts_arr, vs_arr)
                boundary_vals.append(v_i)
            
            for i in range(7):
                daily_growths[i] = max(0, int(boundary_vals[i+1]) - int(boundary_vals[i]))
                d_start = monday + timedelta(days=i); d_str = d_start.strftime("%Y-%m-%d"); sn = week["days"].get(d_str, [])
                ex = adj_db.get(d_str, {}).get(uid, []); ex = [ex] if not isinstance(ex, list) else ex
                if is_current_week and i == today_idx: is_present = (uid in cur_ids) or bool(ex)
                else:
                    is_present = any(uid in s['pts'] for s in sn) if sn else False
                    if not is_present and bool(ex): is_present = True
                presence[i] = is_present
            pl_res[uid] = {"growths": daily_growths, "total": sum(daily_growths), "presence": presence, "first_p": next((idx for idx, p in enumerate(presence) if p), 999), "last_p": next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)}

        clan_growths, clan_rats = [sum(p["growths"][i] for p in pl_res.values()) for i in range(7)], [None] * 7
        for i in range(7):
            day_snaps = [s for s in sd if (monday+timedelta(days=i)) <= s['time'] < (monday+timedelta(days=i+1)) and s.get('rating') is not None]
            if day_snaps: clan_rats[i] = day_snaps[-1]['rating']
        pre_week_sn = [e for e in sd if e['time'] < monday]; prev_r = pre_week_sn[-1]['rating'] if pre_week_sn else 11199931; clan_stats = []
        for i in range(7):
            curr_r = clan_rats[i]; d_str = (monday + timedelta(days=i)).strftime("%Y-%m-%d"); manual_burned = adj_db.get(d_str, {}).get("burned_override")
            if curr_r is not None and prev_r is not None:
                f_ch = int(curr_r) - int(prev_r); brn = int(manual_burned) if manual_burned is not None else max(0, clan_growths[i] - f_ch)
                clan_stats.append({"rating": curr_r, "fact": f_ch, "burned": brn}); prev_r = curr_r
            else:
                brn = int(manual_burned) if manual_burned is not None else 0
                clan_stats.append({"rating": curr_r or 0, "fact": 0, "burned": brn}); prev_r = curr_r or prev_r
        
        sorted_ids = sorted(players, key=lambda x: pl_res[x]['total'], reverse=True)
        dupes = {week_names_map.get(u, {}).get('nick'): u for u in players if [week_names_map.get(x, {}).get('nick') for x in players].count(week_names_map.get(u, {}).get('nick')) > 1}
        nav = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==w_key else ""}">{weeks[wk]["label"]}</a>' for wk in all_ws])
        target_r = current_rating if w_key == all_ws[-1] else (next((r['rating'] for r in reversed(clan_stats) if r['rating']), 0))
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
    nav a {{ text-decoration: none; color: #8b949e; padding: 8px 16px; border-radius: 6px; background: var(--card); border: 1px solid var(--border); font-size: 0.9rem; }}
    nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .table-container {{ background: var(--card); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
    th {{ background: #0b0e14; padding: 12px; color: #8b949e; font-size: 0.65rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
    .clan-row {{ background: #1c2128; font-weight: 700; }}
    .clan-row td {{ border-bottom: 2px solid var(--border); padding: 10px; }}
    .burned {{ color: var(--error); font-size: 0.7rem; font-family: 'Roboto Mono'; opacity: 0.8; }}
    .fact-grow {{ color: var(--accent); font-size: 0.9rem; font-family: 'Roboto Mono'; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); border-right: 1px solid rgba(48, 54, 61, 0.3); }}
    .nick-cell {{ display: flex; flex-direction: column; gap: 6px; }}
    .nick {{ color: #fff; font-weight: 700; font-size: 0.9rem; }}
    .trait {{ color: var(--gold); font-size: 0.68rem; font-weight: 500; font-style: italic; opacity: 0.7; }}
    .role {{ font-size: 0.58rem; color: #8b949e; border: 1px solid var(--border); padding: 1px 3px; border-radius: 3px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 0.9rem; color: var(--green); font-weight: 700; }}
    .absent {{ color: var(--error); font-weight: 900; font-size: 1.1rem; font-family: 'Orbitron'; }}
</style></head><body><div class="container"><header>
<h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE</div></header>
<nav>{nav}</nav>
<div class="table-container"><div class="update-time">ДАННЫЕ ОТ: {last_data_ts} (MSK)</div><table>
    <thead><tr><th style="width:30px">№</th><th>Участник</th><th>Звание</th><th style="text-align:center">Всего</th>
    {" ".join([f'<th>{(week["monday"]+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
    <tbody>
    <tr class="clan-row"><td style="text-align:center; color:#58a6ff">--</td><td colspan="2">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td><td style="text-align:center"><span class="main-score" style="color:#fff">{fmt(target_r)}</span></td>{" ".join(c_cells)}</tr>
    <tr class="clan-row" style="background:#0d1117; height: 45px;"><td style="text-align:center; color:var(--green)">--</td><td colspan="2" style="color:var(--green); font-size: 0.8rem;">СУММАРНЫЙ ЗАРАБОТОК</td><td style="text-align:center"><span class="main-score" style="color:var(--green); font-size: 0.95rem;">{fmt(sum(clan_growths))}</span></td>{" ".join(s_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = week_names_map.get(uid, {}); p_res = pl_res[uid]; nick_sec = f"<div class='nick-cell'><span class='nick'>{p.get('nick', 'ID:'+uid)}</span>"
            if p.get('nick') in dupes: nick_sec += f"<span class='trait'>({p.get('traits','') if p.get('traits','') else 'Без особых примет'})</span>"
            nick_sec += "</div>"
            html += f"<tr><td style='text-align:center; color:#484f58; font-family:\"Roboto Mono\"; font-size: 0.7rem;'>{count}</td><td>{nick_sec}</td><td><span class='role'>{p.get('role','Soldier')}</span></td><td style='text-align:center'><span class='main-score'>{fmt(p_res['total'])}</span></td>"
            for i, g in enumerate(p_res['growths']):
                if is_current_week and i > today_idx: html += '<td style="text-align:center; color:#30363d">-</td>'
                elif g > 0: html += f"<td style='text-align:center'><span class='day-growth'>+{fmt(g)}</span></td>"
                elif i < p_res['first_p']: html += '<td style="text-align:center; color:#8b949e">-</td>'
                elif i > p_res['last_p']: html += '<td style="text-align:center"><span class="absent" title="Покинул клан">X</span></td>'
                else: html += '<td style="text-align:center; color:#484f58; font-size: 0.85rem;">0</td>'
            html += "</tr>"
        html += "</tbody></table></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{w_key}.html"), 'w', encoding='utf-8') as f: f.write(html)
    with open(MAIN_REPORT, 'w', encoding='utf-8') as f: f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{all_ws[-1]}.html"></head></html>')

if __name__ == "__main__":
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), 'replace')
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach(), 'replace')
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force API fetch even if user is active")
    parser.add_argument("--dump", help="Path to a specific JSON dump to process")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    def dprint(msg):
        if args.debug: print(f"[DEBUG] {msg}")

    h, u, r = fetch_data(explicit_dump=args.dump, force_run=args.force, debug_mode=args.debug)
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
