with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'if nick == \'ksotar\':' in line and idx > 300:
        # Заменим следующие несколько строк на чистый код
        lines[idx] = "                if nick == 'ksotar':\n"
        lines[idx+1] = "                    opponent = b.get('opponent', '-')\n"
        lines[idx+2] = "                    opp_clan = b.get('opponent_clan', '-')\n"
        lines[idx+3] = "                    file_html = b.get('file_html', '#')\n"
        lines[idx+4] = "                    rows += f'<tr onclick=\"window.location=\\'{file_html}\\'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class=\"{type_class}\">{type_str}</span></td><td style=\"color:#58a6ff;font-family:\\'Inter\\',sans-serif;font-weight:600\">{opponent}</td><td style=\"color:#8b949e;font-family:\\'Inter\\',sans-serif;font-size:0.75rem\">{opp_clan}</td><td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#8b949e\">{my_units_abbr}</td><td><span class=\"{res_class}\">{res_str}</span></td><td style=\"text-align:right;font-family:\\'Roboto Mono\\';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>'\n"
        lines[idx+5] = "                else:\n"
        break

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully rewrote ksotar row rendering cleanly!")
