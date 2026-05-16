import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SNAPSHOTS_DIR = 'clan_monitor/snapshots'
ADJ_FILE = 'clan_monitor/manual_adjustments.json'
UID = '227408'
START_DATE = '2026-05-11' # Monday UTC

def get_data():
    snaps = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith('points_utc_2026-05-')])
    all_events = []
    for f in snaps:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', f)
        dt_utc = datetime.strptime(m.group(0), '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, f), encoding='utf-8') as fs:
            d = json.load(fs)
            p = d.get('pts', {}).get(UID)
            if p is not None:
                all_events.append({"time": dt_utc, "pts": int(p)})
    
    with open(ADJ_FILE, encoding='utf-8') as f:
        adj = json.load(f)
    
    monday_utc = datetime.strptime(START_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # Base from previous Sunday
    pre_week = [e for e in all_events if e['time'] < monday_utc]
    initial_base = pre_week[-1]['pts'] if pre_week else 0
    
    days_data = []
    for i in range(7):
        curr_day = monday_utc + timedelta(days=i)
        d_str = curr_day.strftime('%Y-%m-%d')
        next_day = curr_day + timedelta(days=1)
        
        day_snaps = [e for e in all_events if curr_day <= e['time'] < next_day]
        manual_vals = adj.get(d_str, {}).get(UID, [])
        if not isinstance(manual_vals, list): manual_vals = [manual_vals]
        
        days_data.append({
            "start": curr_day,
            "snaps": day_snaps,
            "manual": [int(v) for v in manual_vals]
        })
        
    return initial_base, days_data

def plot(base, days):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(18, 11))
    
    current_base = base
    total_acc = 0
    plot_times, plot_cum = [], []
    day_markers = []

    # Monday 00:00 UTC
    plot_times.append(days[0]['start'])
    plot_cum.append(0)
    day_markers.append((days[0]['start'], 0))

    for day in days:
        day_max = 0
        manual_vals = day['manual']
        manual_idx = 0
        
        for sn in day['snaps']:
            val = sn['pts']
            if val < current_base:
                while manual_idx < len(manual_vals) and manual_vals[manual_idx] <= current_base:
                    manual_idx += 1
                total_acc += val
                day_max = val
            else:
                total_acc += (val - current_base)
                day_max = max(day_max, val)
            
            current_base = val
            plot_times.append(sn['time'])
            plot_cum.append(total_acc)

        while manual_idx < len(manual_vals):
            mv = manual_vals[manual_idx]
            if mv > day_max: total_acc += (mv - day_max)
            current_base = 0
            manual_idx += 1
            plot_times.append(day['start'] + timedelta(hours=23, minutes=59))
            plot_cum.append(total_acc)

        # Mark NEXT day start
        day_markers.append((day['start'] + timedelta(days=1), total_acc))

    ax.plot(plot_times, plot_cum, color='#3fb950', linewidth=6, label='Cumulative (UTC)')
    
    # Visual check: Plot raw snaps to ensure alignment
    sn_x = [e['time'] for d in days for e in d['snaps']]
    sn_y = [e['pts'] for d in days for e in d['snaps']]
    ax.scatter(sn_x, sn_y, color='#58a6ff', s=30, alpha=0.4, label='Raw Snapshots (UTC)')

    # Labels
    mx, my = zip(*day_markers)
    ax.scatter(mx, my, color='#f85149', s=200, edgecolors='white', zorder=10)
    for x, y in day_markers:
        if x > datetime.now(timezone.utc) + timedelta(hours=1): continue
        ax.annotate(f"{int(y):,}".replace(',',' '), xy=(x, y), xytext=(0, 20),
                    textcoords='offset points', color='#f85149', weight='bold', size=14, ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#161b22", ec="#f85149", alpha=0.9))

    ax.set_title(f"ksotar Performance: STRICT UTC TIMELINE\nLabels at 00:00 UTC", fontsize=22, pad=30)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m\n00:00'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.grid(True, alpha=0.1)
    ax.legend(loc='upper left', fontsize=12)
    
    plt.tight_layout()
    plt.savefig("ksotar_utc_final.png", dpi=140)
    print(f"UTC Graph saved to ksotar_utc_final.png. Final: {total_acc}")

if __name__ == "__main__":
    b, d = get_data()
    plot(b, d)
