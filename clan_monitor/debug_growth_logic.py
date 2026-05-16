import os
import json
import re
from datetime import datetime, timezone

SNAPSHOTS_DIR = 'clan_monitor/snapshots'
ADJ_FILE = 'clan_monitor/manual_adjustments.json'
UID = '227408'

def diag():
    snaps = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith('points_utc_2026-05-1')])
    events = []
    for f in snaps:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', f)
        dt = datetime.strptime(m.group(0), '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, f), encoding='utf-8') as fs:
            d = json.load(fs)
            p = d.get('pts', {}).get(UID)
            if p is not None:
                events.append({"time": dt, "pts": int(p), "type": "snap"})
    
    with open(ADJ_FILE, encoding='utf-8') as f:
        adj = json.load(f)
    for d_str, users in adj.items():
        if d_str >= '2026-05-11' and UID in users:
            dt = datetime.strptime(d_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            for v in users[UID]:
                events.append({"time": dt, "pts": int(v), "type": "manual"})
    
    events.sort(key=lambda x: x["time"])
    
    print(f"{'Time (UTC)':<18} | {'Pts':>6} | {'Type':<7} | {'Delta':>6} | {'Daily Growth'}")
    print("-" * 65)
    
    current_base = 0
    daily_totals = {}
    
    for e in events:
        day = e['time'].strftime('%Y-%m-%d')
        val = e['pts']
        
        if val < current_base:
            growth = val
        else:
            growth = val - current_base
            
        daily_totals[day] = daily_totals.get(day, 0) + growth
        
        print(f"{e['time'].strftime('%m-%d %H:%M'):<18} | {val:>6} | {e['type']:<7} | {growth:>6} | {daily_totals[day]:>8} ({day})")
        
        if e['type'] == 'manual':
            current_base = 0
        else:
            current_base = val

if __name__ == "__main__":
    diag()
