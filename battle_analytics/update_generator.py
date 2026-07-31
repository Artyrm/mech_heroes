with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Нам нужно переписать генерацию HTML-таблиц в generate_dossiers
# Заменим блок формирования rows в generate_dossiers

new_dossier_logic = '''
        rows = ""
        if battles:
            for b in reversed(battles):
                dt_str = (b['dt'] + timedelta(hours=3)).strftime('%d.%m %H:%M')
                type_str = 'АТАКА' if b['is_attack'] else 'ЗАЩИТА'
                type_class = 'type-attack' if b['is_attack'] else 'type-defense'
                res_str = 'ПОБЕДА' if b['is_win'] else 'ПОРАЖЕНИЕ'
                res_class = 'res-win' if b['is_win'] else 'res-loss'
                delta_val = b['delta']
                delta_str = f"+{delta_val}" if delta_val > 0 else str(delta_val)
                delta_color = '#3fb950' if delta_val > 0 else ('#f85149' if delta_val < 0 else '#8b949e')
                
                my_units_abbr = abbrev_units(b.get('units', []))
                enemy_units_abbr = abbrev_units(b.get('enemy_units', []))
                
                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    p_folder = b.get('p_nick', '')
                    file_html = f"../{p_folder}/{b.get('file_html', '#')}" if p_folder else f"../{b.get('file_html', '#')}"
                    
                    rows += f'''<tr onclick="window.location='{file_html}'" style="cursor:pointer" title="Нажмите, чтобы открыть подробную карточку боя">
                        <td>{dt_str}</td>
                        <td><span class="{type_class}">{type_str}</span></td>
                        <td style="color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600">{opponent}</td>
                        <td style="font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e">{my_units_abbr}</td>
                        <td><span class="{res_class}">{res_str}</span></td>
                        <td style="text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold">{delta_str}</td>
                    </tr>'''
                else:
                    file_html = b.get('file_html', '#')
                    rows += f'''<tr onclick="window.location='{file_html}'" style="cursor:pointer" title="Нажмите, чтобы открыть подробную карточку боя">
                        <td>{dt_str}</td>
                        <td><span class="{type_class}">{type_str}</span></td>
                        <td style="font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff" title="{', '.join(b.get('units', []))}">{my_units_abbr}</td>
                        <td style="font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e" title="{', '.join(b.get('enemy_units', []))}">{enemy_units_abbr}</td>
                        <td><span class="{res_class}">{res_str}</span></td>
                        <td style="text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold">{delta_str}</td>
                    </tr>'''
        else:
            col_span = 6 if nick == 'ksotar' else 6
            rows = f'<tr><td colspan="{col_span}" style="text-align:center;color:#8b949e;padding:20px">Бои не найдены</td></tr>'
'''

# Также обновим заголовки таблиц в генерации HTML:
# Для ksotar: <th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th>
# Для остальных: <th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th>

table_headers_logic = '''
        table_headers = '''
        if nick == 'ksotar':
            table_headers = '<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th></tr>'
        else:
            table_headers = '<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th></tr>'
'''

print('Update script template created')
