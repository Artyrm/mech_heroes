import requests
import json
import os
import sys
import socket
import subprocess
import re
from datetime import datetime, timedelta, timezone
import numpy as np

# ==============================================================================
# CLAN ACCOUNTANT v0.2.5 (2026-05-16)
# Core: Mathematical Parity with gen_utc_graph.py
# Logic: UTC-boundary interpolation + Integer truncation
# ==============================================================================

# ==============================================================================
# IDENTITY & CONFIG
# ==============================================================================
CONFIG_FILE = 'config.json'
ADJUSTMENTS_FILE = 'manual_adjustments.json'
TRANS_CACHE_FILE = 'translations_cache.json'
REPORTS_DIR = 'reports'
MAIN_REPORT = 'index.html'
VERSION_NUM = "0.2.5"

def fmt(n: int) -> str:
    """Format integer with narrow no-break space as thousands separator (RU typography, U+202F)."""
    return f"{n:,}".replace(",", "\u202f")

def is_user_active() -> bool:
    """Fast IP-based detector to avoid kicking active sessions."""
    target_ip = "84.201.164.35"
    try:
        # Check only for ESTABLISHED connection to the game server IP
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
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, 'clan', 'ORDA')
REPORTS_DIR, MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'reports'), os.path.join(OUTPUT_ROOT, 'index.html')
REPO_ROOT, MEMBERS_DB = os.path.dirname(SCRIPT_DIR), 'members_name_db.json'
AUTO_PUSH = True 

for d in [SNAPSHOTS_DIR, REPORTS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

TRANS_CACHE = load_json(TRANS_CACHE_FILE)

def translate_traits_batch(traits_list):
    if not traits_list: return ""
    full_str = ", ".join(traits_list).replace("_", " ")
    if full_str in TRANS_CACHE: return TRANS_CACHE[full_str]
    
    # Pre-translate known game components directly
    m_dict = {
        "Short Hair": "Короткие волосы", "Long Wavy": "Длинные волнистые волосы", "Long Straight": "Длинные прямые волосы",
        "Square": "Площадка", "Tail Male": "Хвост", "Tail Female": "Хвост", "Shaved Temples Male": "Бритые виски",
        "Afro": "Афро", "Bald": "Лысый", "Mohawk": "Ирокез", "Mohawk Male": "Ирокез",
        "Goatee 1 ": "Бородка ", "Goatee 2 ": "Бородка ", "Goatee": "Бородка", "Thin Moustache": "Тонкие усы", "Moustache": "Усы",
        "Bristle": "Щетина", "Beard No Moustache": "Шкиперская бородка", "Scar": "Шрам", "Toxin": "Токсичный шрам",
        "Glasses 1": "Черные очки", "Glasses Yellow": "Желтые очки", "Cyber Glasses": "Киберочки", "Glasses": "Очки", "Visor": "Монокль",
        "Vr": "VR-шлем", "Camouflage": "Камуфляж", "Eye Line": "Макияж глаз",
        "Lipstick Red": "Красная помада", "Cybernatic Mask Male": "Кибермаска", "Aviator Mask Male": "Маска авиатора",
        "Aviator Mask Female": "Маска авиатора"
    }
    
    color_dict = {
        " Brown": " каштан", " Black": " брюнет", " Blond": " блонд", " Red": " рыжий", 
        "Yellow": "желтый", "Male": "", "Female": ""
    }
    
    res = []
    # Sort dictionaries by key length descending to prevent partial replacements (e.g. "Glasses" replacing part of "Cyber Glasses")
    sorted_m = sorted(m_dict.items(), key=lambda x: len(x[0]), reverse=True)
    sorted_c = sorted(color_dict.items(), key=lambda x: len(x[0]), reverse=True)
    
    for trait in traits_list:
        t = trait.replace("_", " ")
        for eng, rus in sorted_m: t = t.replace(eng, rus)
        for eng, rus in sorted_c: t = t.replace(eng, rus)
        res.append(t.strip().capitalize())

    
    translated = ", ".join(res)
    # Cleanup possible double spaces from empty gender words
    translated = translated.replace("  ", " ").replace(" ,", ",")
    
    TRANS_CACHE[full_str] = translated
    with open(TRANS_CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(TRANS_CACHE, f, ensure_ascii=False)
    return translated

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch_data():
    global VERSION, BASE_URL
    try:
        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        print(f"[*] Send /init request (VERSION: {VERSION})...")
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if "error" in r:
            err = r['error']
            print(f"[!] API ERROR on /init: {err}")
            
            # Auto-healing: Update version if game updated
            if isinstance(err, dict) and err.get('code') == 61058:
                m = re.search(r"later version (\d+\.\d+\.\d+)", err.get('message', ''))
                if m:
                    new_v = m.group(1)
                    print(f"[*] Auto-updating config.json with new game version: {new_v}")
                    CONF['VERSION'] = new_v
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(CONF, f, indent=4)
                    
                    # Update global and retry
                    VERSION = new_v
                    BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"
                    print("[*] Retrying fetch_data() with new version...")
                    if 'error' in p1: pass # filler
                    return fetch_data()
            
            return None, None, None
            
        d = r.get("data", {})
        sid, hier = d.get("sessionID"), d.get("clanData", {}).get("clanState", {}).get("hierarchy")
        rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
        
        if not hier:
            print("[!] ERROR: 'hierarchy' not found in server response. Are you in a clan?")
            return None, None, None
            
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots'] if s.get('member', {}).get('userId', -1) != -1}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        print(f"[*] Post /directcommand to get member details...")
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        
        if "error" in r2:
            print(f"[!] API ERROR on /directcommand: {r2['error']}")
            return None, None, None
            
        return hier, json.loads(r2["data"]["response"]).get("Users", []), rating
    except Exception as e:
        print(f"[!] FATAL ERROR during network sync: {e}")
        return None, None, None


def generate_web_report(hier, users, current_rating, last_update_time=None):
    now_utc = last_update_time.astimezone(timezone.utc) if last_update_time else datetime.now(timezone.utc)
    now_mskq = now_utc.astimezone(timezone(timedelta(hours=3)))
    update_str = now_mskq.strftime("%d.%m.%Y %H:%M (MSK)")
    today_idx = now_mskq.weekday()
    names_map = load_json(MEMBERS_DB)
    
    # Track current members strictly (excluding empty slots -1)
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
        if uid != '-1' and uid in names_map:
            names_map[uid]["role"] = s['role']
    with open(MEMBERS_DB, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    # Save a per-week role snapshot so historical reports show correct roles
    cur_wk = f"{now_utc.strftime('%Y')}_W{now_utc.strftime('%W')}"
    roles_snap_path = os.path.join(SNAPSHOTS_DIR, f"roles_{cur_wk}.json")
    with open(roles_snap_path, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)

    
    pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
    for s in hier['slots']: pts[str(s['member']['userId'])] = int(s['member']['points'])
    with open(os.path.join(SNAPSHOTS_DIR, f"points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"), 'w', encoding='utf-8') as f:
        json.dump({"pts": pts, "clanRating": current_rating}, f)

    def get_mon(dt): return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    snf = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_')])
    sd = []
    for fs in snf:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if m:
            dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
            try:
                with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as f:
                    d = json.load(f); pts_m = d.get("pts", d)
                    r_val = d.get("clanRating")
                    # Принудительно приводим к int, если это возможно
                    try:
                        r_int = int(r_val) if r_val is not None else None
                    except:
                        r_int = None
                    sd.append({"time": dt, "pts": {k: int(v) for k,v in pts_m.items() if k.isdigit()}, "rating": r_int})
            except: pass


    adj_db, weeks = load_json(ADJUSTMENTS_FILE), {}
    for e in sd:
        m_dt = get_mon(e['time']); wk = m_dt.strftime("%Y_W%W")
        if wk not in weeks: weeks[wk] = {"monday": m_dt, "label": f"{m_dt.strftime('%d.%m')} - {(m_dt+timedelta(days=6)).strftime('%d.%m')}", "days": {}}
        dk = e['time'].strftime("%Y-%m-%d")
        if dk not in weeks[wk]["days"]: weeks[wk]["days"][dk] = []
        weeks[wk]["days"][dk].append(e)

    all_ws = sorted(weeks.keys())
    for w_key in all_ws:
        is_current_week = (w_key == all_ws[-1])
        roles_snap = os.path.join(SNAPSHOTS_DIR, f"roles_{w_key}.json")
        week_names_map = load_json(roles_snap) if os.path.exists(roles_snap) else names_map
        week, players = weeks[w_key], set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        
        pl_res, clan_rats = {}, [None] * 7
        monday = week["monday"]
        
        all_week_sn = []
        for i in range(7):
            d_str = (monday + timedelta(days=i)).strftime("%Y-%m-%d")
            all_week_sn.extend(week["days"].get(d_str, []))
        all_week_sn.sort(key=lambda x: x['time'])

        for uid in players:
            # --- Interpolation-based Daily Growth (Sync with Graph Markers) ---
            import numpy as np
            daily_growths = [0] * 7
            presence = [False] * 7
            
            # EXACT LOGIC FROM gen_utc_graph.py
            # Filter all snapshots (sd) exactly like the graph does
            week_snaps = [s for s in sd if monday <= s['time'] < monday + timedelta(days=7)]
            
            days_data = []
            for i in range(7):
                d_start = monday + timedelta(days=i)
                d_str = d_start.strftime("%Y-%m-%d")
                day_snaps = [s for s in week_snaps if d_start <= s['time'] < d_start + timedelta(days=1) and uid in s['pts']]
                manual = adj_db.get(d_str, {}).get(uid, [])
                if not isinstance(manual, list): manual = [manual]
                manual = [int(v) for v in manual]
                days_data.append({'start': d_start, 'snaps': day_snaps, 'manual': manual})
            
            total_acc = 0
            current_base = 0 # Monday 00:00 starts at 0
            stream_times = [monday]
            stream_vals = [0]

            for idx, day in enumerate(days_data):
                manual_vals = day['manual']
                manual_idx = 0
                session_max = current_base

                for sn in day['snaps']:
                    val = sn['pts'][uid]
                    if val < current_base:
                        # DROP / EXIT
                        missed = 0
                        if manual_idx < len(manual_vals):
                            mv = manual_vals[manual_idx]
                            if mv > session_max: missed = mv - session_max
                            manual_idx += 1
                        total_acc += missed
                        current_base = val
                        session_max = val
                    else:
                        # GROWTH
                        total_acc += (val - current_base)
                        current_base = val
                        session_max = max(session_max, val)
                    stream_times.append(sn['time'])
                    stream_vals.append(total_acc)

                # End of day manual
                while manual_idx < len(manual_vals):
                    mv = manual_vals[manual_idx]
                    if mv > session_max:
                        total_acc += (mv - session_max)
                    session_max = 0
                    current_base = 0
                    manual_idx += 1
                    stream_times.append(stream_times[-1] + timedelta(minutes=1))
                    stream_vals.append(total_acc)

            # 2. Interpolate values at every 00:00 UTC boundary
            boundary_vals = []
            ts = np.array([t.timestamp() for t in stream_times])
            vs = np.array(stream_vals)
            
            # 2. Interpolate values at every 00:00 UTC boundary
            boundary_vals = []
            ts = np.array([t.timestamp() for t in stream_times])
            vs = np.array(stream_vals)
            
            for i in range(8): # Mon 00:00 to Mon 00:00 next week
                b_dt = monday + timedelta(days=i)
                bt = b_dt.timestamp()
                if bt < ts[0]:
                    v_i = 0
                elif bt > ts[-1]:
                    v_i = total_acc
                else:
                    v_i = np.interp(bt, ts, vs)
                boundary_vals.append(v_i)
            
            # 3. Daily growth = Difference between truncated boundaries
            for i in range(7):
                daily_growths[i] = int(boundary_vals[i+1]) - int(boundary_vals[i])
                d_str = (monday + timedelta(days=i)).strftime("%Y-%m-%d")
                if week["days"].get(d_str, []) or daily_growths[i] > 0:
                    presence[i] = True

            if is_current_week:
                presence[today_idx] = (uid in cur_ids) or any(presence)

            pl_res[uid] = {
                "growths": daily_growths, 
                "total": sum(daily_growths), 
                "presence": presence,
                "first_p": next((idx for idx, p in enumerate(presence) if p), 999),
                "last_p": next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)
            }

        clan_growths = [sum(p["growths"][i] for p in pl_res.values()) for i in range(7)]
        pre_week_sn = [e for e in sd if e['time'] < week["monday"]]
        prev_r = pre_week_sn[-1]['rating'] if pre_week_sn else 11199931
        clan_stats = []
        for i in range(7):
            curr_r = clan_rats[i]
            d_str = (week["monday"] + timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Check for manual burned override in the adjustments file
            manual_burned = adj_db.get(d_str, {}).get("burned_override")
            
            if curr_r is not None and prev_r is not None:
                f_ch = int(curr_r) - int(prev_r)
                if manual_burned is not None:
                    brn = int(manual_burned)
                else:
                    brn = max(0, clan_growths[i] - f_ch)
                clan_stats.append({"rating": curr_r, "fact": f_ch, "burned": brn}); prev_r = curr_r
            else:
                brn = int(manual_burned) if manual_burned is not None else 0
                clan_stats.append({"rating": curr_r or 0, "fact": 0, "burned": brn})
                if curr_r: prev_r = curr_r

        sorted_ids = sorted(players, key=lambda x: pl_res[x]['total'], reverse=True)
        dupes = {week_names_map.get(u, {}).get('nick'): u for u in players if [week_names_map.get(x, {}).get('nick') for x in players].count(week_names_map.get(u, {}).get('nick')) > 1}
        nav = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==w_key else ""}">{weeks[wk]["label"]}</a>' for wk in all_ws])
        target_r = current_rating if w_key == all_ws[-1] else (next((r['rating'] for r in reversed(clan_stats) if r['rating']), 0))
        
        c_cells = []
        for i, s in enumerate(clan_stats):
            if s["rating"]:
                f_val = f"+{fmt(s['fact'])}" if s['fact'] >= 0 else f"-{fmt(-s['fact'])}"
                c_cells.append(f'<td style="text-align:center"><div class="fact-grow">{f_val}</div><div class="burned">🔥 -{fmt(s["burned"])}</div></td>')
            else:
                lbl = "-" if i <= today_idx else ""
                c_cells.append(f'<td style="text-align:center; color:#30363d">{lbl}</td>')
        s_cells = [f'<td style="text-align:center"><span class="day-growth">+{fmt(cg)}</span></td>' for i, cg in enumerate(clan_growths)]

        html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>ОРДА | {week['label']}</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    :root {{ --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --error: #f85149; --border: #30363d; --text: #c9d1d9; }}
    body {{ background: #0d1117; color: var(--text); font-family: 'Inter', sans-serif; margin: 25px; font-size: 16px; overflow-x: hidden; }}
    header {{ text-align: center; margin-bottom: 30px; }}
    h1 {{ font-family: 'Orbitron'; font-size: 3rem; color: #fff; margin: 0; letter-spacing: 12px; }}
    .subtitle {{ color: var(--gold); letter-spacing: 6px; font-size: 0.9rem; text-transform: uppercase; font-weight: 500; }}
    .update-time {{ font-size: 0.65rem; color: #30363d; text-align: center; margin-bottom: 10px; font-family: 'Roboto Mono'; letter-spacing: 1px; text-transform: uppercase; }}
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
<h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE v{VERSION_NUM}</div></header>
<nav>{nav}</nav>
<div class="update-time">Данные обновлены: {update_str}</div>
<div class="table-container"><table>
    <thead><tr><th style="width:30px">№</th><th>Участник</th><th>Звание</th><th style="text-align:center">Всего</th>
    {" ".join([f'<th>{(week["monday"]+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
    <tbody>
    <tr class="clan-row"><td style="text-align:center; color:#58a6ff">--</td><td colspan="2">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td>
    <td style="text-align:center"><span class="main-score" style="color:#fff">{fmt(target_r)}</span></td>
    {" ".join(c_cells)}</tr>
    <tr class="clan-row" style="background:#0d1117; height: 45px;"><td style="text-align:center; color:var(--green)">--</td><td colspan="2" style="color:var(--green); font-size: 0.8rem;">СУММАРНЫЙ ЗАРАБОТОК</td>
    <td style="text-align:center"><span class="main-score" style="color:var(--green); font-size: 0.95rem;">{fmt(sum(clan_growths))}</span></td>
    {" ".join(s_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = week_names_map.get(uid, {}); p_res = pl_res[uid]
            first, last = p_res['first_p'], p_res['last_p']
            nick_sec = f"<div class='nick-cell'><span class='nick'>{p.get('nick','ID:'+uid)}</span>"
            if p.get('nick') in dupes: nick_sec += f"<span class='trait'>({p.get('traits','') if p.get('traits','') else 'Без особых примет'})</span>"
            nick_sec += "</div>"
            html += f"<tr><td style='text-align:center; color:#484f58; font-family:\"Roboto Mono\"; font-size: 0.7rem;'>{count}</td><td>{nick_sec}</td><td><span class='role'>{p.get('role','Soldier')}</span></td>"
            html += f"<td style='text-align:center'><span class='main-score'>{fmt(p_res['total'])}</span></td>"
            for i, g in enumerate(p_res['growths']):
                if is_current_week and i > today_idx: # Future (only hide in current week)
                    html += '<td style="text-align:center; color:#30363d">-</td>'
                elif g > 0:
                    html += f"<td style='text-align:center'><span class='day-growth'>+{fmt(g)}</span></td>"
                elif i < first: # Hasn't joined yet
                    html += '<td style="text-align:center; color:#8b949e">-</td>'
                elif i > last: # Left early (not in the last snapshot of the day or current hier)
                    html += '<td style="text-align:center"><span class="absent" title="Покинул клан">X</span></td>'
                else:
                    html += '<td style="text-align:center; color:#484f58; font-size: 0.85rem;">0</td>'
            html += "</tr>"
        html += "</tbody></table></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{w_key}.html"), 'w', encoding='utf-8') as f: f.write(html)
    with open(MAIN_REPORT, 'w', encoding='utf-8') as f:
        f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{all_ws[-1]}.html"></head></html>')

if __name__ == "__main__":
    # Принудительно ставим UTF-8 для вывода в Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), 'replace')
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach(), 'replace')

    print(f"--- Starting Clan Accountant v{VERSION_NUM} ---")
    print(f"[*] Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("[*] Проверка активности пользователя...")
    if is_user_active():
        print("[!] ВНИМАНИЕ: Обнаружена активная игровая сессия. Чтобы избежать конфликта, бот завершает работу.")
        sys.exit(0)

    print("[*] Попытка получения данных от API сервера...")
    h, u, r = fetch_data()
    
    if h: 
        print(f"[*] Данные успешно получены. Рейтинг клана: {fmt(r)}")
        print(f"[*] Найдено участников: {len(u)}")
        print(f"[*] Генерация HTML-отчета...")
        generate_web_report(h, u, r, last_update_time=datetime.now())
        print("[*] ОТЧЕТ УСПЕШНО ОБНОВЛЕН.")
    else:
        print("[!] КРИТИЧЕСКАЯ ОШИБКА: Не удалось получить данные от сервера.")
        print("[!] Возможные причины: просрочен AUTH_KEY, изменилась версия игры или нет связи с сервером.")
        sys.exit(1)
