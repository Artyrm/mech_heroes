import requests
import json
import os
import sys
import subprocess
import re
from datetime import datetime, timedelta, timezone
from deep_translator import GoogleTranslator

# ==============================================================================
# IDENTITY & CONFIG
# ==============================================================================
CONFIG_FILE = 'config.json'
ADJUSTMENTS_FILE = 'manual_adjustments.json'
TRANS_CACHE_FILE = 'translations_cache.json'
VERSION_NUM = "0.2.2"

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
    try:
        manual_fix = full_str.replace("Blond", "Blonde").replace("blond", "blonde").replace("Goatee", "Beard")
        translated = GoogleTranslator(source='en', target='ru').translate(manual_fix)
        translated = translated.replace("блондинка", "блонд").replace("Блондинка", "Блонд").replace("эспаньолка", "бородка")
        TRANS_CACHE[full_str] = translated
        with open(TRANS_CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(TRANS_CACHE, f, ensure_ascii=False)
        return translated
    except: return full_str

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
        if "error" in r: return None, None, None
        d = r.get("data", {})
        sid, hier = d.get("sessionID"), d.get("clanData", {}).get("clanState", {}).get("hierarchy")
        rating = int(d.get("clanData", {}).get("clanState", {}).get("rating", 0))
        ids = {hier['leader']['member']['userId']} | {s['member']['userId'] for s in hier['slots']}
        p2 = {"data": {"userId": USER_ID, "sessionID": sid, "type": "GetUsersRawInfos", "request": json.dumps({"users": list(ids)})}, "platform": "YandexGamesDesktop", "requestId": 2, "version": VERSION}
        r2 = requests.post(f"{BASE_URL}/directcommand?userid={USER_ID}", json=p2, headers=HEADERS).json()
        return hier, json.loads(r2["data"]["response"]).get("Users", []), rating
    except: return None, None, None

def run_git_push():
    try:
        subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True, capture_output=True); subprocess.run(["git", "commit", "-m", f"Report updated {datetime.now().strftime('%d.%m %H:%M')}"], cwd=REPO_ROOT, check=True, capture_output=True); subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True, capture_output=True)
    except: pass

def generate_web_report(hier, users, current_rating):
    now_utc, names_map = datetime.now(timezone.utc), load_json(MEMBERS_DB)
    # MOSCOW TIME FOR WEEKDAY
    now_mskq = now_utc.astimezone(timezone(timedelta(hours=3)))
    today_idx = now_mskq.weekday() # 0-Mon, 1-Tue...
    
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
        uid = str(s['member']['userId']); names_map[uid]["role"] = s['role']
    with open(MEMBERS_DB, 'w', encoding='utf-8') as f: json.dump(names_map, f, ensure_ascii=False, indent=2)
    
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
                    sd.append({"time": dt, "pts": {k: int(v) for k,v in pts_m.items() if k.isdigit()}, "rating": d.get("clanRating")})
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
        week, players = weeks[w_key], set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        pl_res, clan_rats = {}, [None] * 7
        for uid in players:
            growths, total_acc, last_ref, pres = [], 0, 0, []
            for i in range(7):
                d_str = (week["monday"] + timedelta(days=i)).strftime("%Y-%m-%d")
                sn, ex = week["days"].get(d_str, []), adj_db.get(d_str, {}).get(uid, [])
                if not isinstance(ex, list): ex = [ex]
                is_present = any(uid in s['pts'] for s in sn) or bool(ex)
                pres.append(is_present)
                day_growth, reference = 0, last_ref
                for ev in ex: day_growth += max(0, ev - reference); reference = 0
                if sn:
                    final = sn[-1]['pts'].get(uid, 0)
                    day_growth += (final if final < reference and not ex else max(0, final - reference)); last_ref = final
                    if sn[-1].get('rating'): clan_rats[i] = sn[-1]['rating']
                growths.append(day_growth); total_acc += day_growth
            
            try: first_p = pres.index(True)
            except: first_p = 999
            try: last_p = 6 - pres[::-1].index(True)
            except: last_p = -1
            pl_res[uid] = {"growths": growths, "total": total_acc, "presence": pres, "first_p": first_p, "last_p": last_p}

        clan_growths = [sum(p["growths"][ev] for p in pl_res.values()) for ev in range(7)]
        clan_stats, prev_r = [], 11199931
        for i in range(7):
            curr_r = clan_rats[i]
            if curr_r and prev_r:
                f_ch = curr_r - prev_r; brn = max(0, clan_growths[i] - f_ch)
                clan_stats.append({"rating": curr_r, "fact": f_ch, "burned": brn}); prev_r = curr_r
            else:
                clan_stats.append({"rating": curr_r or 0, "fact": 0, "burned": 0})
                if curr_r: prev_r = curr_r

        sorted_ids = sorted(players, key=lambda x: pl_res[x]['total'], reverse=True)
        dupes = {names_map.get(u, {}).get('nick'): u for u in players if [names_map.get(x, {}).get('nick') for x in players].count(names_map.get(u, {}).get('nick')) > 1}
        nav = " ".join([f'<a href="report_{wk}.html" class="{"active" if wk==w_key else ""}">{weeks[wk]["label"]}</a>' for wk in all_ws])
        target_r = current_rating if w_key == all_ws[-1] else (next((r['rating'] for r in reversed(clan_stats) if r['rating']), 0))
        
        c_cells = []
        for i, s in enumerate(clan_stats):
            if s["rating"]:
                f_val = f"+{s['fact']:,}" if s['fact'] >= 0 else f"{s['fact']:,}"
                c_cells.append(f'<td style="text-align:center"><div class="fact-grow">{f_val}</div><div class="burned">🔥 -{s["burned"]:,}</div></td>')
            else:
                lbl = "-" if i <= today_idx else ""
                c_cells.append(f'<td style="text-align:center; color:#30363d">{lbl}</td>')

        s_cells = []
        for i, cg in enumerate(clan_growths):
            if i <= today_idx: s_cells.append(f'<td style="text-align:center"><span class="day-growth">+{cg:,}</span></td>')
            else: s_cells.append('<td style="text-align:center">-</td>')

        html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>ОРДА | {week['label']}</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    :root {{ --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --error: #f85149; --border: #30363d; --text: #c9d1d9; }}
    body {{ background: #0d1117; color: var(--text); font-family: 'Inter', sans-serif; margin: 30px; font-size: 16px; }}
    header {{ text-align: center; margin-bottom: 40px; }}
    h1 {{ font-family: 'Orbitron'; font-size: 3.5rem; color: #fff; margin: 0; letter-spacing: 12px; }}
    .subtitle {{ color: var(--gold); letter-spacing: 6px; font-size: 1rem; text-transform: uppercase; font-weight: 500; }}
    nav {{ display: flex; gap: 12px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap; }}
    nav a {{ text-decoration: none; color: #8b949e; padding: 10px 20px; border-radius: 8px; background: var(--card); border: 1px solid var(--border); }}
    nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .table-container {{ background: var(--card); border-radius: 20px; border: 1px solid var(--border); overflow: hidden; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; }}
    th {{ background: #0b0e14; padding: 15px; color: #8b949e; font-size: 0.7rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
    .clan-row {{ background: #1c2128; font-weight: 700; }}
    .clan-row td {{ border-bottom: 2px solid var(--border); padding: 12px; }}
    .burned {{ color: var(--error); font-size: 0.75rem; font-family: 'Roboto Mono'; opacity: 0.8; margin-top: 3px; }}
    .fact-grow {{ color: var(--accent); font-size: 0.95rem; font-family: 'Roboto Mono'; }}
    td {{ padding: 12px 14px; border-bottom: 1px solid var(--border); border-right: 1px solid rgba(48, 54, 61, 0.3); }}
    .nick {{ color: #fff; font-weight: 700; font-size: 0.95rem; }}
    .trait {{ color: var(--gold); font-size: 0.7rem; font-weight: 500; font-style: italic; opacity: 0.7; }}
    .role {{ font-size: 0.6rem; color: #8b949e; border: 1px solid var(--border); padding: 1px 4px; border-radius: 3px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1.1rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 0.95rem; color: var(--green); font-weight: 700; }}
    .absent {{ color: var(--error); font-weight: 900; font-size: 1.2rem; font-family: 'Orbitron'; }}
</style></head><body><div class="container"><header><h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE v{VERSION_NUM}</div></header>
<nav>{nav}</nav><div class="table-container"><table>
    <thead><tr><th style="width:30px">№</th><th>Участник</th><th>Звание</th><th style="text-align:center">Всего</th>
    {" ".join([f'<th>{(week["monday"]+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
    <tbody>
    <tr class="clan-row"><td style="text-align:center; color:#58a6ff">--</td><td colspan="2">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td>
    <td style="text-align:center"><span class="main-score" style="color:#fff">{target_r:,}</span></td>
    {" ".join(c_cells)}</tr>
    <tr class="clan-row" style="background:#0d1117; height: 50px;"><td style="text-align:center; color:var(--green)">--</td><td colspan="2" style="color:var(--green); font-size: 0.85rem;">СУММАРНЫЙ ЗАРАБОТОК</td>
    <td style="text-align:center"><span class="main-score" style="color:var(--green); font-size: 1rem;">{sum(clan_growths):,}</span></td>
    {" ".join(s_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = names_map.get(uid, {}); p_res = pl_res[uid]
            first, last = p_res['first_p'], p_res['last_p']
            nick_sec = f"<div class='nick-cell'><span class='nick'>{p.get('nick','ID:'+uid)}</span>"
            if p.get('nick') in dupes: nick_sec += f"<span class='trait'>({p.get('traits','') if p.get('traits','') else 'Без особых примет'})</span>"
            nick_sec += "</div>"
            html += f"<tr><td style='text-align:center; color:#484f58; font-family:\"Roboto Mono\"; font-size: 0.75rem;'>{count}</td><td>{nick_sec}</td><td><span class='role'>{p.get('role','Soldier')}</span></td>"
            html += f"<td style='text-align:center'><span class='main-score'>{p_res['total']:,}</span></td>"
            for i, g in enumerate(p_res['growths']):
                if i > today_idx: # Future
                    html += '<td style="text-align:center; color:#30363d">-</td>'
                elif g > 0:
                    html += f"<td style='text-align:center'><span class='day-growth'>+{g:,}</span></td>"
                elif i < first: # Hasn't joined yet
                    html += '<td style="text-align:center; color:#8b949e">-</td>'
                elif i > last: # Left early
                    html += '<td style="text-align:center"><span class="absent" title="Покинул клан">X</span></td>'
                else:
                    html += '<td style="text-align:center; color:#484f58; font-size: 0.85rem;">0</td>'
            html += "</tr>"
        html += "</tbody></table></div></div></body></html>"
        with open(os.path.join(REPORTS_DIR, f"report_{w_key}.html"), 'w', encoding='utf-8') as f: f.write(html)
    with open(MAIN_REPORT, 'w', encoding='utf-8') as f:
        f.write(f'<html><head><meta http-equiv="refresh" content="0; url=reports/report_{all_ws[-1]}.html"></head></html>')
    if AUTO_PUSH: run_git_push()
if __name__ == "__main__":
    h, u, r = fetch_data(); 
    if h: generate_web_report(h, u, r)
