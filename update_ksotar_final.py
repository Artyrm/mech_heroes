with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Мы заменим строки 303 и 317-321
for idx, line in enumerate(lines):
    if '<th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th>' in line:
        lines[idx] = '                table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Состав отряда</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"\n'
    
    if 'if nick == \'ksotar\':' in line and 'opponent = b.get(\'opponent\', \'-\')' in lines[idx+1]:
        # Заменим этот блок на правильный рендеринг строки для ksotar с кланом и правильным file_html
        lines[idx] = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\\">{opponent}</td><td style=\\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\\">{opp_clan}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{my_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"\\n'''
        # Очистим следующие 4 строки старого кода, чтобы не было дублирования
        for j in range(1, 5):
            lines[idx+j] = ''

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully updated generate_personal_stats.py for ksotar table and links!")
