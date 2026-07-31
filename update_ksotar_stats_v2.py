with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = '''            all_ksotar_battles.append({
                'dt': dt,
                'is_win': ksotar_is_win,
                'is_attack': ksotar_is_attack,
                'delta': ksotar_delta,
                'file_html': '../' + os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'opponent': opponent
            })'''

new_block = '''            p_clan_info = sd.get('player', {}).get('clan', {})
            e_clan_info = sd.get('enemy', {}).get('clan', {})
            p_clan_tag = p_clan_info.get('clanTag') or p_clan_info.get('clanName') if isinstance(p_clan_info, dict) else str(p_clan_info)
            e_clan_tag = e_clan_info.get('clanTag') or e_clan_info.get('clanName') if isinstance(e_clan_info, dict) else str(e_clan_info)
            opp_clan = p_clan_tag if is_attack else e_clan_tag
            if not opp_clan or opp_clan == '-':
                opp_clan = '-'

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

if old_block in text:
    text = text.replace(old_block, new_block)
    print("Successfully replaced ksotar append block!")
else:
    print("Old block not found!")

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)
