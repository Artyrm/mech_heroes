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
    print(f"CRITICAL: {CONFIG_FILE} not found!")
    sys.exit(1)

USER_ID = CONF['USER_ID']
AUTH_KEY = CONF['AUTH_KEY']
VERSION = CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

# PATHS
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

def fetch_data():
    try:
        p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
        r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1, headers=HEADERS).json()
        if "error" in r: return None, None
        d = r.get("data", {})
        sid = d.get("sessionID")
        hier = d.get("clanData", {}).get("clanState", {}).get("hierarchy")
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots']}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
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
    
    # DB Update
    names_map = load_json(MEMBERS_DB)
    for u in users: names_map[str(u['userId'])] = {"nick": u['nickname'], "role": "Soldier"}
    
    curr_pts = {str(hier['leader']['member']['userId']): int(hier['leader']['member']['points'])}
    names_map[str(hier['leader']['member']['userId'])]["role"] = "LEADER"
    for s in hier['slots']: 
        uid = str(s['member']['userId'])
        curr_pts[uid] = int(s['member']['points'])
        if uid in names_map: names_map[uid]["role"] = s['role']
    with open(MEMBERS_DB, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    
    # Save snapshot
    with open(os.path.join(SNAPSHOTS_DIR, f"points_utc_{now_utc.strftime('%Y-%m-%d_%H-%M')}.json"), 'w', encoding='utf-8') as f:
        json.dump(curr_pts, f)

    def get_monday(dt): return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    
    all_snaps = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_') and fs.endswith('.json')])
    raw_history = []
    for fs in all_snaps:
        match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fs)
        if not match: continue
        dt = datetime.strptime(f"{match.group(1)}_{match.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as jf:
            data = json.load(jf)
            if len(data) > 5: raw_history.append({"time": dt, "pts": {k: int(v) for k,v in data.items() if k.isdigit()}})

    adj_db = load_json(ADJUSTMENTS_FILE)

    weeks = {}
    for entry in raw_history:
        monday = get_monday(entry['time'])
        wkey = monday.strftime("%Y_W%W")
        if wkey not in weeks:
            sun = monday + timedelta(days=6)
            weeks[wkey] = {"monday": monday, "label": f"{monday.strftime('%d.%m')} - {sun.strftime('%d.%m')}", "daily": {}}
        dkey = entry['time'].strftime("%Y-%m-%d")
        if dkey not in weeks[wkey]["daily"]: weeks[wkey]["daily"][dkey] = []
        weeks[wkey]["daily"][dkey].append(entry)

    all_week_keys = sorted(weeks.keys())
    for cur_wk in all_week_keys:
        week = weeks[cur_wk]
        players = set()
        for d in week["daily"].values():
            for e in d: players.update(e['pts'].keys())
        
        player_results = {}
        for uid in players:
            daily_growths = []
            total_acc = 0
            last_p_seq = 0 
            
            mon = week["monday"]
            for i in range(7):
                d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
                d_growth = 0
                snaps = week["daily"].get(d_str, [])
                
                for s in snaps:
                    curr = s['pts'].get(uid, 0)
                    if curr > last_p_seq:
                        d_growth += (curr - last_p_seq)
                        last_p_seq = curr
                    elif curr < last_p_seq and curr > 0:
                        d_growth += curr
                        last_p_seq = curr
                
                m_adj = adj_db.get(d_str, {}).get(uid)
                if m_adj and m_adj > d_growth: d_growth = m_adj
                
                daily_growths.append(d_growth)
                total_acc += d_growth

            player_results[uid] = {"growths": daily_growths, "total": total_acc}

        clan_growths = [sum(p["growths"][i] for p in player_results.values()) for i in range(7)]
        sorted_ids = sorted(players, key=lambda x: player_results[x]['total'], reverse=True)

        nav_html = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==cur_wk else ""}">{weeks[wk]["label"]}</a>' for wk in all_week_keys])

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
    .summary-row td:first-child {{ border-top-left-radius: 23px; }}
    .summary-row td:last-child {{ border-top-right-radius: 23px; }}
    tr:last-child td:first-child {{ border-bottom-left-radius: 23px; }}
    tr:last-child td:last-child {{ border-bottom-right-radius: 23px; }}
    tr:last-child td {{ border-bottom: none; }}
    .summary-row {{ background: rgba(88, 166, 255, 0.1); }}
    .summary-row td {{ padding: 30px 20px; color: var(--accent); font-weight: 700; border-bottom: 3px solid var(--accent); }}
    .clan-score {{ font-size: 1.6rem; font-family: 'Roboto Mono'; display: block; }}
    th {{ background: #0b0e14; padding: 20px; color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; text-align: center; border-bottom: 1px solid var(--border); }}
    td {{ padding: 18px 20px; border-bottom: 1px solid var(--border); }}
    .num-col {{ color: #484f58; font-family: 'Roboto Mono'; width: 40px; font-size: 0.9rem; }}
    .nick {{ color: #fff; font-weight: 700; font-size: 1.1rem; }}
    .role {{ font-size: 0.72rem; color: #8b949e; border: 1px solid var(--border); padding: 3px 8px; border-radius: 4px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1.3rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 1rem; color: var(--green); font-weight: 700; text-align: center; display: block; }}
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
            p = names_map.get(uid, {"nick": f"ID:{uid}", "role": "Soldier"})
            res = player_results[uid]
            html += f"<tr><td class='num-col'>{count}</td>"
            html += f"<td class='t-left'><span class='nick'>{p['nick']}</span></td><td class='t-left'><span class='role'>{p['role']}</span></td>"
            html += f"<td class='t-center'><span class='main-score'>{res['total']:,}</span></td>"
            for g in res['growths']:
                if g > 0: html += f"<td class='t-center'><span class='day-growth'>+{g:,}</span></td>"
                else: html += "<td class='t-center no-growth'>0</td>"
            html += "</tr>"
        html += "</tbody></table></div></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{cur_wk}.html"), 'w', encoding='utf-8') as f: f.write(html)

    with open(MAIN_REPORT, 'w', encoding='utf-8') as f:
        latest_wk = sorted(weeks.keys())[-1]
        f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{latest_wk}.html"></head></html>')
    if AUTO_PUSH: run_git_push()

if __name__ == "__main__":
    h, u = fetch_data()
    if h: generate_web_report(h, u)
