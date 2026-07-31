with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's fix enemy_units definition in all_ksotar_battles collection loop
old_snippet = '''            enemy_units = []
            target_enemy_data = p_u_data if ksotar_is_attack else e_u_data
            for slot in target_enemy_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()'''

if old_snippet not in text:
    # Let's see what is there
    print("Old snippet not found directly")

# Let's replace the whole all_ksotar_battles loop cleanly
start_pos = text.find('all_ksotar_battles = []')
if start_pos != -1:
    print("Found all_ksotar_battles collection")

with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'enemy_units = []' in line:
        print(f"Found enemy_units at line {i+1}")

