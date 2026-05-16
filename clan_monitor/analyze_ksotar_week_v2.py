import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt

SNAPSHOTS_DIR = "clan_monitor/snapshots"
UID = "227408"  # ksotar
START_DATE = "2026-05-11"

# Manual data from manual_adjustments.json for ksotar
MANUAL_DATA = {
    "2026-05-12": [10502],
    "2026-05-14": [10575],
    "2026-05-15": [13205]
}

def get_data():
    files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_")])
    data = []
    for fn in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
        if not m: continue
        date_str = m.group(1)
        if date_str < START_DATE: continue
            
        dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        path = os.path.join(SNAPSHOTS_DIR, fn)
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            pts_map = d.get("pts", d)
            pts = pts_map.get(UID)
            if pts is not None:
                data.append({"time": dt, "pts": int(pts), "file": fn, "type": "snap"})
        except: pass
        
    # Inject manual points
    # We'll place them just before the first snapshot of the NEXT day or at the end of their day
    for d_str, vals in MANUAL_DATA.items():
        dt_base = datetime.strptime(d_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        # Place manual point at 23:59 of that day
        dt_exit = dt_base + timedelta(hours=23, minutes=59)
        for v in vals:
            data.append({"time": dt_exit, "pts": v, "file": "MANUAL", "type": "manual"})
            
    data.sort(key=lambda x: x["time"])
    return data

def plot_data(data):
    if not data: return

    times = [d["time"] for d in data]
    pts = [d["pts"] for d in data]

    plt.figure(figsize=(15, 8))
    
    # Raw points
    plt.plot(times, pts, marker='.', linestyle='-', color='#aaaaaa', alpha=0.5, label='Raw Points (Snapshots)')
    
    # Highlight manual points
    manual_pts = [d for d in data if d["type"] == "manual"]
    plt.scatter([m["time"] for m in manual_pts], [m["pts"] for m in manual_pts], 
                color='red', s=100, zorder=5, label='Manual Exit Points')

    # Detect drops and calculate cumulative
    # A drop is when pts < prev_pts
    cumulative_pts = []
    total = 0
    prev_val = 0
    
    print(f"{'Time (UTC)':<20} {'Raw Pts':>8} {'Source':>8} {'Total Growth':>12}")
    print("-" * 60)
    
    for d in data:
        val = d["pts"]
        source = d["type"]
        
        if val < prev_val:
            # We treat a drop as a reset. 
            # Growth from 0 to val
            total += val
            marker = " [RESET]"
        else:
            # Normal growth
            total += (val - prev_val)
            marker = ""
            
        cumulative_pts.append(total)
        print(f"{d['time'].strftime('%m-%d %H:%M'):<20} {val:>8} {source:>8} {total:>12}{marker}")
        prev_val = val
        
    plt.plot(times, cumulative_pts, marker='', linestyle='-', color='blue', linewidth=2, label='True Cumulative Growth')

    plt.title(f"ksotar ({UID}) Points & Growth - Manual Correlation")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Points")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("ksotar_manual_correlation.png")
    print("\nGraph saved to ksotar_manual_correlation.png")

if __name__ == "__main__":
    data = get_data()
    plot_data(data)
