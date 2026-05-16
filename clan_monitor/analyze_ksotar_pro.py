import os
import json
import re
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SNAPSHOTS_DIR = "clan_monitor/snapshots"
UID = "227408"  # ksotar
START_DATE = "2026-05-11"

# Manual exit data from manual_adjustments.json for ksotar
MANUAL_DATA = {
    "2026-05-12": 10502,
    "2026-05-14": 10575,
    "2026-05-15": 13205
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
                data.append({"time": dt, "pts": int(pts), "type": "snap"})
        except: pass
        
    # Inject manual points more precisely
    # We place them at 23:59:59 of the day they represent
    for d_str, val in MANUAL_DATA.items():
        dt_exit = datetime.strptime(d_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        data.append({"time": dt_exit, "pts": val, "type": "manual"})
            
    data.sort(key=lambda x: x["time"])
    return data

def make_pro_plot(data):
    if not data: return

    # Setup styles
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(16, 9))
    
    times = [d["time"] for d in data]
    pts_raw = [d["pts"] for d in data]

    # Calculate Cumulative Growth (Actual)
    cumulative_actual = []
    total_actual = 0
    prev_val = 0
    for d in data:
        val = d["pts"]
        if val < prev_val:
            total_actual += val # Reset detection
        else:
            total_actual += (val - prev_val)
        cumulative_actual.append(total_actual)
        prev_val = val

    # Calculate "Old Algorithm" Growth (Approximation)
    # The old algorithm only looks at the last snapshot of each day compared to previous day
    reported_growth = []
    daily_stats = {}
    for d in data:
        day = d["time"].strftime("%Y-%m-%d")
        daily_stats[day] = d["pts"]
    
    # Simulating what the report shows
    total_reported = 0
    ref_day_val = 0
    days = sorted(daily_stats.keys())
    # We need to map this back to the timeframe for plotting
    current_rep_total = 0
    reported_timeline = []
    prev_d_key = None
    for d in data:
        d_key = d["time"].strftime("%Y-%m-%d")
        if prev_d_key and d_key != prev_d_key:
            ref_day_val = daily_stats[prev_d_key]
        
        val = d["pts"]
        # This is a simplification of the bug logic
        if val < ref_day_val:
             growth_increment = val
        else:
             growth_increment = val - ref_day_val
             
        # But wait, the report only updates at the end of the day. 
        # For visualization, let's just use the final delta we calculated in the table.
        prev_d_key = d_key

    # Manual override for visualization of the "Broken" vs "Actual"
    # Based on the table: [4144, 15206, 944, 2677, 12052] vs [4144, 15206, 9792, 11358, 24516]
    broken_totals = {
        "2026-05-11": 4144,
        "2026-05-12": 4144 + 15206,
        "2026-05-13": 4144 + 15206 + 944,
        "2026-05-14": 4144 + 15206 + 944 + 2677,
        "2026-05-15": 4144 + 15206 + 944 + 2677 + 12052
    }
    cumulative_broken = []
    for d in data:
        day = d["time"].strftime("%Y-%m-%d")
        cumulative_broken.append(broken_totals.get(day, 0))

    # --- Plotting ---
    
    # 1. Raw Points (Snapshots)
    ax1.fill_between(times, pts_raw, color='#58a6ff', alpha=0.2, label='Current Points (Raw)')
    ax1.plot(times, pts_raw, color='#58a6ff', linewidth=1, alpha=0.6)
    
    # 2. Manual Exit Points
    m_times = [d["time"] for d in data if d["type"] == "manual"]
    m_pts = [d["pts"] for d in data if d["type"] == "manual"]
    ax1.scatter(m_times, m_pts, color='#f85149', s=120, edgecolors='white', label='Manual Exit Data (Out of Clan)', zorder=5)

    # 3. Cumulative Lines
    ax1.plot(times, cumulative_actual, color='#3fb950', linewidth=4, label='REAL TOTAL (New Logic)')
    ax1.plot(times, cumulative_broken, color='#f2cc60', linewidth=3, linestyle='--', label='REPORTED TOTAL (Old Logic)')

    # Formatting
    ax1.set_title(f"ksotar Clan Points Analysis: Real vs Reported\n(Week 11.05 - 17.05)", fontsize=20, color='white', pad=20)
    ax1.set_xlabel("Time (UTC)", fontsize=14)
    ax1.set_ylabel("Points / Growth", fontsize=14)
    
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
    plt.xticks(rotation=30)
    
    ax1.grid(True, alpha=0.1)
    ax1.legend(loc='upper left', fontsize=12)
    
    # Add annotations for loss
    last_actual = cumulative_actual[-1]
    last_broken = cumulative_broken[-1]
    loss = last_actual - last_broken
    
    plt.annotate(f'LOST IN STATS:\n-{loss:,} pts'.replace(',', ' '), 
                 xy=(times[-1], last_broken), xytext=(-100, -60),
                 textcoords='offset points', color='#f85149', weight='bold', size=14,
                 arrowprops=dict(arrowstyle='->', color='#f85149'))

    plt.tight_layout()
    plt.savefig("ksotar_final_analysis.png", dpi=120)
    print("Graph saved to ksotar_final_analysis.png")

if __name__ == "__main__":
    data = get_data()
    make_pro_plot(data)
