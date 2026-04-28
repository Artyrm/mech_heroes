import requests
import json
import os
import sys
import subprocess
import re
from datetime import datetime, timedelta, timezone

# ==============================================================================
# IDENTITY & CONFIG
# ==============================================================================
CONFIG_FILE = 'config.json'
ADJUSTMENTS_FILE = 'manual_adjustments.json'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

CONF = load_json(CONFIG_FILE)
if not CONF:
    print("CRITICAL: config.json not found!")
    sys.exit(1)

USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

SNAPSHOTS_DIR = 'snapshots'
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_ROOT = os.path.join(REPO_ROOT, 'clan', 'ORDA')
REPORTS_DIR = os.path.join(OUTPUT_ROOT, 'reports')
MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'index.html')
MEMBERS_DB = 'members_name_db.json'
AUTO_PUSH = True 

for d in [SNAPSHOTS_DIR, REPORTS_DIR]:
    if not os.path.exists(d): os.makedirs(d)

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://app-476209.games.s3.yandex.net",
    "Referer": "https://app-476209.games.s3.yandex.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# ACCESSORY MAPPING
ACC_MAP = {
    "cap_black": "Черная кепка",
    "cap_red": "Красная кепка",
    "glasses_2": "Очки",
    "glasses_1": "Черные очки",
    "helper": "Спецовка",
    "bristle_blond": "Светлая щетина",
    "hair_brown": "Шатен",
    "hair_blond": "Блондин",
    "bald": "Лысый",
    "goatee_blond": "Светлая эспаньолка",
    "mask_1": "Маска",
    "short_hair_brown": "Короткий шатен",
    "none": ""
}

def translate_acc(val):
    if not val or val == "none": return ""
    return ACC_MAP.get(val, val.replace("_", " ").title())

def fetch_data():
    try:
        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if "error" in r: return None, None
        d = r.get("data", {})
        sid = d.get("sessionID")
        hier = d.get("clanData", {}).get("clanState", {}).get("hierarchy")
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots']}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        users = json.loads(r2["data"]["response"]).get("Users", [])
        return hier, users
    except: return None, None

def run_git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Report updated {datetime.now().strftime('%d.%m %H:%M')}"], cwd=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True, capture_output=True)
    except: pass

def generate_web_report(hier, users):
    now_utc = datetime.now(timezone.utc)
    names_map = load_json(MEMBERS_DB)
    
    for u in users:
        acc = u.get("avatarConfiguration", {})
        traits = filter(None, [translate_acc(acc.get('top')), translate_acc(acc.get('front')), translate_acc(acc.get('down'))])
        names_map[str(u['userId'])] = {
            "nick": u['nickname'], 
            "role": "Soldier",
            "traits": ", ".join(traits)
        }
    
    l_id = str(hier['leader']['member']['userId'])
    if l_id in names_map: names_map[l_id]["role"] = "LEADER"
    for s in hier['slots']: 
        uid = str(s['member']['userId'])
        if uid in names_map: names_map[uid]["role"] = s['role']

    with open(MEMBERS_DB, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    
    curr_pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
    for s in hier['slots']: curr_pts[str(s['member']['userId'])] = int(s['member']['points'])
    with open(os.path.join(SNAPSHOTS_DIR, f"points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"), 'w', encoding='utf-8') as f:
        json.dump(curr_pts, f)

    def get_monday(dt): return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    all_snaps = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_') and fs.endswith('.json')])
    snaps_data = []
    for fs in all_snaps:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if not m: continue
        dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as f:
            d = json.load(f)
            if len(d) > 5: snaps_data.append({"time": dt, "pts": {k: int(v) for k,v in d.items() if k.isdigit()}})

    adj_db = load_json(ADJUSTMENTS_FILE)
    weeks = {}
    for e in snaps_data:
        m_dt = get_monday(e['time'])
        wk = m_dt.strftime("%Y_W%W")
        if wk not in weeks:
            weeks[wk] = {"monday": m_dt, "label": f"{m_dt.strftime('%d.%m')} - {(m_dt+timedelta(days=6)).strftime('%d.%m')}", "days": {}}
        dk = e['time'].strftime("%Y-%m-%d")
        if dk not in weeks[wk]["days"]: weeks[wk]["days"][dk] = []
        weeks[wk]["days"][dk].append(e)

    for w_key in sorted(weeks.keys()):
        week = weeks[w_key]
        players = set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        
        pl_results = {}
        for uid in players:
            growths, total_acc, last_ref = [], 0, 0
            for i in range(7):
                d_str = (week["monday"] + timedelta(days=i)).strftime("%Y-%m-%d")
                d_snaps = week["days"].get(d_str, [])
                exits = adj_db.get(d_str, {}).get(uid, [])
                if not isinstance(exits, list): exits = [exits]
                day_growth, reference = 0, last_ref
                for ev in exits:
                    day_growth += max(0, ev - reference)
                    reference = 0
                if d_snaps:
                    final = d_snaps[-1]['pts'].get(uid, 0)
                    day_growth += (final if final < reference and not exits else max(0, final - reference))
                    last_ref = final
                growths.append(day_growth)
                total_acc += day_growth
            pl_results[uid] = {"growths": growths, "total": total_acc}

        clan_growths = [sum(p["growths"][ev] for p in pl_results.values()) for ev in range(7)]
        sorted_ids = sorted(players, key=lambda x: pl_results[x]['total'], reverse=True)
        nav_html = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==w_key else ""}">{weeks[wk]["label"]}</a>' for wk in sorted(weeks.keys())])

        html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>ОРДА | {week['label']}</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    :root {{ --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --border: #30363d; --text: #c9d1d9; }}
    body {{ background: #0d1117; color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 40px; font-size: 16px; overflow-y: scroll; }}
    .container {{ max-width: 1500px; margin: 0 auto; }}
    header {{ text-align: center; margin-bottom: 50px; }}
    h1 {{ font-family: 'Orbitron'; font-size: 4rem; color: #fff; margin: 0; letter-spacing: 12px; }}
    .subtitle {{ color: var(--gold); letter-spacing: 6px; font-size: 1.1rem; text-transform: uppercase; font-weight: 500; }}
    nav {{ display: flex; gap: 15px; justify-content: center; margin-bottom: 40px; flex-wrap: wrap; }}
    nav a {{ text-decoration: none; color: #8b949e; padding: 12px 24px; border-radius: 10px; background: var(--card); border: 2px solid var(--border); transition: 0.3s; }}
    nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .table-container {{ background: var(--card); border-radius: 24px; border: 1px solid var(--border); margin-bottom: 50px; overflow: hidden; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
    .summary-row td {{ padding: 30px 20px; color: var(--accent); font-weight: 700; border-bottom: 3px solid var(--accent); }}
    th {{ background: #0b0e14; padding: 20px; color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; text-align: center; border-bottom: 1px solid var(--border); }}
    td {{ padding: 18px 20px; border-bottom: 1px solid var(--border); border-right: 1px solid rgba(48, 54, 61, 0.5); }}
    td:last-child {{ border-right: none; }}
    .num-col {{ color: #484f58; font-family: 'Roboto Mono'; width: 40px; font-size: 0.9rem; }}
    .nick-cell {{ display: flex; flex-direction: column; gap: 4px; }}
    .nick {{ color: #fff; font-weight: 700; font-size: 1.1rem; }}
    .trait {{ color: var(--gold); font-size: 0.75rem; font-weight: 500; opacity: 0.9; font-style: italic; }}
    .role {{ font-size: 0.72rem; color: #8b949e; border: 1px solid var(--border); padding: 2px 6px; border-radius: 4px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1.3rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 1.1rem; color: var(--green); font-weight: 700; text-align: center; display: block; }}
    .no-growth {{ color: #484f58; opacity: 0.4; font-family: 'Roboto Mono'; text-align: center; }}
    .t-center {{ text-align: center; }}
    .t-left {{ text-align: left; }}
</style></head><body><div class="container"><header><h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE</div></header>
<nav>{nav_html}</nav>
<div class="table-container"><table>
    <tr class="summary-row">
        <td class="num-col">--</td>
        <td colspan="2" class="t-left"><span style="text-transform:uppercase; letter-spacing:3px;">Итоги недели</span></td>
        <td class="t-center"><span class="clan-score">{sum(clan_growths):,}</span></td>
        {" ".join([f'<td class="t-center"><span class="day-growth">+{cg:,}</span></td>' for cg in clan_growths])}
    </tr>
    <thead>
        <tr>
            <th class="num-col">№</th>
            <th class="t-left">Участник</th>
            <th class="t-left">Звание</th>
            <th class="t-center">Рейтинг</th>
            {" ".join([f'<th>{(week["monday"]+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}
        </tr>
    </thead>
    <tbody>"""
        for count, uid in enumerate(sorted_ids, 1):
            p_data = names_map.get(uid, {})
            p_nick = p_data.get('nick', f"ID:{uid}")
            p_traits = p_data.get('traits', '')
            p_role = p_data.get('role', 'Soldier')
            
            res = pl_results[uid]
            nick_sec = f"<div class='nick-cell'><span class='nick'>{p_nick}</span>"
            if p_traits: nick_sec += f"<span class='trait'>{p_traits}</span>"
            nick_sec += "</div>"
            
            html += f"<tr><td class='num-col'>{count}</td>"
            html += f"<td class='t-left'>{nick_sec}</td><td class='t-left'><span class='role'>{p_role}</span></td>"
            html += f"<td class='t-center'><span class='main-score'>{res['total']:,}</span></td>"
            for g in res['growths']:
                if g > 0: html += f"<td class='t-center'><span class='day-growth'>+{g:,}</span></td>"
                else: html += "<td class='t-center no-growth'>0</td>"
            html += "</tr>"
        html += "</tbody></table></div></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{w_key}.html"), 'w', encoding='utf-8') as f: f.write(html)

    with open(MAIN_REPORT, 'w', encoding='utf-8') as f:
        latest_wk = sorted(weeks.keys())[-1]
        f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{latest_wk}.html"></head></html>')
    if AUTO_PUSH: run_git_push()

if __name__ == "__main__":
    h, u = fetch_data()
    if h: generate_web_report(h, u)
