import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_str = """            player_units = []
            target_units_data = e_u_data if ksotar_is_attack else p_u_data
            for slot in target_units_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()"""

new_str = """            player_units = []
            target_units_data = p_u_data if ksotar_is_attack else e_u_data
            for slot in target_units_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            enemy_units = []
            enemy_units_data = e_u_data if ksotar_is_attack else p_u_data
            for slot in enemy_units_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()"""

if old_str in text:
    text = text.replace(old_str, new_str)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed enemy_units for ksotar")
else:
    print("Not found ksotar enemy_units")

# And for normal players:
old_str_normal = """            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()

            battles.append({"""

new_str_normal = """            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()

            battles.append({"""

if old_str_normal in text:
    text = text.replace(old_str_normal, new_str_normal)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed enemy_units for normal")
else:
    print("Not found normal enemy_units")
