import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SNAPSHOTS_DIR = "clan_monitor/snapshots"
ADJ_FILE = "clan_monitor/manual_adjustments.json"
UID = "227408"  # ksotar
START_DATE = "2026-05-11"

def get_data():
    # 1. Load manual adjustments
    with open(ADJ_FILE, 'r', encoding='utf-8') as f:
        adj_data = json.load(f)
    
    # 2. Load snapshots
    files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_")])
    raw_snaps = []
    for fn in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
        if not m: continue
        date_str = m.group(1)
        if date_str < START_DATE: continue
        dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        with open(os.path.join(SNAPSHOTS_DIR, fn), encoding='utf-8') as f:
            d = json.load(f)
        pts = d.get("pts", d).get(UID)
        if pts is not None:
            raw_snaps.append({"time": dt, "pts": int(pts), "date": date_str})

    # 3. Interleave manual points
    # Logic: if we have a manual entry for a day, and we see a "drop" in snapshots that day,
    # the manual entry likely happened just before that drop.
    final_timeline = []
    processed_adj = set()
    
    for i in range(len(raw_snaps)):
        curr = raw_snaps[i]
        prev = raw_snaps[i-1] if i > 0 else None
        
        # Check for a drop (reset)
        if prev and curr['pts'] < prev['pts']:
            # Reset detected! Check if we have an adjustment for this day or previous day
            date_key = curr['date']
            if date_key in adj_data and UID in adj_data[date_key] and date_key not in processed_adj:
                for val in adj_data[date_key][UID]:
                    # Inject manual point 1 minute before the re-entry snapshot
                    final_timeline.append({"time": curr['time'] - timedelta(minutes=1), "pts": val, "type": "manual"})
                processed_adj.add(date_key)
        
        final_timeline.append({"time": curr['time'], "pts": curr['pts'], "type": "snap"})

    # Handle adjustments that happened after the last snapshot of the day (not followed by a re-entry snap yet)
    for date_key, users in adj_data.items():
        if date_key >= START_DATE and UID in users and date_key not in processed_adj:
            # Check if we are already past this date
            # Just put it at the end of that day
            dt_end = datetime.strptime(date_key, "%Y-%m-%d").replace(hour=23, minute=59, tzinfo=timezone.utc)
            for val in users[UID]:
                final_timeline.append({"time": dt_end, "pts": val, "type": "manual"})
    
    final_timeline.sort(key=lambda x: x["time"])
    return final_timeline

def plot(data):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(16, 8))
    
    times = [d["time"] for d in data]
    pts = [d["pts"] for d in data]
    
    # Calculate True Cumulative
    actual_total = 0
    prev_val = 0
    cum_actual = []
    for d in data:
        val = d["pts"]
        if val < prev_val:
            actual_total += val
        else:
            actual_total += (val - prev_val)
        cum_actual.append(actual_total)
        prev_val = val

    # Draw everything
    ax.plot(times, pts, color='#58a6ff', alpha=0.4, label='Raw Points (In-Clan)')
    
    # Manual points
    m_times = [d["time"] for d in data if d["type"] == "manual"]
    m_pts = [d["pts"] for d in data if d["type"] == "manual"]
    ax.scatter(m_times, m_pts, color='red', s=80, label='Exits (Manual Data)', zorder=5)
    
    # Cumulative
    ax.plot(times, cum_actual, color='#3fb950', linewidth=3, label='TRUE Cumulative Growth')
    
    # Formatting
    ax.set_title(f"ksotar Analysis (May 11 - May 16)\nPrecise Reconstruction from Snapshots & Manual Logs")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
    plt.xticks(rotation=30)
    plt.grid(True, alpha=0.1)
    plt.legend()
    
    # Show last total
    plt.annotate(f"Final Total: {cum_actual[-1]:,}".replace(',',' '), 
                 xy=(times[-1], cum_actual[-1]), xytext=(10, 10),
                 textcoords='offset points', color='#3fb950', weight='bold')

    plt.tight_layout()
    plt.savefig("ksotar_corrected.png")
    print(f"Graph saved. Final calculated points: {cum_actual[-1]}")

if __name__ == "__main__":
    d = get_data()
    plot(d)
