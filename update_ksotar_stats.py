import re

with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect how all_ksotar_battles is built in generate_personal_stats.py
# We will rewrite the loop that collects all_ksotar_battles and generate_dossiers for ksotar

old_ksotar_collect = '''            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'ksotar')
            opponent = p_name if ksotar_is_attack else e_name
            if opponent == 'ksotar' or not opponent:
                opponent = p_nick
                
            player_units = []
            target_units_data = e_u_data if ksotar_is_attack else p_u_data
            for slot in target_units_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            enemy_units = []
            target_enemy_data = p_u_data if ksotar_is_attack else e_u_data
            for slot in target_enemy_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()
            
            all_ksotar_battles.append({
                'dt': dt,
                'is_win': ksotar_is_win,
                'is_attack': ksotar_is_attack,
                'delta': ksotar_delta,
                'file_html': '../' + os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'opponent': opponent
            })'''

new_ksotar_collect = '''            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'ksotar')
            opponent = p_name if ksotar_is_attack else e_name
            if opponent == 'ksotar' or not opponent:
                opponent = p_nick
                
            # Клан противника
            p_clan_info = sd.get('player', {}).get('clan', {})
            e_clan_info = sd.get('enemy', {}).get('clan', {})
            p_clan_tag = p_clan_info.get('clanTag') or p_clan_info.get('clanName') if isinstance(p_clan_info, dict) else str(p_clan_info)
            e_clan_tag = e_clan_info.get('clanTag') or e_clan_info.get('clanName') if isinstance(e_clan_info, dict) else str(e_clan_info)
            opp_clan = p_clan_tag if ksotar_is_attack else e_clan_tag
            if not opp_clan or opp_clan == '-':
                # Попробуем из реестра или профилей
                opp_clan = '-'
                
            player_units = []
            target_units_data = e_u_data if ksotar_is_attack else p_u_data
            for slot in target_units_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            enemy_units = []
            target_enemy_data = p_u_data if ksotar_is_attack else e_u_data
            for slot in target_enemy_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()
            
            rel_file_html = f"../{p_nick}/{os.path.basename(bf).replace('.json', '.html')}"
            
            all_ksotar_battles.append({
                'dt': dt,
                'is_win': ksotar_is_win,
                'is_attack': ksotar_is_attack,
                'delta': ksotar_delta,
                'file_html': rel_file_html,
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'opponent_clan': opp_clan
            })'''

if old_ksotar_collect in text:
    text = text.replace(old_ksotar_collect, new_ksotar_collect)
    print("Replaced ksotar collect block successfully!")
else:
    print("Could not find old_ksotar_collect block")

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)
