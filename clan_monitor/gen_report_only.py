import json, os, re, sys, traceback, argparse
from datetime import datetime, timedelta, timezone
import numpy as np

# ==============================================================================
# CLAN ACCOUNTANT - LOCAL ONLY GENERATOR (SYNCED WITH v0.3.11)
# ==============================================================================

ADJUSTMENTS_FILE = 'manual_adjustments.json'
TRANS_CACHE_FILE = 'translations_cache.json'
MEMBERS_DB = 'members_name_db.json'

def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

# PATHS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SNAPSHOTS_DIR = os.path.join(SCRIPT_DIR, 'snapshots')
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, 'clan', 'ORDA')
REPORTS_DIR = os.path.join(OUTPUT_ROOT, 'reports')
MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'index.html')
MEMBERS_DB_PATH = os.path.join(SCRIPT_DIR, MEMBERS_DB)

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

def generate_local_report():
    names_map = load_json(MEMBERS_DB_PATH)
    adj_db = load_json(os.path.join(SCRIPT_DIR, ADJUSTMENTS_FILE))
    
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

    if not sd:
        print("[!] Нет данных для генерации отчета."); return

    last_data_ts = sd[-1]['time'].astimezone(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M") if sd else "НЕТ ДАННЫХ"
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
        
        reset_players = set()
        for d_str in adj_db:
            reset_players.update(adj_db[d_str].keys())

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
                
                if i == 0: prev_day_end = 0

                if day_snaps:
                    vals = [s['pts'][str(uid)] for s in day_snaps]
                    
                    if use_reset_logic:
                        day_growth = 0
                        last_v = prev_day_end
                        d_key = d_start.strftime("%Y-%m-%d")
                        manual_vals = adj_db.get(d_key, {}).get(str(uid), [])
                        if not isinstance(manual_vals, list): manual_vals = [manual_vals]
                        
                        for v in vals:
                            effective_v = v
                            if v < last_v and manual_vals:
                                last_v = max(last_v, max(manual_vals))
                            
                            if effective_v >= last_v:
                                day_growth += (effective_v - last_v)
                            else:
                                day_growth += effective_v
                            last_v = effective_v
                        daily_growths[i] = int(day_growth)
                    else:
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
        tr = clan_rats[6] if clan_rats[6] else (next((r['rating'] for r in reversed(clan_stats) if r['rating']), 0))
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
    .nick {{ color: #fff; font-weight: 700; font-size: 0.9rem; }}
    .trait {{ color: var(--gold); font-size: 0.68rem; font-weight: 500; font-style: italic; opacity: 0.7; }}
    .role {{ font-size: 0.58rem; color: #8b949e; border: 1px solid var(--border); padding: 1px 3px; border-radius: 3px; }}
    .main-score {{ font-family: 'Roboto Mono'; font-size: 1rem; color: var(--gold); font-weight: 700; }}
    .day-growth {{ font-family: 'Roboto Mono'; font-size: 0.9rem; color: var(--green); font-weight: 700; }}
    .absent {{ color: var(--error); font-weight: 900; font-size: 1.1rem; font-family: 'Orbitron'; }}
    .no-growth {{ color: #484f58; opacity: 0.4; font-family: 'Roboto Mono'; text-align: center; }}
</style></head><body><div class="container"><header>
<h1>O R D A</h1><div class="subtitle">CLAN ANALYTICS CORE</div></header>
<nav>{nav}</nav>
<div class="table-container"><div class="update-time">ДАННЫЕ ОТ: {last_data_ts} (MSK)</div><table>
    <thead><tr><th style="width:30px">№</th><th>Участник</th><th>Звание</th><th style="text-align:center">Всего</th>
    {" ".join([f'<th>{(monday+timedelta(days=i)):%a %d.%m}</th>' for i in range(7)])}</tr></thead>
    <tbody>
    <tr class="clan-row"><td style="text-align:center; color:#58a6ff">--</td><td colspan="2">ИСТОРИЧЕСКИЙ РЕЙТИНГ</td><td style="text-align:center"><span class="main-score" style="color:#fff">{fmt(tr)}</span></td>{" ".join(c_cells)}</tr>
    <tr class="clan-row" style="background:#0d1117; height: 45px;"><td style="text-align:center; color:var(--green)">--</td><td colspan="2" style="color:var(--green); font-size: 0.8rem;">СУММАРНЫЙ ЗАРАБОТОК</td><td style="text-align:center"><span class="main-score" style="color:var(--green); font-size: 0.95rem;">{fmt(sum(clan_growths))}</span></td>{" ".join(s_cells)}</tr>"""
        for count, uid in enumerate(sorted_ids, 1):
            p = names_map.get(uid, {"nick": f"ID:{uid}", "role": "Soldier"}); p_res = pl_res[uid]; nick_sec = f"<div class='nick-cell'><span class='nick'>{p['nick']}</span>"
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
    print("[*] ОТЧЕТЫ УСПЕШНО ОБНОВЛЕНЫ (Локально).")

if __name__ == "__main__":
    generate_local_report()
