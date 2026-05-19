import os
import json
import glob
from datetime import datetime

def analyze_elo():
    our_nick = "ksotar"
    snaps = sorted(glob.glob('arena/snapshots/arena_*.json'))
    our_rating_history = []
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

    data_points = []
    player_dirs = [d for d in os.listdir('battle_analytics') if os.path.isdir(os.path.join('battle_analytics', d)) and not d.startswith('__') and d != 'snapshots']
    
    for player in player_dirs:
        for bf in glob.glob(os.path.join('battle_analytics', player, "battle_*.json")):
            with open(bf, 'r', encoding='utf-8') as f:
                try:
                    b = json.load(f)
                    dt = datetime.strptime(b.get('fightTime', '').split('.')[0], "%d/%m/%Y_%H:%M:%S")
                    opp_r = int(b.get('opponentRating', 0))
                    delta = int(b.get('ourRatingDelta', 0))
                    our_r = None
                    for s_dt, r in reversed(our_rating_history):
                        if s_dt <= dt:
                            our_r = r
                            break
                    if our_r:
                        data_points.append({'diff': opp_r - our_r, 'delta': delta, 'win': delta > 0})
                except: continue

    print("| Opp - Our | Win Delta | Loss Delta | Count |")
    print("|-----------|-----------|------------|-------|")
    
    grouped = {} 
    for p in data_points:
        d = p['diff']
        if d not in grouped: grouped[d] = {'win': [], 'loss': [], 'count': 0}
        if p['win']: grouped[d]['win'].append(p['delta'])
        else: grouped[d]['loss'].append(p['delta'])
        grouped[d]['count'] += 1
        
    for d in sorted(grouped.keys()):
        if grouped[d]['count'] < 1: continue
        avg_w = round(sum(grouped[d]['win'])/len(grouped[d]['win']), 1) if grouped[d]['win'] else "-"
        avg_l = round(sum(grouped[d]['loss'])/len(grouped[d]['loss']), 1) if grouped[d]['loss'] else "-"
        print(f"| {d:>9} | {avg_w:>9} | {avg_l:>10} | {grouped[d]['count']:>5} |")

if __name__ == '__main__':
    analyze_elo()
