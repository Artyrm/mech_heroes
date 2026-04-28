import os
import json
import re
from datetime import datetime, timedelta, timezone

SNAPSHOTS_DIR = 'snapshots'

def get_monday(dt): 
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

weekly_db = {}
all_snaps = sorted([fs for fs in os.listdir(SNAPSHOTS_DIR) if fs.endswith('.json')])

print(f"Total snapshots found: {len(all_snaps)}")

for fs in all_snaps:
    try:
        match = re.search(r'(\d{4}-\d{2}-\d{2})(?:_(\d{2}-\d{2}))?', fs)
        if not match: 
            print(f"  [SKIP] No date match: {fs}")
            continue
        
        day_str = match.group(1)
        time_str = match.group(2) if match.group(2) else '23-55'
        dt = datetime.strptime(f"{day_str}_{time_str}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
        monday = get_monday(dt)
        wkey = monday.strftime("%Y_W%W")
        
        if wkey not in weekly_db:
            weekly_db[wkey] = {"label": monday.strftime('%Y-%m-%d'), "days": {}}
        
        if day_str not in weekly_db[wkey]["days"] or dt > weekly_db[wkey]["days"][day_str]["time"]:
            with open(os.path.join(SNAPSHOTS_DIR, fs), 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                weekly_db[wkey]["days"][day_str] = {
                    "time": dt, 
                    "pts_count": len(data)
                }
                print(f"  [OK] Processed {fs} for {day_str} in week {wkey}")
    except Exception as e:
        print(f"  [ERROR] {fs}: {e}")

print("\nFinal structure in memory:")
for wk, val in weekly_db.items():
    print(f"Week {wk} (Start {val['label']}):")
    for dy, dval in val['days'].items():
        print(f"  Day {dy}: {dval['pts_count']} entries, last seen at {dval['time']}")
