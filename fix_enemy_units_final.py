with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('all_ksotar_battles = []')
end_idx = text.find("player_timelines['ksotar'] = all_ksotar_battles")

clean_ksotar_loop = '''all_ksotar_battles = []
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    for p_nick in player_keys:
        p_dir = os.path.join(ANALYTICS_DIR, p_nick)
        for bf in glob.glob(os.path.join(p_dir, 'battle_*.json')):
            b = load_json(bf)
            dt = parse_fight_time(b.get('fightTime'))
            delta = int(b.get('ourRatingDelta', 0))
            sd = b.get('statistics', {})
            p_u_data = sd.get('player', {}).get('units', {})
            e_u_data = sd.get('enemy', {}).get('units', {})
            
            p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
            e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
            is_attack = p_min < e_min
            
            ksotar_is_attack = is_attack
            ksotar_is_win = delta > 0
            ksotar_delta = delta
            
            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'ksotar')
            opponent = p_name if ksotar_is_attack else e_name
            if opponent == 'ksotar' or not opponent:
                opponent = p_nick
                
            p_clan_info = sd.get('player', {}).get('clan', {})
            e_clan_info = sd.get('enemy', {}).get('clan', {})
            p_clan_tag = p_clan_info.get('clanTag') or p_clan_info.get('clanName') if isinstance(p_clan_info, dict) else str(p_clan_info)
            e_clan_tag = e_clan_info.get('clanTag') or e_clan_info.get('clanName') if isinstance(e_clan_info, dict) else str(e_clan_info)
            opp_clan = p_clan_tag if is_attack else e_clan_tag
            if not opp_clan or opp_clan == '-':
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
            })
            
    all_ksotar_battles.sort(key=lambda x: x['dt'])
    all_ksotar_battles = all_ksotar_battles[-100:]
    player_timelines['ksotar'] = all_ksotar_battles'''

key_str = "player_timelines['ksotar'] = all_ksotar_battles"
text = text[:start_idx] + clean_ksotar_loop + text[end_idx + len(key_str):]

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully replaced all_ksotar_battles loop cleanly!")
