import os, json, re

SNAPSHOTS_DIR = "snapshots"
UID = "227408"  # ksotar

files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_2026-05-0")])

print(f"{'Файл':<45} {'Очки':>10}")
print("-" * 57)

prev_pts = None
for fn in files:
    m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
    if not m:
        continue
    path = os.path.join(SNAPSHOTS_DIR, fn)
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    pts_map = d.get("pts", d)
    pts = pts_map.get(UID)
    
    if pts is None:
        marker = "  <-- ОТСУТСТВУЕТ В СНЭПШОТЕ"
    elif prev_pts is not None and pts != prev_pts:
        diff = int(pts) - int(prev_pts)
        marker = f"  <-- DELTA: {'+' if diff > 0 else ''}{diff}"
    else:
        marker = ""
    
    print(f"{fn:<45} {str(pts) if pts is not None else 'N/A':>10}{marker}")
    if pts is not None:
        prev_pts = int(pts)
