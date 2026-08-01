with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect how player_timelines gets battles and where opponent_clan is stored
# In fetch_and_store_battles or wherever battles are extracted, opponent_clan might be in sd.get('enemy', {}).get('clan', {}).get('name', '-')
# Let's update get_player_battles_timeline to extract opponent_clan properly.

old_timeline_func = '''            p_name = sd.get('player', {}).get('name', nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            is_attack = p_min < e_min
            opponent = e_name if is_attack else p_name
            if opponent == nick:
                opponent = e_name if p_name == nick else p_name


            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()

            battles.append({
                'dt': dt, 
                'is_win': delta > 0, 
                'is_attack': is_attack, 
                'delta': delta, 
                'file_html': os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'p_nick': nick
            })'''

new_timeline_func = '''            p_name = sd.get('player', {}).get('name', nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            
            p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
            e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
            
            p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
            e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
            
            is_attack = p_min < e_min
            opponent = e_name if is_attack else p_name
            if opponent == nick:
                opponent = e_name if p_name == nick else p_name
                
            opponent_clan = e_clan if is_attack else p_clan
            if not opponent_clan or opponent_clan == '-':
                opponent_clan = e_clan if opponent == e_name else p_clan

            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()

            battles.append({
                'dt': dt, 
                'is_win': delta > 0, 
                'is_attack': is_attack, 
                'delta': delta, 
                'file_html': os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'opponent_clan': opponent_clan or '-',
                'p_nick': nick
            })'''

if old_timeline_func in text:
    text = text.replace(old_timeline_func, new_timeline_func)
    with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated get_player_battles_timeline with opponent_clan extraction!")
else:
    print("old_timeline_func marker not found")
