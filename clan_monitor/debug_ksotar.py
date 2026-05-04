import os, json, re
from datetime import datetime, timezone, timedelta

SNAPSHOTS_DIR = "snapshots"
UID = "227408"  # ksotar

files = sorted([f for f in os.listdir(SNAPSHOTS_DIR) if f.startswith("points_utc_")])
sd = []
for fn in files:
    m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})', fn)
    if not m: continue
    dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
    with open(os.path.join(SNAPSHOTS_DIR, fn), encoding='utf-8') as f:
        d = json.load(f)
    pts_map = d.get("pts", d)
    pts_val = pts_map.get(UID)
    if pts_val is not None:
        sd.append({"time": dt, "pts": int(pts_val), "file": fn})

# Group by UTC day
days = {}
for e in sd:
    dk = e["time"].strftime("%Y-%m-%d")
    days.setdefault(dk, []).append(e)

print(f"{'День':<12} {'Снэпшоты':<10} {'Первый':>8} {'Последний':>10} {'Алг.СТАРЫЙ':>12} {'Алг.НОВЫЙ':>11}")
print("-" * 70)

prev_last = 0
for dk in sorted(days.keys()):
    entries = days[dk]
    vals = [e["pts"] for e in entries]

    # СТАРЫЙ: только последний снэпшот
    final = vals[-1]
    if final < prev_last:
        old_growth = final
    else:
        old_growth = max(0, final - prev_last)

    # НОВЫЙ: все снэпшоты
    ref = prev_last
    new_growth = 0
    for v in vals:
        if v == 0: continue
        if v < ref:
            new_growth += v
        else:
            new_growth += (v - ref)
        ref = v

    marker = " <-- РАЗНИЦА!" if abs(old_growth - new_growth) > 100 else ""
    print(f"{dk:<12} {len(vals):<10} {vals[0]:>8} {vals[-1]:>10} {old_growth:>12} {new_growth:>11}{marker}")

    prev_last = vals[-1]
