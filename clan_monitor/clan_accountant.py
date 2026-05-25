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
# CLAN ACCOUNTANT v0.3.5 (2026-05-25)
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
    if is_user_active() and not force_run:
        msg = "[!] ОБНАРУЖЕНО АКТИВНОЕ СОЕДИНЕНИЕ. Обновление пропущено."
        print(msg)
        with open(os.path.join(REPO_ROOT, 'logs', 'accountant.log'), 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S,%f')[:-4]}] {msg}\n")
        return None, None, None

    try:
        def perform_refresh(sid, clan_version, last_cmd_id):
            now = datetime.now().strftime('%d/%m/%Y_%H:%M:%S.%f')[:-2]
            cmd_body = {"data": {"userId": USER_ID, "sessionID": sid, "commands": [{"commandNumber": last_cmd_id + 1, "hash": random.randint(-2147483648, 2147483647), "id": "UseServiceCommand", "paramsStr": json.dumps({"serviceData": {"ServiceType": "RefreshArenaLeaderboards", "Data": ""}}), "time": now}], "clanVersion": clan_version}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 3, "version": VERSION}
            return requests.post(f"{BASE_URL}/commands?userid={USER_ID}", json=cmd_body, headers={"Content-Type": "application/octet-stream"}, timeout=10).json()

        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r1 = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if debug_mode: print(f"[DEBUG] INIT 1 complete. LastCmd={r1.get('data',{}).get('userState',{}).get('lastCommandId')}")
        
        try:
            refresh_resp = perform_refresh(r1['data']['sessionID'], r1['data']['clanData']['clanState']['version'], r1['data']['userState']['lastCommandId'])
            if debug_mode: print(f"[DEBUG] REFRESH status: {refresh_resp.get('data', {}).get('data', [{}])[0].get('error', 'SUCCESS')}")
        except: pass

        time.sleep(5)
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if debug_mode: 
            arena = r.get('data',{}).get('userState',{}).get('arena',{})
            print(f"[DEBUG] INIT 2 complete. ArenaTime={arena.get('leaderboards',{}).get('lastUpdateTime')}")
        
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
        json.dump({"pts": {str(k): v for k, v in {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points']), **{str(s['member']['userId']): int(s['member']['points']) for s in hier['slots']}}.items()}, "clanRating": current_rating}, f)

    snf = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_')])
    sd = []
    for fs in snf:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if m:
            dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
            try:
                with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sd.append({"time": dt, "pts": {str(k): int(v) for k,v in data.get("pts", {}).items()}, "rating": data.get("clanRating")})
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
        
        pl_res = {}
        for uid in players:
            daily_growths = [0] * 7
            presence = [False] * 7
            
            # База на начало недели. Для каждой недели начинаем с 0,
            # но для корректного переноса между днями используем prev_day_end.
            prev_day_end = 0 
            
            # Для первой недели в истории или если нет данных за прошлую, база 0.
            # Если есть снимки до начала этой недели, берем последний из них.
            pre_week_sn = [e for e in sd if e['time'] < monday]
            if pre_week_sn:
                prev_day_end = pre_week_sn[-1]['pts'].get(str(uid), 0)

            for i in range(7):
                d_start = monday + timedelta(days=i)
                d_end = d_start + timedelta(days=1)
                day_snaps = sorted([s for s in sd if d_start <= s['time'] < d_end and str(uid) in s['pts']], key=lambda x: x['time'])
                
                if day_snaps:
                    vals = [s['pts'][str(uid)] for s in day_snaps]
                    peak = max(vals)
                    end_val = vals[-1]
                    
                    # Проверяем, есть ли игрок в manual_adjustments (наш особый алгоритм сброса)
                    use_reset_logic = False
                    for d_adj in adj_db:
                        if str(uid) in adj_db[d_adj]:
                            use_reset_logic = True
                            break

                    if use_reset_logic and end_val < peak:
                        growth = (peak - prev_day_end) + end_val
                    else:
                        growth = end_val - prev_day_end
                    
                    daily_growths[i] = max(0, int(growth))
                    prev_day_end = end_val
                else:
                    daily_growths[i] = 0
                
                d_str = d_start.strftime("%Y-%m-%d")
                ex = adj_db.get(d_str, {}).get(str(uid), [])
                presence[i] = (any(str(uid) in s['pts'] for s in week["days"].get(d_str, [])) if d_str in week["days"] else False) or bool(ex)

            pl_res[uid] = {"growths": daily_growths, "total": sum(daily_growths), "presence": presence, "first_p": next((idx for idx, p in enumerate(presence) if p), 999), "last_p": next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)}

        clan_growths = [sum(p["growths"][i] for p in pl_res.values()) for i in range(7)]
        clan_rats = [None] * 7
        for i in range(7):
            ds = [s for s in sd if (monday+timedelta(days=i)) <= s['time'] < (monday+timedelta(days=i+1)) and s.get('rating') is not None]    
            if ds: clan_rats[i] = ds[-1]['rating']
        
        pre_week_sn = [e for e in sd if e['time'] < monday]
        prev_r = pre_week_sn[-1]['rating'] if pre_week_sn else 11199931
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
    .summary-row {{ background: rgba(88, 166, 255, 0.1); }}
    .summary-row td {{ padding: 25px 20px; color: var(--accent); font-weight: 700; border-bottom: 3px solid var(--accent); }}
    .clan-score {{ font-size: 1.4rem; font-family: 'Roboto Mono'; display: block; }}
    th {{ background: #0b0e14; padding: 12px; color: #8b949e; font-size: 0.65rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
    td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); border-right: 1px solid rgba(48, 54, 61, 0.3); }}
    .nick {{ color: #fff; font-weight: 700; font-size: 0.9rem; }}
    .role {{ font-size: 0.58rem; color: #8b949e; border: 1px solid var(--border); padding: 1px 3px; border-radius: 3px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 0.9rem; color: var(--green); font-weight: 700; }}
    .absent {{ color: var(--error); font-weight: 900; font-size: 1.1rem; font-family: 'Orbitron'; text-align: center; display: block; }}
    .no-growth {{ color: #484f58; opacity: 0.4; font-family: 'Roboto Mono'; text-align: center; }}
</style></head><body><div class="container"><header><h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE</div></header>
<nav>{nav}</nav><div class="table-container"><div class="update-time">ДАННЫЕ ОТ: {last_data_ts} (MSK)</div><table>
<thead><tr><th style="width:30px">№</th><th style="text-align:left">Участник</th><th style="text-align:left">Звание</th><th style="text-align:center">Всего</th>{" ".join([f'<th>{(monday+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
<tbody>
<tr class="summary-row"><td>--</td><td colspan="2" style="text-align:left"><span style="text-transform:uppercase; letter-spacing:3px;">Итоги недели</span></td><td style="text-align:center"><span class="clan-score">{fmt(sum(clan_growths))}</span></td>{" ".join([f'<td style="text-align:center"><span class="day-growth">+{fmt(cg)}</span></td>' for cg in clan_growths])}</tr>
<tr class="summary-row" style="background:#0d1117"><td>--</td><td colspan="2" style="text-align:left">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td><td style="text-align:center"><span class="clan-score" style="color:#fff">{fmt(tr)}</span></td>{" ".join(c_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = names_map.get(uid, {"nick": f"ID:{uid}", "role": "Soldier"}); p_res = pl_res[uid]; nick_sec = f"<span class='nick'>{p['nick']}</span>"
            html += f"<tr><td>{count}</td><td style='text-align:left'>{nick_sec}</td><td style='text-align:left'><span class='role'>{p['role']}</span></td><td style='text-align:center'><span class='main-score'>{fmt(p_res['total'])}</span></td>"
            for i, g in enumerate(p_res['growths']):
                if is_current_week and i > today_idx: html += "<td style='text-align:center; color:#30363d'>-</td>"
                elif g > 0: html += f"<td><span class='day-growth'>+{fmt(g)}</span></td>"
                elif i < p_res['first_p']: html += "<td style='text-align:center; color:#8b949e'>-</td>"
                elif i > p_res['last_p']: html += "<td style='text-align:center'><span class='absent'>X</span></td>"
                else: html += "<td class='no-growth'>0</td>"
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
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dump", help="Path to a specific JSON dump to process")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    h, u, r = fetch_data(explicit_dump=args.dump, force_run=args.force, debug_mode=args.debug)
    if h: generate_web_report(h, u, r); print("[*] УСПЕХ")
    else: sys.exit(1)
