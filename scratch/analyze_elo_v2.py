import os
import json
import glob
from datetime import datetime

def analyze_elo():
    our_nick = "ksotar"
    
    # 1. Gather our rating history from snapshots
    snaps = sorted(glob.glob('arena/snapshots/arena_*.json'))
    our_rating_history = [] # list of (dt, rating)
    for sf in snaps:
        with open(sf, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                ts_str = os.path.basename(sf).replace('arena_', '').replace('.json', '')
                dt = datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
                for p in data.get('players', []):
                    if p.get('profileState', {}).get('nickname') == our_nick:
                        our_rating_history.append((dt, int(p.get('rating', 0))))
            except: continue
    
    our_rating_history.sort()
    
    # 2. Gather all battles
    data_points = []
    player_dirs = [d for d in os.listdir('battle_analytics') if os.path.isdir(os.path.join('battle_analytics', d)) and not d.startswith('__') and d != 'snapshots']
    
    for player in player_dirs:
        for bf in glob.glob(os.path.join('battle_analytics', player, "battle_*.json")):
            with open(bf, 'r', encoding='utf-8') as f:
                try:
                    b = json.load(f)
                    ft = b.get('fightTime', '')
                    dt = datetime.strptime(ft.split('.')[0], "%d/%m/%Y_%H:%M:%S")
                    opp_r = int(b.get('opponentRating', 0))
                    delta = int(b.get('ourRatingDelta', 0))
                    
                    # Find our rating at this time
                    # We can use the closest snapshot, but even better:
                    # if we have many battles, we can see the delta sequence.
                    # For now, let's use the closest snapshot before battle.
                    our_r = None
                    for s_dt, r in reversed(our_rating_history):
                        if s_dt <= dt:
                            our_r = r
                            break
                    
                    if our_r:
                        diff = our_r - opp_r
                        data_points.append({
                            'diff': diff,
                            'delta': delta,
                            'win': delta > 0
                        })
                except: continue

    if not data_points:
        print("No data points found.")
        return

    # 3. Print table
    print("Rating Analysis (ELO-like):")
    print("| Diff (Our-Opp) | Win Delta | Loss Delta | Count |")
    print("|----------------|-----------|------------|-------|")
    
    grouped = {} # diff -> {win_deltas: set, loss_deltas: set, count: int}
    for p in data_points:
        # Round diff to nearest 10 or 50 to see patterns? 
        # Actually ELO usually depends on exact diff.
        # But games often use tiers.
        diff = p['diff']
        if diff not in grouped:
            grouped[diff] = {'win': set(), 'loss': set(), 'count': 0}
        if p['win']: grouped[diff]['win'].add(p['delta'])
        else: grouped[diff]['loss'].add(p['delta'])
        grouped[diff]['count'] += 1
        
    for d in sorted(grouped.keys()):
        w = ",".join(map(str, sorted(grouped[d]['win']))) or "-"
        l = ",".join(map(str, sorted(grouped[d]['loss']))) or "-"
        print(f"| {d:>14} | {w:>9} | {l:>10} | {grouped[d]['count']:>5} |")

if __name__ == '__main__':
    analyze_elo()
