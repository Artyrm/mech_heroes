import os
import json
import re
from datetime import datetime, timezone
import matplotlib.pyplot as plt

SNAPSHOTS_DIR = "clan_monitor/snapshots"
UID = "227408"  # ksotar
START_DATE = "2026-05-11"

def get_data():
    files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_")])
    data = []
    for fn in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
        if not m:
            continue
        date_str = m.group(1)
        if date_str < START_DATE:
            continue
            
        dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        path = os.path.join(SNAPSHOTS_DIR, fn)
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            pts_map = d.get("pts", d)
            pts = pts_map.get(UID)
            if pts is not None:
                data.append({"time": dt, "pts": int(pts), "file": fn})
        except Exception as e:
            print(f"Error reading {fn}: {e}")
    return data

def plot_data(data):
    if not data:
        print("No data found for ksotar.")
        return

    times = [d["time"] for d in data]
    pts = [d["pts"] for d in data]

    plt.figure(figsize=(12, 6))
    plt.plot(times, pts, marker='.', linestyle='-', color='b', label='Points (Raw)')
    
    # Calculate cumulative points (naive fix for resets)
    cumulative_pts = []
    total = 0
    prev_val = 0
    for d in data:
        val = d["pts"]
        if val < prev_val:
            # Reset detected
            total += val
        else:
            total += (val - prev_val)
        cumulative_pts.append(total)
        prev_val = val
        
    plt.plot(times, cumulative_pts, marker='', linestyle='--', color='r', label='Cumulative Points (Adjusted)')

    plt.title(f"ksotar ({UID}) Points - Week starting {START_DATE}")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Points")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("ksotar_points_analysis.png")
    print("Plot saved to ksotar_points_analysis.png")

    # Detailed table
    print(f"{'Time (UTC)':<20} {'Raw Pts':>8} {'Delta':>8} {'Cumulative':>12} {'File'}")
    print("-" * 75)
    prev_val = 0
    total = 0
    for i, d in enumerate(data):
        val = d["pts"]
        delta = val - prev_val
        if val < prev_val:
            total += val
            delta_str = f"{delta} (R)"
        else:
            total += (val - prev_val)
            delta_str = f"+{delta}" if delta >= 0 else str(delta)
            
        print(f"{d['time'].strftime('%Y-%m-%d %H:%M'):<20} {val:>8} {delta_str:>8} {total:>12} {d['file']}")
        prev_val = val

if __name__ == "__main__":
    data = get_data()
    plot_data(data)
