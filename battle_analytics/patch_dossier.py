import os

with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Заменим блок формирования таблицы в generate_dossiers
old_code_marker = '        rows = ""'
if old_code_marker in text:
    parts = text.split(old_code_marker)
    # Нам нужно заменить начиная с rows = "" до конца html
    # Давайте найдем точное место
    print("Found marker")

# Напишем патч через замену всей генерации html в generate_dossiers
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'rows = ""' in line:
        skip = True
        # Вставим нашу новую логику
        new_lines.append('        table_headers = \'<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Состав отряда</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr>\' if nick == \'ksotar\' else \'<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr>\'\n')
        new_lines.append('        rows = ""\n')
        new_lines.append('        if battles:\n')
        new_lines.append('            for b in reversed(battles):\n')
        new_lines.append('                dt_str = (b[\'dt\'] + timedelta(hours=3)).strftime(\'%d.%m %H:%M\')\n')
        new_lines.append('                type_str = \'АТАКА\' if b[\'is_attack\'] else \'ЗАЩИТА\'\n')
        new_lines.append('                type_class = \'type-attack\' if b[\'is_attack\'] else \'type-defense\'\n')
        new_lines.append('                res_str = \'ПОБЕДА\' if b[\'is_win\'] else \'ПОРАЖЕНИЕ\'\n')
        new_lines.append('                res_class = \'res-win\' if b[\'is_win\'] else \'res-loss\'\n')
        new_lines.append('                delta_val = b[\'delta\']\n')
        new_lines.append('                delta_str = f\"+{delta_val}\" if delta_val > 0 else str(delta_val)\n')
        new_lines.append('                delta_color = \'#3fb950\' if delta_val > 0 else (\'#f85149\' if delta_val < 0 else \'#8b949e\')\n')
        new_lines.append('                my_units_abbr = abbrev_units(b.get(\'units\', []))\n')
        new_lines.append('                enemy_units_abbr = abbrev_units(b.get(\'enemy_units\', []))\n')
        new_lines.append('                if nick == \'ksotar\':\n')
        new_lines.append('                    opponent = b.get(\'opponent\', \'-\')\n')
        new_lines.append('                    p_folder = b.get(\'p_nick\', \'\')\n')
        new_lines.append('                    file_html = f\"../{p_folder}/{b.get(\'file_html\', \'#\')}\" if p_folder else f\"../{b.get(\'file_html\', \'#\')}\"\n')
        new_lines.append('                    rows += f\'<tr onclick=\"window.location=\\'{file_html}\\'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class=\"{type_class}\">{type_str}</span></td><td style=\"color:#58a6ff;font-family:\\\'Inter\\\',sans-serif;font-weight:600\">{opponent}</td><td style=\"font-family:\\\'Roboto Mono\\\';font-size:0.75rem;color:#8b949e\">{my_units_abbr}</td><td><span class=\"{res_class}\">{res_str}</span></td><td style=\"text-align:right;font-family:\\\'Roboto Mono\\\';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>\'\n')
        new_lines.append('                else:\n')
        new_lines.append('                    file_html = b.get(\'file_html\', \'#\')\n')
        new_lines.append('                    rows += f\'<tr onclick=\"window.location=\\'{file_html}\\'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class=\"{type_class}\">{type_str}</span></td><td style=\"font-family:\\\'Roboto Mono\\\';font-size:0.75rem;color:#58a6ff\" title=\"{\\\', \\\'.join(b.get(\\\'units\\\', []))}\">{my_units_abbr}</td><td style=\"font-family:\\\'Roboto Mono\\\';font-size:0.75rem;color:#8b949e\" title=\"{\\\', \\\'.join(b.get(\\\'enemy_units\\\', []))}\">{enemy_units_abbr}</td><td><span class=\"{res_class}\">{res_str}</span></td><td style=\"text-align:right;font-family:\\\'Roboto Mono\\\';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>\'\n')
        new_lines.append('        else:\n')
        new_lines.append('            col_span = 6 if nick == \'ksotar\' else 6\n')
        new_lines.append('            rows = f\'<tr><td colspan=\"{col_span}\" style=\"text-align:center;color:#8b949e;padding:20px\">Бои не найдены</td></tr>\'\n')
    elif skip and 'target_dir = os.path.join' in line:
        skip = False
        new_lines.append(line)
    elif skip:
        continue
    else:
    # также поправим html template в generate_dossiers чтобы использовать {table_headers}
        if '<thead><tr><th>Дата и время' in line:
            line = '        <table><thead>{table_headers}</thead><tbody>{rows}</tbody></table>\n'
        new_lines.append(line)

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully patched generate_personal_stats.py!")
