with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Исправим table_headers для ksotar: должно быть 7 колонок
old_headers_code = 'table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else'
new_headers_code = 'table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else'

if old_headers_code in text:
    text = text.replace(old_headers_code, new_headers_code)
    print("Updated table_headers for ksotar!")
else:
    print("old_headers_code not found")

# 2. Исправим генерацию строки для ksotar: должно быть 8 колонок (td) синхронно с шапкой
old_ksotar_row = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f'<tr onclick="window.location=\'{file_html}\'" style="cursor:pointer" title="Нажмите, чтобы открыть подробную карточку боя"><td>{dt_str}</td><td><span class="{type_class}">{type_str}</span></td><td style="color:#58a6ff;font-family:\'Inter\',sans-serif;font-weight:600">{opponent}</td><td style="color:#8b949e;font-family:\'Inter\',sans-serif;font-size:0.75rem">{opp_clan}</td><td style="font-family:\'Roboto Mono\';font-size:0.75rem;color:#8b949e">{my_units_abbr}</td><td><span class="{res_class}">{res_str}</span></td><td style="text-align:right;font-family:\'Roboto Mono\';color:{delta_color};font-weight:bold">{delta_str}</td></tr>\''''

new_ksotar_row = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f'<tr onclick="window.location=\'{file_html}\'" style="cursor:pointer" title="Нажмите, чтобы открыть подробную карточку боя"><td>{dt_str}</td><td><span class="{type_class}">{type_str}</span></td><td style="color:#58a6ff;font-family:\'Inter\',sans-serif;font-weight:600">{opponent}</td><td style="color:#8b949e;font-family:\'Inter\',sans-serif;font-size:0.75rem">{opp_clan}</td><td style="font-family:\'Roboto Mono\';font-size:0.75rem;color:#58a6ff" title="{ \', \'.join(b.get(\'units\', [])) }">{my_units_abbr}</td><td style="font-family:\'Roboto Mono\';font-size:0.75rem;color:#8b949e" title="{ \', \'.join(b.get(\'enemy_units\', [])) }">{enemy_units_abbr}</td><td><span class="{res_class}">{res_str}</span></td><td style="text-align:right;font-family:\'Roboto Mono\';color:{delta_color};font-weight:bold">{delta_str}</td></tr>\''''

if old_ksotar_row in text:
    text = text.replace(old_ksotar_row, new_ksotar_row)
    print("Updated ksotar row rendering!")
else:
    print("old_ksotar_row not found")

# 3. Также исправим col_span для сообщения "Бои не найдены"
text = text.replace('col_span = 6', 'col_span = 8')

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved generate_personal_stats.py successfully!")
