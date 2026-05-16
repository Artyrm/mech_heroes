import json
import os
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def get_data():
    uid = "227408"
    monday = datetime(2026, 5, 11, tzinfo=timezone.utc)
    
    all_snaps = []
    sn_dir = 'clan_monitor/snapshots'
    if not os.path.exists(sn_dir): sn_dir = 'snapshots'
        
    for fn in os.listdir(sn_dir):
        if not fn.endswith('.json') or not fn.startswith('points_utc_'): continue
        try:
            parts = fn.replace('.json','').split('_')
            ts_str = f"{parts[2]} {parts[3].replace('-',':')}"
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            with open(os.path.join(sn_dir, fn), 'r') as f:
                data = json.load(f)
                if uid in data.get('pts', {}):
                    all_snaps.append({'time': dt, 'pts': data['pts'][uid]})
        except: continue
    
    all_snaps.sort(key=lambda x: x['time'])
    week_snaps = [s for s in all_snaps if monday <= s['time'] < monday + timedelta(days=7)]
    
    adj_path = 'clan_monitor/manual_adjustments.json'
    if not os.path.exists(adj_path): adj_path = 'manual_adjustments.json'
    with open(adj_path, 'r') as f:
        adj_db = json.load(f)
    
    days_data = []
    for i in range(7):
        d_start = monday + timedelta(days=i)
        d_str = d_start.strftime("%Y-%m-%d")
        day_snaps = [s for s in week_snaps if d_start <= s['time'] < d_start + timedelta(days=1)]
        manual = adj_db.get(d_str, {}).get(uid, [])
        if not isinstance(manual, list): manual = [manual]
        manual = [int(v) for v in manual]
        days_data.append({'start': d_start, 'snaps': day_snaps, 'manual': manual})
    
    return days_data

def plot(days):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(18, 11))
    
    # SIMPLE ROBUST STREAM LOGIC
    total_acc = 0
    current_base = 0 # Monday 00:00 starts at 0
    
    cum_times, cum_vals = [], []
    raw_times, raw_vals = [], []
    day_markers = []
    now_utc = datetime.now(timezone.utc)

    # Initial anchor at 00:00 Monday
    cum_times.append(days[0]['start'])
    cum_vals.append(0)

    for idx, day in enumerate(days):
        manual_vals = day['manual']
        manual_idx = 0
        session_max = current_base

        for sn in day['snaps']:
            val = sn['pts']
            raw_times.append(sn['time'])
            raw_vals.append(val)
            
            if val < current_base:
                # DROP / EXIT
                missed = 0
                if manual_idx < len(manual_vals):
                    mv = manual_vals[manual_idx]
                    if mv > session_max: missed = mv - session_max
                    manual_idx += 1
                
                total_acc += missed
                current_base = val
                session_max = val
            else:
                # GROWTH
                total_acc += (val - current_base)
                current_base = val
                session_max = max(session_max, val)
            
            cum_times.append(sn['time'])
            cum_vals.append(total_acc)

        # End of day manual
        while manual_idx < len(manual_vals):
            mv = manual_vals[manual_idx]
            if mv > session_max:
                total_acc += (mv - session_max)
            session_max = 0
            current_base = 0
            manual_idx += 1
            cum_times.append(cum_times[-1] + timedelta(minutes=1))
            cum_vals.append(total_acc)
            if raw_times:
                raw_times.append(raw_times[-1] + timedelta(minutes=1))
                raw_vals.append(0)

    # Intersection Interpolation
    if cum_times:
        ts = np.array([t.timestamp() for t in cum_times])
        vs = np.array(cum_vals)
        for i in range(8): # Check up to Sunday end
            d_b = days[0]['start'] + timedelta(days=i)
            if d_b > now_utc and i < 7: continue
            if d_b.timestamp() < ts[0] or d_b.timestamp() > ts[-1]: continue
            v_i = np.interp(d_b.timestamp(), ts, vs)
            day_markers.append((d_b, v_i))

    # Plot
    if raw_times:
        ax.fill_between(raw_times, raw_vals, color='#58a6ff', alpha=0.2, label='Instantaneous Pts (Area)')
        ax.plot(raw_times, raw_vals, color='#58a6ff', linewidth=2, alpha=0.8, label='Instantaneous Pts (Blue Line)')
    
    pure_raw_times = [sn['time'] for d in days for sn in d['snaps']]
    pure_raw_vals = [sn['pts'] for d in days for sn in d['snaps']]
    ax.scatter(pure_raw_times, pure_raw_vals, color='#58a6ff', s=40, edgecolors='white', linewidths=0.5, zorder=15, label='Actual Snapshots (Dots)')
    
    if cum_times:
        ax.plot(cum_times, cum_vals, color='#3fb950', linewidth=5, label='Total Weekly Growth (Green)', zorder=10)

    if day_markers:
        print("\n--- DAY BOUNDARY MARKERS (RED DOTS) ---")
        for x, y in day_markers:
            print(f"{x.strftime('%Y-%m-%d %H:%M')} UTC: {int(y)}")
        print("---------------------------------------\n")
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
    print(f"Graph saved. Final Acc: {int(total_acc)}")
    plt.close()

if __name__ == "__main__":
    d = get_data()
    plot(d)
