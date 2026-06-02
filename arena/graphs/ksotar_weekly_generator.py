import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt

# Paths
SNAPSHOTS_DIR = r"G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots"
OUTPUT_FILENAME = "ksotar_weekly.png"
UID = "227408"  # ksotar
START_DATE = "2026-06-01" 
END_DATE = "2026-06-07"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)

def get_data():
    # 1. Load all snapshots as raw data
    files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_")])
    data = []
    
    for fn in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
        if not m: continue
        date_str = m.group(1)
        if date_str < START_DATE or date_str > END_DATE: continue
            
        dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        path = os.path.join(SNAPSHOTS_DIR, fn)
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            pts_map = d.get("pts", d)
            pts = pts_map.get(UID)
            if pts is not None:
                data.append({"time": dt, "pts": int(pts), "type": "snap"})
        except: pass
            
    # 2. Load manual adjustments
    manual_adj_path = os.path.join(os.path.dirname(os.path.dirname(SNAPSHOTS_DIR)), "clan_monitor", "manual_adjustments.json")
    with open(manual_adj_path, 'r', encoding='utf-8') as f:
        manual_data = json.load(f)
    
    # 3. Apply manual adjustments in-memory
    # Identify resets and compare snapshots with manual data
    data.sort(key=lambda x: x["time"])
    
    for i in range(len(data) - 1):
        if data[i+1]['pts'] < data[i]['pts']: # Reset found (data[i] is pre-reset)
            date_str = data[i]['time'].strftime("%Y-%m-%d")
            if date_str in manual_data:
                m_pts = manual_data[date_str].get(UID)
                if m_pts and m_pts[0] > data[i]['pts']:
                    data[i]['pts'] = m_pts[0] # Just update the value, timestamp stays same
                    data[i]['type'] = 'manual'
            
    return data

def plot_data(data):
    if not data: 
        print("No data found.")
        return

    # Add start-of-week point if needed (not here to avoid artificial points)
    times = [d["time"] for d in data]
    pts = [d["pts"] for d in data]

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(times, pts, marker='.', linestyle='-', color='#aaaaaa', alpha=0.5, label='Raw Points')

    cumulative_pts = []
    total = 0
    prev_val = 0
    
    # Store resets for annotation
    resets = []
    
    for d in data:
        val = d["pts"]
        if val < prev_val and prev_val != 0:
            resets.append((d['time'], val))
            print(f"DEBUG: RESET detected at {d['time'].strftime('%H:%M')} | Prev: {prev_val} | Curr: {val}")
        else:
            total += (val - prev_val)
        cumulative_pts.append(total)
        prev_val = val
        
    ax.plot(times, cumulative_pts, marker='', linestyle='-', color='blue', linewidth=2, label='True Cumulative Growth')
    
    # Add reset markers
    for time_val, pt_val in resets:
        ax.axvline(x=time_val, color='red', linestyle='--', alpha=0.9, zorder=5)
        ax.annotate(f"RESET\n{time_val.strftime('%H:%M')}", 
                    xy=(time_val, max(cumulative_pts) * 0.9), 
                    xytext=(0, 10), 
                    textcoords='offset points',
                    ha='center', color='red', fontweight='bold', fontsize=10,
                    zorder=100)

    ax.set_ylim(0, max(max(pts), max(cumulative_pts)) * 1.1)
    ax.set_title(f"ksotar ({UID}) Personal Weekly Points - {START_DATE} to {END_DATE}")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Points")
    ax.legend()
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH)
    print(f"\nGraph saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    data = get_data()
    plot_data(data)
