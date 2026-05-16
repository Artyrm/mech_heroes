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
    global_max = base # Global peak achieved in the clan (starts from Sunday end)
    total_acc = 0
    
    # Data for cumulative line
    cum_times, cum_vals = [], []
    # Data for instantaneous line (Raw snapshots)
    raw_times, raw_vals = [], []
    
    day_markers = []
    now_utc = datetime.now(timezone.utc)

    # Initial state
    cum_times.append(days[0]['start'])
    cum_vals.append(0)

    for idx, day in enumerate(days):
        is_monday = (idx == 0)
        server_reset_done = not is_monday
        manual_vals = day['manual']
        manual_idx = 0
        
        # In this logic, we don't care about sessions, only the absolute peak
        for sn in day['snaps']:
            val = sn['pts']
            raw_times.append(sn['time'])
            raw_vals.append(val)
            
            # Growth only counts if we exceed the global max
            if val > global_max:
                total_acc += (val - global_max)
                global_max = val
            
            cum_times.append(sn['time'])
            cum_vals.append(total_acc)

        # Handle manual adjustments (as peak overrides)
        while manual_idx < len(manual_vals):
            mv = manual_vals[manual_idx]
            if mv > global_max:
                total_acc += (mv - global_max)
                global_max = mv
            manual_idx += 1
            cum_times.append(cum_times[-1] + timedelta(minutes=1))
            cum_vals.append(total_acc)
            # Visual exit
            raw_times.append(raw_times[-1] + timedelta(minutes=1))
            raw_vals.append(0)

        # Connect boundary to host red markers
        next_day_start = day['start'] + timedelta(days=1)
        if next_day_start <= now_utc:
            cum_times.append(next_day_start)
            cum_vals.append(total_acc)
            day_markers.append((next_day_start, total_acc))

    # 1. Instantaneous Graph (Fill)
    ax.fill_between(raw_times, raw_vals, color='#58a6ff', alpha=0.2, label='Instantaneous Pts (Area)')
    ax.plot(raw_times, raw_vals, color='#58a6ff', linewidth=2, alpha=0.8, label='Instantaneous Pts (Blue Line)')
    
    # Add explicit dots for actual snapshots
    pure_raw_times = [sn['time'] for d in days for sn in d['snaps']]
    pure_raw_vals = [sn['pts'] for d in days for sn in d['snaps']]
    ax.scatter(pure_raw_times, pure_raw_vals, color='#58a6ff', s=40, edgecolors='white', linewidths=0.5, zorder=15, label='Actual Snapshots (Dots)')
    
    # 2. Cumulative Growth (Line)
    ax.plot(cum_times, cum_vals, color='#3fb950', linewidth=5, label='Total Weekly Growth (Green)', zorder=10)

    # Markers for Daily Results
    if day_markers:
        mx, my = zip(*day_markers)
        ax.scatter(mx, my, color='#f85149', s=150, edgecolors='white', zorder=20)
        for x, y in day_markers:
            ax.annotate(f"{int(y):,}".replace(',',' '), xy=(x, y), xytext=(0, 20),
                        textcoords='offset points', color='#f85149', weight='bold', size=14, ha='center',
                        bbox=dict(boxstyle="round,pad=0.3", fc="#161b22", ec="#f85149", alpha=0.9))

    ax.set_title(f"ksotar Analysis: Instantaneous vs Accumulated", fontsize=22, pad=30)
    ax.set_ylabel('Points', fontsize=14)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m\n00:00'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.grid(True, alpha=0.1)
    ax.legend(loc='upper left', fontsize=12)
    
    plt.tight_layout()
    plt.savefig("ksotar_utc_final.png", dpi=140)
    print(f"Graph saved. Final Acc: {cum_vals[-1]}")

if __name__ == "__main__":
    b, d = get_data()
    plot(b, d)
