import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SNAPSHOTS_DIR = 'clan_monitor/snapshots'
ADJ_FILE = 'clan_monitor/manual_adjustments.json'
UID = '227408'
START_DATE = '2026-05-11'

def get_data():
    snaps = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith('points_utc_2026-05-')])
    all_data = []
    for f in snaps:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', f)
        dt = datetime.strptime(m.group(0), '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, f), encoding='utf-8') as fs:
            d = json.load(fs)
            p = d.get('pts', {}).get(UID)
            if p is not None:
                all_data.append({"time": dt, "pts": int(p)})
    
    with open(ADJ_FILE, encoding='utf-8') as f:
        adj = json.load(f)
    
    days = []
    for i in range(7):
        d_str = (datetime.strptime(START_DATE, '%Y-%m-%d') + timedelta(days=i)).strftime('%Y-%m-%d')
        day_snaps = [s for s in all_data if s['time'].strftime('%Y-%m-%d') == d_str]
        manual_vals = adj.get(d_str, {}).get(UID, [])
        if not isinstance(manual_vals, list): manual_vals = [manual_vals]
        days.append({"date": d_str, "snaps": day_snaps, "manual": [int(v) for v in manual_vals]})
    return days

def plot(days):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(16, 10))
    
    current_base = 0
    total_acc = 0
    
    plot_times = []
    plot_cum = []
    snap_times, snap_pts = [], []
    auto_resets, manual_exits = [], []

    for day in days:
        day_max_since_reset = 0
        manual_vals = day['manual']
        manual_idx = 0
        
        for sn in day['snaps']:
            val = sn['pts']
            snap_times.append(sn['time'])
            snap_pts.append(val)
            
            if val < current_base:
                # RESET detected. Check redundancy
                while manual_idx < len(manual_vals) and manual_vals[manual_idx] <= current_base:
                    manual_idx += 1
                
                auto_resets.append((sn['time'], 0))
                total_acc += val
                day_max_since_reset = val
            else:
                total_acc += (val - current_base)
                day_max_since_reset = max(day_max_since_reset, val)
            
            current_base = val
            plot_times.append(sn['time'])
            plot_cum.append(total_acc)

        while manual_idx < len(manual_vals):
            mv = manual_vals[manual_idx]
            dt_manual = datetime.strptime(day['date'], '%Y-%m-%d').replace(hour=23, minute=59, tzinfo=timezone.utc)
            if mv > day_max_since_reset:
                total_acc += (mv - day_max_since_reset)
            
            manual_exits.append((dt_manual, mv))
            current_base = 0 
            plot_times.append(dt_manual)
            plot_cum.append(total_acc)
            manual_idx += 1

    ax.fill_between(snap_times, snap_pts, color='#58a6ff', alpha=0.1)
    ax.scatter(snap_times, snap_pts, color='#58a6ff', s=25, label='Snapshots', zorder=2)
    
    if auto_resets:
        rx, ry = zip(*auto_resets)
        ax.scatter(rx, ry, color='orange', marker='^', s=120, label='Auto-Detected Rejoin', zorder=5)
    
    if manual_exits:
        mx, my = zip(*manual_exits)
        ax.scatter(mx, my, color='red', marker='x', s=100, linewidth=3, label='Manual Exit Peak', zorder=5)

    ax.plot(plot_times, plot_cum, color='#3fb950', linewidth=4, label='TRUE TOTAL (Cumulative)', zorder=4)
    
    ax.set_title(f"ksotar Performance: SMART LOGIC V2\nNo redundant exits. Real carry-over.", fontsize=18, pad=20)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
    plt.xticks(rotation=30); ax.grid(True, alpha=0.05); ax.legend(loc='upper left')
    
    plt.annotate(f"FINAL TOTAL: {plot_cum[-1]:,}".replace(',',' '), 
                 xy=(plot_times[-1], plot_cum[-1]), xytext=(10, 30),
                 textcoords='offset points', color='#3fb950', weight='bold', size=16)

    plt.tight_layout()
    plt.savefig("ksotar_smart_logic.png", dpi=130)
    print(f"Graph saved to ksotar_smart_logic.png. Final: {plot_cum[-1]}")

if __name__ == "__main__":
    d = get_data()
    plot(d)
