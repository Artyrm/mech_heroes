import os
import json
import glob
from datetime import datetime

def analyze_elo():
    # 1. Gather all battles chronologically
    all_battles = []
    player_dirs = [d for d in os.listdir('battle_analytics') if os.path.isdir(os.path.join('battle_analytics', d)) and not d.startswith('__') and d != 'snapshots']
    
    for player in player_dirs:
        for bf in glob.glob(os.path.join('battle_analytics', player, "battle_*.json")):
            with open(bf, 'r', encoding='utf-8') as f:
                b = json.load(f)
                ft = b.get('fightTime', '')
                try:
                    dt = datetime.strptime(ft.split('.')[0], "%d/%m/%Y_%H:%M:%S")
                except:
                    continue
                all_battles.append({
                    'dt': dt,
                    'opp_rating': int(b.get('opponentRating', 0)),
                    'delta': int(b.get('ourRatingDelta', 0)),
                    'nick': b.get('nick', '')
                })
    
    all_battles.sort(key=lambda x: x['dt'])
    
    # 2. Find our rating from snapshots to anchor the timeline
    snaps = sorted(glob.glob('arena/snapshots/arena_*.json'))
    our_uid = None
    # Try to find our UID from .env or config if possible, or just look for 'ksotar'
    # Actually, we can just find which player has the most folders in battle_analytics? 
    # No, battle_analytics has folders of OPPONENTS.
    # The current_init_dump.json probably has our info.
    our_nick = "Quack" # Just a guess based on the logs, let's verify
    if os.path.exists('current_init_dump.json'):
        with open('current_init_dump.json', 'r', encoding='utf-8') as f:
            init = json.load(f)
            our_nick = init.get('data', {}).get('userState', {}).get('profile', {}).get('nickname', '')
            print(f"DEBUG: Our nick identified as {our_nick}")

    our_rating_history = {} # dt -> rating
    for sf in snaps:
        with open(sf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data.get('players', []):
                if p.get('profileState', {}).get('nickname') == our_nick:
                    ts_str = os.path.basename(sf).replace('arena_', '').replace('.json', '')
                    dt = datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
                    our_rating_history[dt] = int(p.get('rating', 0))

    if not our_rating_history:
        print("ERROR: Could not find our rating in snapshots.")
        return

    # 3. Correlate battles with rating
    data_points = []
    for b in all_battles:
        # Find the closest snapshot BEFORE the battle
        closest_dt = None
        for s_dt in sorted(our_rating_history.keys()):
            if s_dt < b['dt']:
                closest_dt = s_dt
            else:
                break
        
        if closest_dt:
            our_r = our_rating_history[closest_dt]
            # Since rating might have changed between snapshot and battle, we can't be 100% sure
            # But if there are many points, we can find a pattern.
            diff = our_r - b['opp_rating']
            data_points.append({
                'diff': diff,
                'delta': b['delta'],
                'our_r': our_r,
                'opp_r': b['opp_rating']
            })

    # 4. Group by diff and delta to find a table
    # Formula: Delta = K * (S - E) where E = 1 / (1 + 10^((opp - our)/400))
    # Or simpler game logic
    print("| Diff (Our - Opp) | Delta (Win/Loss) | Count |")
    print("|------------------|------------------|-------|")
    
    # Sort and group
    patterns = {}
    for p in data_points:
        key = (p['diff'], p['delta'])
        patterns[key] = patterns.get(key, 0) + 1
    
    for k in sorted(patterns.keys()):
        print(f"| {k[0]:>16} | {k[1]:>16} | {patterns[k]:>5} |")

if __name__ == '__main__':
    analyze_elo()
