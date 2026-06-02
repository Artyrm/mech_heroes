import json, os, re, sys, traceback
from datetime import datetime, timedelta, timezone
import numpy as np

# --- Helper functions ---
def fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

# Need the translation function
def translate_traits_batch(traits_list, trans_cache, script_dir):
    if not traits_list: return ""
    full_str = ", ".join(traits_list).replace("_", " ")
    if full_str in trans_cache: return trans_cache[full_str]
    # (Dictionary logic omitted for brevity, keeping structural integrity)
    return full_str

# --- Main Report Generation Logic ---
def generate_local_report():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SNAPSHOTS_DIR = os.path.join(SCRIPT_DIR, 'snapshots')
    OUTPUT_ROOT = os.path.join(SCRIPT_DIR, 'clan', 'ORDA')
    REPORTS_DIR = os.path.join(OUTPUT_ROOT, 'reports')
    MAIN_REPORT = os.path.join(OUTPUT_ROOT, 'index.html')
    MEMBERS_DB_PATH = os.path.join(SCRIPT_DIR, 'members_name_db.json')
    ADJUSTMENTS_FILE = 'manual_adjustments.json'
    TRANS_CACHE_FILE = 'translations_cache.json'
    
    if not os.path.exists(REPORTS_DIR): os.makedirs(REPORTS_DIR)
    
    # 1. Загрузка данных
    snf = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.startswith('points_utc_')])
    if not snf:
        print("[!] Нет данных снэпшотов.")
        return
        
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
    
    names_map = load_json(MEMBERS_DB_PATH)
    adj_db = load_json(os.path.join(SCRIPT_DIR, ADJUSTMENTS_FILE))
    
    # Реконструкция недель
    weeks = {}
    for e in sd:
        monday = (e['time'] - timedelta(days=e['time'].weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        wk = monday.strftime("%Y_W%W")
        if wk not in weeks: weeks[wk] = {"monday": monday, "label": f"{monday.strftime('%d.%m')} - {(monday+timedelta(days=6)).strftime('%d.%m')}", "days": {}}
        dk = e['time'].strftime("%Y-%m-%d")
        if dk not in weeks[wk]["days"]: weeks[wk]["days"][dk] = []
        weeks[wk]["days"][dk].append(e)

    print("[*] Локальная генерация отчетов...")
    for w_key in sorted(weeks.keys()):
        week = weeks[w_key]
        monday = week["monday"]
        players = set()
        for d in week["days"].values():
            for e in d: players.update(e['pts'].keys())
        
        reset_players = set()
        for d_str in adj_db: reset_players.update(adj_db[d_str].keys())

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
                        # Truth Logic (original)
                        day_growth = 0; last_v = prev_day_end
                        
                        d_key = d_start.strftime("%Y-%m-%d")
                        manual_vals = adj_db.get(d_key, {}).get(str(uid), [])
                        if not isinstance(manual_vals, list): manual_vals = [manual_vals]
                        
                        for v in vals:
                            effective_v = v
                            if v < last_v and manual_vals: last_v = max(last_v, max(manual_vals))
                            if effective_v >= last_v: day_growth += (effective_v - last_v)
                            else: day_growth += effective_v
                            last_v = effective_v
                        daily_growths[i] = int(day_growth)
                    else:
                        daily_growths[i] = max(0, vals[-1] - prev_day_end)
                    prev_day_end = vals[-1]
                else: daily_growths[i] = 0
                
                d_str = d_start.strftime("%Y-%m-%d"); ex = adj_db.get(d_str, {}).get(str(uid), []); 
                if not isinstance(ex, list): ex = [ex]
                presence[i] = (any(str(uid) in s['pts'] for s in week["days"].get(d_str, [])) if d_str in week["days"] else False) or bool(ex)
                
            pl_res[uid] = {"growths": daily_growths, "total": sum(daily_growths), "presence": presence, "first_p": next((idx for idx, p in enumerate(presence) if p), 999), "last_p": next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)}
            
        print(f"[*] Отчет {w_key} сгенерирован.")

if __name__ == "__main__":
    generate_local_report()
