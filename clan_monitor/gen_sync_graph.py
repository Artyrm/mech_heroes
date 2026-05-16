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
    all_snaps = []
    for f in snaps:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', f)
        dt_utc = datetime.strptime(m.group(0), '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, f), encoding='utf-8') as fs:
            d = json.load(fs)
            p = d.get('pts', {}).get(UID)
            if p is not None:
                all_snaps.append({"time": dt_utc, "pts": int(p)})
    
    with open(ADJ_FILE, encoding='utf-8') as f:
        adj = json.load(f)
    
    monday_utc = datetime.strptime(START_DATE, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # Base from previous Sunday
    pre_week = [e for e in all_snaps if e['time'] < monday_utc]
    sunday_base = pre_week[-1]['pts'] if pre_week else 0
    
    # Weekly events
    weekly_snaps = [e for e in all_snaps if e['time'] >= monday_utc]
    
    # Manual adjustments on weekly timeline
    manual_events = []
    for d_str, users in adj.items():
        if d_str >= START_DATE and UID in users:
            # We don't have time for manual, but let's find the reset in snaps
            dt_manual = datetime.strptime(d_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            for v in users[UID]:
                manual_events.append({"time": dt_manual, "pts": int(v), "type": "manual"})

    return sunday_base, weekly_snaps, manual_events, monday_utc

def plot(sunday_base, snaps, manual_events, monday_utc):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(18, 11))
    
    # We need to build a single chronological sequence of events
    # to maintain strict Raw vs Cumulative synchronization.
    events = []
    for s in snaps: events.append({"time": s['time'], "pts": s['pts'], "type": "snap"})
    for m in manual_events: events.append(m)
    events.sort(key=lambda x: x["time"])

    current_base = sunday_base
    total_burned = 0
    
    times = []
    raw_pts = []
    cum_growth = []
    
    # Boundary tracking
    day_markers = []
    next_boundary = monday_utc

    # Initial state at Monday 00:00
    times.append(monday_utc)
    raw_pts.append(sunday_base)
    cum_growth.append(0)
    day_markers.append((monday_utc, 0))
    next_boundary += timedelta(days=1)

    for ev in events:
        # Check if we passed a day boundary to record a marker
        while ev['time'] >= next_boundary:
            # Estimate cum_growth at boundary (it's the last known growth)
            day_markers.append((next_boundary, cum_growth[-1]))
            next_boundary += timedelta(days=1)

        val = ev['pts']
        
        if val < current_base:
            # RESET detected
            total_burned += current_base
        
        current_growth = val - sunday_base + total_burned
        
        times.append(ev['time'])
        raw_pts.append(val)
        cum_growth.append(current_growth)
        
        if ev['type'] == 'manual':
            # Manual exit peak is processed, next start is 0
            total_burned += (val - val) # logical placeholder
            current_base = 0 
        else:
            current_base = val

    # Final boundary markers if needed
    while next_boundary <= datetime.now(timezone.utc):
        day_markers.append((next_boundary, cum_growth[-1]))
        next_boundary += timedelta(days=1)

    # --- Plotting ---
    # 1. Raw Points (Blue Area)
    ax.fill_between(times, raw_pts, color='#58a6ff', alpha=0.15, label=f'Current Points (Base {sunday_base})')
    ax.plot(times, raw_pts, color='#58a6ff', alpha=0.5, linewidth=1, linestyle='--')
    ax.scatter(times, raw_pts, color='#58a6ff', s=20, alpha=0.6)

    # 2. Cumulative Growth (Green Line)
    ax.plot(times, cum_growth, color='#3fb950', linewidth=6, label='TRUE CUMULATIVE GROWTH', zorder=5)
    
    # 3. Day Markers (Red Dots)
    mx, my = zip(*day_markers)
    ax.scatter(mx, my, color='#f85149', s=250, edgecolors='white', zorder=10, label='UTC Day Boundary (00:00)')
    for x, y in day_markers:
        ax.annotate(f"{int(y):,}".replace(',',' '), xy=(x, y), xytext=(0, 20),
                    textcoords='offset points', color='#f85149', weight='bold', size=14, ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#161b22", ec="#f85149", alpha=0.9))

    # Formatting
    ax.set_title(f"ksotar Performance: PERFECTLY SYNCHRONIZED UTC\nGreen Line = Raw Points - Start_Base + Sum_of_Resets", fontsize=22, pad=30)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m\n00:00'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.grid(True, alpha=0.1)
    ax.legend(loc='upper left', fontsize=14)
    
    plt.annotate(f"WEEK TOTAL:\n{int(cum_growth[-1]):,}".replace(',',' '), 
                 xy=(times[-1], cum_growth[-1]), xytext=(30, 0),
                 textcoords='offset points', color='#3fb950', weight='bold', size=20,
                 arrowprops=dict(arrowstyle='->', color='#3fb950', lw=3))

    plt.tight_layout()
    plt.savefig("ksotar_sync_final.png", dpi=140)
    print(f"Synchronized graph saved to ksotar_sync_final.png. Total: {cum_growth[-1]}")

if __name__ == "__main__":
    base, snaps, manual, monday = get_data()
    plot(base, snaps, manual, monday)
