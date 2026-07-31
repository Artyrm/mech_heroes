with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Найдем второе вхождение if nick == 'ksotar':
start = text.find('if nick == \'ksotar\':')
start2 = text.find('if nick == \'ksotar\':', start + 20)

# Посмотрим вокруг start2
print("Found start2 at:", start2)
print(text[start2:start2+300])

# Заменим этот блок
old_snippet = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    p_folder = b.get('p_nick', '')
                    file_html = f"../{p_folder}/{b.get('file_html', '#')}"
                    rows += f"<tr onclick=\"window.location='{file_html}'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">{opponent}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\">{my_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>"'''

new_snippet = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\"window.location='{file_html}'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">{opponent}</td><td style=\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\">{opp_clan}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\">{my_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>"'''

old_headers = '<table><thead><tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr></thead><tbody>{rows}</tbody></table>'
new_headers = '<table><thead><tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Состав отряда</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr></thead><tbody>{rows}</tbody></table>'

if old_snippet in text:
    text = text.replace(old_snippet, new_snippet)
    print("Successfully replaced ksotar row generation!")
else:
    print("Could not find old_snippet!")

if old_headers in text:
    text = text.replace(old_headers, new_headers)
    print("Successfully replaced headers!")
else:
    print("Could not find old_headers!")

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)
