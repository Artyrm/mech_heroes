import json
import os
from datetime import datetime

def format_power(power_str):
    try:
        # Remove decimals and format with spaces
        val = int(float(power_str.replace(',', '.')))
        return f"{val:,}".replace(',', ' ')
    except:
        return power_str

def calculate_winrate(wins, loses):
    try:
        total = int(wins) + int(loses)
        if total == 0: return 0
        return round(int(wins) / total * 100, 2)
    except:
        return 0

def get_player_data(player):
    ps = player.get('profileState', {})
    cp = player.get('clanProfile', {})
    
    return {
        "id": player.get('userID'),
        "nick": ps.get('nickname', 'Unknown'),
        "rating": int(player.get('rating', 0)),
        "power": player.get('power', '0'),
        "wins": int(ps.get('winCount', 0)),
        "loses": int(ps.get('defeatCount', 0)),
        "winrate": calculate_winrate(ps.get('winCount', 0), ps.get('defeatCount', 0)),
        "clan": cp.get('clanName', ''),
        "clan_tag": cp.get('clanTag', ''),
        "clan_role": cp.get('playerRole', '')
    }

def compare_snapshots(t1_data, t2_data):
    """
    Compares t2 (newer) against t1 (older).
    Returns a list of player records with deltas.
    """
    p1 = {str(p['userID']): get_player_data(p) for p in t1_data['players']}
    p2 = {str(p['userID']): get_player_data(p) for p in t2_data['players']}
    
    # Current Top-50 list based on t2
    results = []
    
    # Sort t2 players by rating desc
    sorted_p2 = sorted(t2_data['players'], key=lambda x: int(x.get('rating', 0)), reverse=True)
    
    for rank, p in enumerate(sorted_p2, 1):
        uid = str(p['userID'])
        current = get_player_data(p)
        current['rank'] = rank
        
        if uid in p1:
            old = p1[uid]
            # Calculate deltas
            current['delta_rating'] = current['rating'] - old['rating']
            current['delta_wins'] = current['wins'] - old['wins']
            current['delta_loses'] = current['loses'] - old['loses']
            # Find old rank
            old_rank = -1
            sorted_p1_ids = [str(x['userID']) for x in sorted(t1_data['players'], key=lambda x: int(x.get('rating', 0)), reverse=True)]
            if uid in sorted_p1_ids:
                old_rank = sorted_p1_ids.index(uid) + 1
            
            if old_rank != -1:
                current['delta_rank'] = old_rank - rank # Positive means rank improved (smaller number)
            else:
                current['delta_rank'] = 0
            current['is_new'] = False
        else:
            current['delta_rating'] = 0
            current['delta_wins'] = 0
            current['delta_loses'] = 0
            current['delta_rank'] = 0
            current['is_new'] = True
            
        results.append(current)
        
    return results

if __name__ == "__main__":
    # Test logic
    import glob
    snaps = sorted(glob.glob("arena/snapshots/arena_*.json"))
    if len(snaps) >= 2:
        with open(snaps[0], 'r', encoding='utf-8') as f: t1 = json.load(f)
        with open(snaps[-1], 'r', encoding='utf-8') as f: t2 = json.load(f)
        diff = compare_snapshots(t1, t2)
        print(f"Compared {snaps[0]} vs {snaps[-1]}")
        print(f"Top player: {diff[0]['nick']} | Delta Rating: {diff[0]['delta_rating']}")
