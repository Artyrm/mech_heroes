import json
import os

SNAPSHOTS_DIR = 'snapshots'

def analyze_players():
    f_start = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_16-16.json')
    f_end = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
    
    with open(f_start, 'r') as f: d1 = json.load(f)['pts']
    with open(f_end, 'r') as f: d2 = json.load(f)['pts']
    
    players = {
        "371651": "Димарик",
        "361914": "Александр (Gen)",
        "74509": "Александр (Sol)"
    }
    
    print(f"{'Игрок':<18} | {'Было':<10} | {'Стало':<10} | {'Прирост':<10}")
    print("-" * 55)
    for uid, name in players.items():
        v1 = d1.get(uid, 0)
        v2 = d2.get(uid, 0)
        print(f"{name:<18} | {v1:<10} | {v2:<10} | {v2-v1:<10}")

if __name__ == "__main__":
    analyze_players()
