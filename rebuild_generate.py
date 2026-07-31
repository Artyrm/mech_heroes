with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's completely rewrite the generate_dossiers method from `def generate_dossiers` to the end of the file
start_pos = text.find('def generate_dossiers(player_timelines):')
if start_pos == -1:
    print("Could not find generate_dossiers")
else:
    print("Found generate_dossiers at index:", start_pos)

# Let's inspect what follows after generate_dossiers
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_generate_dossiers = '''def generate_dossiers(player_timelines):
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    all_nicks = set(player_timelines.keys())
    for uid_str, nick in known_users.items():
        all_nicks.add(nick)
        
    for nick in all_nicks:
        battles = player_timelines.get(nick, [])
        if nick == 'ksotar':
            battles = all_ksotar_battles
            
        compositions = {}
        for b in battles:
            u = b.get('units')
            if not u: continue
            if u not in compositions:
                compositions[u] = {'wins': 0, 'losses': 0}
            if b['is_win']: compositions[u]['wins'] += 1
            else: compositions[u]['losses'] += 1
            
        sorted_comps = sorted(compositions.items(), key=lambda x: (x[1]['wins'] + x[1]['losses']), reverse=True)
        
        tactical_html = ''
        if nick != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'
            if not sorted_comps:
                tactical_html += '<div style="color:#8b949e;padding:10px">Нет данных о составах</div>'
            for units, res in sorted_comps:
                total = res['wins'] + res['losses']
                wr = (res['wins'] / total) * 100
                color = '#3fb950' if wr >= 60 else ('#f85149' if wr <= 40 else '#f2cc60')
                units_str = ", ".join(units)
                tactical_html += f\'\'\'
                <div class="comp-box">
                    <div class="comp-units">{units_str}</div>
                    <div class="comp-stats">Боёв: <b>{total}</b> | Винрейт: <span style="color:{color};font-weight:bold">{wr:.1f}%</span> ({res['wins']}В / {res['losses']}П)</div>
                </div>\'\'\'
            tactical_html += '</div>'

        table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"
        
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
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\\">{opponent}</td><td style=\\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\\">{opp_clan}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\\">{my_units_abbr}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"
                else:
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\\" title=\\"{ ', '.join(b.get('units', [])) }\\">{my_units_abbr}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\" title=\\"{ ', '.join(b.get('enemy_units', [])) }\\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"
        else:
            col_span = 8 if nick == 'ksotar' else 6
            rows = f"<tr><td colspan=\\"{col_span}\\" style=\\"text-align:center;color:#8b949e;padding:20px\\">Бои не найдены</td></tr>"
            
        target_dir = os.path.join(ANALYTICS_DIR, nick.strip())
        os.makedirs(target_dir, exist_ok=True)
        
        html = f\'\'\'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>История: {nick}</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet">
        <style>
            body{{background:#0d1117;color:#c9d1d9;font-family:'Inter',sans-serif;margin:20px;font-size:0.9rem}}
            .container{{max-width:1000px;margin:0 auto}}
            h1{{font-family:'Orbitron';color:#fff;text-align:center;font-size:1.8rem;margin-bottom:10px}}
            h2{{font-family:'Orbitron';font-size:1.1rem;color:#8b949e;border-bottom:1px solid #30363d;padding-bottom:5px;margin-top:20px}}
            .back-link{{color:#58a6ff;text-decoration:none;display:inline-block;margin-bottom:20px;font-size:0.85rem}}
            table{{width:100%;border-collapse:collapse;background:#161b22;border-radius:8px;overflow:hidden;margin-top:20px}}
            th{{background:#21262d;padding:12px;text-align:left;font-size:0.7rem;text-transform:uppercase;color:#888;letter-spacing:1px}}
            td{{padding:12px;border-bottom:1px solid #30363d}}
            tr:hover{{background:#1c2128}}
            .comp-box {{ border-bottom: 1px solid #30363d; padding: 8px 0; }}
            .comp-box:last-child {{ border-bottom: none; }}
            .comp-units {{ color: #58a6ff; font-family: 'Roboto Mono'; font-size: 0.8rem; font-weight: bold; }}
            .comp-stats {{ font-size: 0.75rem; color: #8b949e; margin-top: 3px; }}
            .type-attack {{ color: #f2cc60; font-weight: bold; }}
            .type-defense {{ color: #58a6ff; font-weight: bold; }}
            .res-win {{ color: #3fb950; font-weight: bold; }}
            .res-loss {{ color: #f85149; font-weight: bold; }}
        </style></head>
        <body><div class="container"><a href="../personal.html" class="back-link">← К списку игроков</a>
        <h1>ДОСЬЕ: {nick}</h1>
        {tactical_html}
        <table><thead>{table_headers}</thead><tbody>{rows}</tbody></table>
        </div></body></html>\'\'\'
        
        with open(os.path.join(target_dir, 'summary.html'), 'w', encoding='utf-8') as f: f.write(html)
'''

# Find line index where def generate_dossiers starts
dossier_line_idx = -1
for idx, line in enumerate(lines):
    if line.startswith('def generate_dossiers'):
        dossier_line_idx = idx
        break

if dossier_line_idx != -1:
    lines[dossier_line_idx:] = [new_generate_dossiers + "\n"]
    with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully rebuilt generate_dossiers cleanly!")
else:
    print("Could not find generate_dossiers in lines")
