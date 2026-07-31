with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'rows += f\'<tr onclick=' in line and 'ksotar' in lines[idx-5]:
        # Заменим на чистую конкатенацию без вложенных кавычек в f-string
        lines[idx] = "                    rows += '<tr onclick=\"window.location=\\'' + file_html + '\\'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\">'\n"
        # Вставим добавление ячеек по одной, чтобы избежать синтаксических ошибок f-string
        # Создадим новые строки для вставки
        new_lines = [
            "                    rows += '<td>' + dt_str + '</td>'\n",
            "                    rows += '<td><span class=\"' + type_class + '\">' + type_str + '</span></td>'\n",
            "                    rows += '<td style=\"color:#58a6ff;font-family:\\'Inter\\',sans-serif;font-weight:600\">' + opponent + '</td>'\n",
            "                    rows += '<td style=\"color:#8b949e;font-family:\\'Inter\\',sans-serif;font-size:0.75rem\">' + opp_clan + '</td>'\n",
            "                    rows += '<td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#58a6ff\">' + my_units_abbr + '</td>'\n",
            "                    rows += '<td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#8b949e\">' + enemy_units_abbr + '</td>'\n",
            "                    rows += '<td><span class=\"' + res_class + '\">' + res_str + '</span></td>'\n",
            "                    rows += '<td style=\"text-align:right;font-family:\\'Roboto Mono\\';color:' + delta_color + ';font-weight:bold\">' + delta_str + '</td></tr>'\n"
        ]
        # Заменим текущую строку и очистим следующие (если они были частью старой строки)
        lines[idx] = "".join([
            "                    rows += f'<tr onclick=\"window.location=\" + repr(file_html) + \"\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\">'\n",
            "                    rows += f'<td>{dt_str}</td><td><span class=\"{type_class}\">{type_str}</span></td>'\n",
            "                    rows += f'<td style=\"color:#58a6ff;font-family:\\'Inter\\',sans-serif;font-weight:600\">{opponent}</td>'\n",
            "                    rows += f'<td style=\"color:#8b949e;font-family:\\'Inter\\',sans-serif;font-size:0.75rem\">{opp_clan}</td>'\n",
            "                    rows += f'<td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#58a6ff\">{my_units_abbr}</td>'\n",
            "                    rows += f'<td style=\"font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#8b949e\">{enemy_units_abbr}</td>'\n",
            "                    rows += f'<td><span class=\"{res_class}\">{res_str}</span></td>'\n",
            "                    rows += f'<td style=\"text-align:right;font-family:\\'Roboto Mono\\';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>'\n"
        ])
        break

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully fixed f-string syntax!")
