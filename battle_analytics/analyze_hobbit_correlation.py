import json
import os
from datetime import datetime

# Path is now local since the script is in the analytics folder
ANALYTICS_DIR = os.path.join(os.path.dirname(__file__), 'Хоббит')

def get_team_str(units):
    res = []
    # Sort by slot number
    for slot in sorted(units.keys(), key=lambda x: int(x)):
        u = units[slot]
        state = u.get('state', {})
        res.append(f"{state.get('defId')}({state.get('stars')}*)")
    return " | ".join(res)

def analyze():
    files = [f for f in os.listdir(ANALYTICS_DIR) if f.endswith('.json')]
    data = []
    
    for f in files:
        with open(os.path.join(ANALYTICS_DIR, f), 'r', encoding='utf-8') as file:
            b = json.load(file)
            stats = b.get('statistics', {})
            p_units = stats.get('player', {}).get('units', {})
            e_units = stats.get('enemy', {}).get('units', {})
            
            delta = int(b.get('ourRatingDelta', 0))
            result = "WIN" if delta > 0 else "LOSE"
            
            data.append({
                'time': b.get('fightTime'),
                'p_team': get_team_str(p_units),
                'e_team': get_team_str(e_units),
                'res': result,
                'delta': delta
            })
            
    # Sort by time
    def parse_time(t):
        try: return datetime.strptime(t.split('.')[0], '%d/%m/%Y_%H:%M:%S')
        except: return datetime.min
        
    data.sort(key=lambda x: parse_time(x['time']))
    
    print(f"{'Время':<20} | {'Твой состав':<60} | {'Состав Хоббита':<60} | {'Рез'}")
    print("-" * 150)
    
    last_p = ""
    last_e = ""
    
    for b in data:
        p_change = "*" if b['p_team'] != last_p else " "
        e_change = "*" if b['e_team'] != last_e else " "
        
        # Only print if something changed or it's the first record to keep it clean
        if b['p_team'] != last_p or b['e_team'] != last_e:
            print(f"{b['time'][:16]:<20} | {b['p_team']:<60} | {b['e_team']:<60} | {b['res']} ({b['delta']})")
        
        last_p = b['p_team']
        last_e = b['e_team']

if __name__ == "__main__":
    analyze()
