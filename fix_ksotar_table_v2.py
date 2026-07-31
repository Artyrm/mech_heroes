with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Заменим table_headers для ksotar
old_h = 'table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Состав отряда</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else'
new_h = 'table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else'

if old_h in text:
    text = text.replace(old_h, new_h)
    print("Updated table_headers successfully!")
else:
    print("old_h not found")

# 2. Заменим блок рендеринга строки для ksotar
start_k = text.find("if nick == 'ksotar':")
print("Found ksotar block at:", start_k)

# Перепишем генерацию строки для ksotar в generate_personal_stats.py
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "if nick == 'ksotar':" in line and idx > 300:
        lines[idx] = "                if nick == 'ksotar':\n"
        lines[idx+1] = "                    opponent = b.get('opponent', '-')\n"
        lines[idx+2] = "                    opp_clan = b.get('opponent_clan', '-')\n"
        lines[idx+3] = "                    file_html = b.get('file_html', '#')\n"
        lines[idx+4] = "                    rows += f'<tr onclick=\"window.location=\\'{file_html}\\'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class=\"{type_class}\">{type_str}</span></td><td style=\"color:#58a6ff;font-family:\\'Inter\\',sans-serif;font-weight:600\">{opponent}</td><td style=\"color:#8b949e;font-family:\\'Inter\\',sans-serif;font-size:0.75rem\">{opp_clan}</td><td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#58a6ff\" title=\"{ \', \'.join(b.get(\'units\', [])) }\">{my_units_abbr}</td><td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#8b949e\" title=\"{ \', \'.join(b.get(\'enemy_units\', [])) }\">{enemy_units_abbr}</td><td><span class=\"{res_class}\">{res_str}</span></td><td style=\"text-align:right;font-family:\\'Roboto Mono\\';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>'\n"
        lines[idx+5] = "                else:\n"
        break

text = "".join(lines)
text = text.replace('col_span = 6', 'col_span = 8')

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated generate_personal_stats.py table structure!")
