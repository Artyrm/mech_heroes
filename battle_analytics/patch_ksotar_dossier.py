import os
import re

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Сначала вставим сбор боев ksotar в начало generate_dossiers
pos_dossiers = text.find('def generate_dossiers(player_timelines):')
pos_dossiers_body = text.find('    all_nicks = set(player_timelines.keys())', pos_dossiers)

ksotar_aggregation = """
    # Собираем все бои против ksotar со всех папок противников
    all_ksotar_battles = []
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    for p_nick in player_keys:
        p_dir = os.path.join(ANALYTICS_DIR, p_nick)
        import glob
        for bf in glob.glob(os.path.join(p_dir, "battle_*.json")):
            b_data = load_json(bf)
            dt = parse_fight_time(b_data.get('fightTime'))
            delta = int(b_data.get('ourRatingDelta', 0))
            sd = b_data.get('statistics', {})
            
            p_u_data = sd.get('player', {}).get('units', {})
            e_u_data = sd.get('enemy', {}).get('units', {})
            
            p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
            e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
            is_attack = p_min < e_min
            
            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            opponent = e_name if is_attack else p_name
            if opponent == 'ksotar' or not opponent:
                opponent = p_name if p_name != 'ksotar' else p_nick
                
            p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
            e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
            p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
            e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
            opponent_clan = e_clan if is_attack else p_clan
            if not opponent_clan or opponent_clan == '-':
                opponent_clan = e_clan if opponent == e_name else p_clan
            
            ksotar_is_attack = not is_attack
            ksotar_is_win = delta <= 0
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
"""

if "all_ksotar_battles = []" not in text:
    text = text[:pos_dossiers_body] + ksotar_aggregation + text[pos_dossiers_body:]


# 2. Добавляем ksotar в all_nicks
if "all_nicks.add('ksotar')" not in text:
    text = text.replace("for uid_str, nick in known_users.items():\n        all_nicks.add(nick)", "for uid_str, nick in known_users.items():\n        all_nicks.add(nick)\n    all_nicks.add('ksotar')")

# 3. Меняем player_timelines.get на all_ksotar_battles
old_battles = "battles = player_timelines.get(nick, [])"
new_battles = """if nick.strip() == 'ksotar':
            battles = all_ksotar_battles
        else:
            battles = player_timelines.get(nick, [])"""
text = text.replace(old_battles, new_battles)

# 4. Убираем тактический блок для ksotar
old_tactical = """        tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'"""
new_tactical = """        tactical_html = ''
        if nick.strip() != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'"""
text = text.replace(old_tactical, new_tactical)

# 5. Меняем table_headers
old_headers = """        table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>\""""
new_headers = """        if nick.strip() == 'ksotar':
            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"
        else:
            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>\""""
text = text.replace(old_headers, new_headers)

# 6. Вспомогательная функция аббревиатур (если нет)
if "def abbrev_units" not in text:
    text = text.replace("def generate_dossiers(player_timelines):", """def abbrev_units(units):
    if not units: return '-'
    res = []
    for u in units:
        res.append(u[:2].upper() if len(u) >= 2 else u.upper())
    return ", ".join(res)

def generate_dossiers(player_timelines):""")

# 7. Меняем rows
old_rows = """                rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\"><td>{(b['dt']+timedelta(hours=3)).strftime('%d.%m %H:%M')}</td><td>{'АТАКА' if b['is_attack'] else 'ЗАЩИТА'}</td><td>{'ПОБЕДА' if b['is_win'] else 'ПОРАЖЕНИЕ'}</td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{'#3fb950' if b['delta']>0 else ('#f85149' if b['delta']<0 else '#8b949e')}\\">{'+' if b['delta']>0 else ''}{b['delta']}</td></tr>" """
new_rows = """                dt_str = (b['dt']+timedelta(hours=3)).strftime('%d.%m %H:%M')
                type_str = 'АТАКА' if b['is_attack'] else 'ЗАЩИТА'
                type_class = 'type-attack' if b['is_attack'] else 'type-defense'
                res_str = 'ПОБЕДА' if b['is_win'] else 'ПОРАЖЕНИЕ'
                res_class = 'res-win' if b['is_win'] else 'res-loss'
                delta_val = b['delta']
                delta_str = f"+{delta_val}" if delta_val > 0 else str(delta_val)
                delta_color = '#3fb950' if delta_val > 0 else ('#f85149' if delta_val < 0 else '#8b949e')
                my_units_abbr = abbrev_units(b.get('units', []))
                enemy_units_abbr = abbrev_units(b.get('enemy_units', []))
                file_html = b.get('file_html', '#')

                if nick.strip() == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\\">{opponent}</td><td style=\\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\\">{opp_clan}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\\">{my_units_abbr}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"
                else:
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\\">{my_units_abbr}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>\""""
text = text.replace(old_rows, new_rows)

old_col_span = """        else:
            rows = '<tr><td colspan="4" style="text-align:center;color:#8b949e;padding:20px">Бои не найдены</td></tr>'"""
new_col_span = """        else:
            col_span = 8 if nick.strip() == 'ksotar' else 6
            rows = f"<tr><td colspan=\\"{col_span}\\" style=\\"text-align:center;color:#8b949e;padding:20px\\">Бои не найдены</td></tr>\""""
text = text.replace(old_col_span, new_col_span)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched ksotar dossier completely!")
