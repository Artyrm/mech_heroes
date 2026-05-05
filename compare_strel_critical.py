import json
import os

def get_battle_summary(path):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    stats = d.get('statistics', {})
    player = stats.get('player', {})
    enemy = stats.get('enemy', {})
    
    def get_units(side):
        res = {}
        for s, u in side.get('units', {}).items():
            state = u.get('state', {})
            res[s] = {
                'id': state.get('defId'),
                'lvl': state.get('level'),
                'stars': state.get('stars'),
                'dmg': u.get('statistics', {}).get('damageDone', '0')
            }
        return res

    return {
        'time': d.get('fightTime'),
        'p_gen': player.get('general', {}).get('defId'),
        'p_units': get_units(player),
        'e_gen': enemy.get('general', {}).get('defId'),
        'e_units': get_units(enemy)
    }

b1 = get_battle_summary('battle_analytics/Strel/battle_05-05-2026_04-00-08_7550.json') # WIN
b2 = get_battle_summary('battle_analytics/Strel/battle_05-05-2026_04-14-21_2970.json') # LOSE

print(f"WIN ({b1['time']}) vs LOSE ({b2['time']})")

if b1['p_gen'] != b2['p_gen']:
    print(f"OUR General changed: {b1['p_gen']} -> {b2['p_gen']}")

for s in b1['p_units']:
    u1, u2 = b1['p_units'][s], b2['p_units'].get(s, {})
    if u1['id'] != u2.get('id'):
        print(f"OUR Slot {s} changed: {u1['id']} -> {u2.get('id')}")

print("\n--- ENEMY (STREL) CHANGES ---")
if b1['e_gen'] != b2['e_gen']:
    print(f"ENEMY General changed: {b1['e_gen']} -> {b2['e_gen']}")

for s in b1['e_units']:
    u1, u2 = b1['e_units'][s], b2['e_units'].get(s, {})
    if u1['id'] != u2.get('id') or u1['stars'] != u2.get('stars'):
        print(f"ENEMY Slot {s} changed: {u1['id']}({u1['stars']}*) -> {u2.get('id')}({u2.get('stars')}*)")
    
    # Compare damage output
    d1 = float(u1['dmg'].replace(',', '.'))
    d2 = float(u2.get('dmg', '0').replace(',', '.'))
    if abs(d1 - d2) / (max(d1, d2) + 1) > 0.5:
        print(f"ENEMY Slot {s} ({u1['id']}) damage shift: {u1['dmg']} -> {u2.get('dmg', '0')}")
