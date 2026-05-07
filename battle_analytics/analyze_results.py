import os
import json
from datetime import datetime

# Smart path detection
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DUMPS_DIR = os.path.join(ROOT_DIR, 'init_dumps')
ANALYTICS_DIR = SCRIPT_DIR

def find_battles(nick):
    results = []
    # Check all files in dumps
    for f in os.listdir(DUMPS_DIR):
        if not f.endswith('.json'): continue
        path = os.path.join(DUMPS_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            history = data.get('data', {}).get('userState', {}).get('arena', {}).get('battlesHistory', [])
            for b in history:
                if b.get('nick') == nick:
                    results.append(b)
        except:
            continue
    return results

def get_unit_summary(units):
    res = []
    for slot, u in sorted(units.items(), key=lambda x: int(x[0])):
        state = u.get('state', {})
        res.append(f"{state.get('defId')} ({state.get('level')}lvl, {state.get('stars')}*)")
    return ", ".join(res)

def compare_battles(b1, b2):
    # b1 is old, b2 is new
    print(f"--- COMPARISON FOR {b2.get('nick')} ---")
    print(f"Old: {b1.get('fightTime')} (Delta: {b1.get('ourRatingDelta')})")
    print(f"New: {b2.get('fightTime')} (Delta: {b2.get('ourRatingDelta')})")
    
    e1 = b1.get('statistics', {}).get('enemy', {})
    e2 = b2.get('statistics', {}).get('enemy', {})
    
    g1 = e1.get('general', {})
    g2 = e2.get('general', {})
    
    if g1.get('defId') != g2.get('defId') or g1.get('level') != g2.get('level'):
        print(f"General changed: {g1.get('defId')} (L{g1.get('level')}) -> {g2.get('defId')} (L{g2.get('level')})")
    else:
        print(f"General same: {g2.get('defId')} (L{g2.get('level')})")
        
    u1 = get_unit_summary(e1.get('units', {}))
    u2 = get_unit_summary(e2.get('units', {}))
    
    if u1 != u2:
        print(f"Units changed!")
        print(f"  WAS: {u1}")
        print(f"  NOW: {u2}")
    else:
        print(f"Units same: {u2}")

def analyze_player(nick):
    battles = find_battles(nick)
    # Sort by time
    # fightTime format: "05/05/2026_13:03:38.1060"
    def parse_time(t):
        try: return datetime.strptime(t.split('.')[0], '%d/%m/%Y_%H:%M:%S')
        except: return datetime.min
    
    from datetime import datetime
    battles.sort(key=lambda x: parse_time(x.get('fightTime')))
    
    if not battles:
        print(f"No battles found for {nick}")
        return
        
    print(f"\n--- TREND FOR {nick} ({len(battles)} battles) ---")
    for b in battles:
        delta = int(b.get('ourRatingDelta', 0))
        res = "WIN" if delta > 0 else "LOSE"
        print(f"{b.get('fightTime')}: {res} ({delta})")

if __name__ == "__main__":
    # 1. LordDragon
    dragon_battles = find_battles('LordDragon')
    if len(dragon_battles) >= 2:
        from datetime import datetime
        def parse_time(t):
            try: return datetime.strptime(t.split('.')[0], '%d/%m/%Y_%H:%M:%S')
            except: return datetime.min
        dragon_battles.sort(key=lambda x: parse_time(x.get('fightTime')))
        compare_battles(dragon_battles[0], dragon_battles[-1])
    elif len(dragon_battles) == 1:
        print("Only one battle with LordDragon found.")
    
    # 2. Strel
    analyze_player('Strel')
    
    # 3. Hobbit
    analyze_player('Хоббит')
