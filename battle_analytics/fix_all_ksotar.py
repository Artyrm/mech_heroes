# -*- coding: utf-8 -*-
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's fix how all_ksotar_battles is collected and defined at the beginning of generate_dossiers
old_snippet = '''def generate_dossiers(player_timelines):
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    all_nicks = set(player_timelines.keys())
    for uid_str, nick in known_users.items():
        all_nicks.add(nick)
        
    for nick in all_nicks:
        battles = player_timelines.get(nick, [])
        if nick.strip() == 'ksotar':
            battles = all_ksotar_battles'''

new_snippet = '''def generate_dossiers(player_timelines):
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    
    # Собираем все бои против ksotar со всех папок противников
    all_ksotar_battles = []
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    for p_nick in player_keys:
        p_dir = os.path.join(ANALYTICS_DIR, p_nick)
        for bf in glob.glob(os.path.join(p_dir, "battle_*.json")):
            b_data = load_json(bf)
            dt = parse_fight_time(b_data.get('fightTime'))
            delta = int(b_data.get('ourRatingDelta', 0))
            sd = b_data.get('statistics', {})
            
            p_u_data = sd.get('player', {}).get('units', {})
            e_u_data = sd.get('enemy', {}).get('units', {})
            
            p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
            e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
            
            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            
            p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
            e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
            
            p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
            e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
            
            is_attack = p_min < e_min
            opponent = e_name if is_attack else p_name
            opponent_clan = e_clan if is_attack else p_clan
            
            # Инвертируем для ksotar: если противник выиграл (delta > 0), для ksotar это поражение
            ksotar_is_win = delta < 0
            ksotar_is_attack = not is_attack
            ksotar_delta = -delta
            
            player_units = []
            for slot in p_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()
            
            all_ksotar_battles.append({
                'dt': dt,
                'is_win': ksotar_is_win,
                'is_attack': ksotar_is_attack,
                'delta': ksotar_delta,
                'file_html': f"../{p_nick}/" + os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'opponent_clan': opponent_clan or '-'
            })
    all_ksotar_battles.sort(key=lambda x: x['dt'])

    all_nicks = set(player_timelines.keys())
    for uid_str, nick in known_users.items():
        all_nicks.add(nick)
    all_nicks.add('ksotar')
        
    for nick in all_nicks:
        if nick.strip() == 'ksotar':
            battles = all_ksotar_battles
        else:
            battles = player_timelines.get(nick, [])'''

if old_snippet in text:
    text = text.replace(old_snippet, new_snippet)
    with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully added all_ksotar_battles collection in generate_dossiers!")
else:
    print("old_snippet not found, let's check exact text")
