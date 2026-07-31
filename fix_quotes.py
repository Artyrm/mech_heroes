with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's replace the multiline concatenation with single-line clean string building
old_block = '''                    rows += "<tr onclick=\"window.location='" + file_html + "'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\">" \\
                            "<td>" + dt_str + "</td>" \\
                            "<td><span class=\"" + type_class + "\">" + type_str + "</span></td>" \\
                            "<td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">" + opponent + "</td>" \\
                            "<td style=\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\">" + opp_clan + "</td>" \\
                            "<td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\" title=\"" + my_units_str + "\">" + my_units_abbr + "</td>" \\
                            "<td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\" title=\"" + enemy_units_str + "\">" + enemy_units_abbr + "</td>" \\
                            "<td><span class=\"" + res_class + "\">" + res_str + "</span></td>" \\
                            "<td style=\"text-align:right;font-family:'Roboto Mono';color:" + delta_color + ";font-weight:bold\">" + delta_str + "</td></tr>"'''

new_block = '''                    rows += f"<tr onclick=\\\"window.location='{file_html}'\\\" style=\\\"cursor:pointer\\\" title=\\\"Нажмите, чтобы открыть подробную карточку боя\\\"><td style=\\\"white-space:nowrap\\\">{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\\">{opponent}</td><td style=\\\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\\">{opp_clan}</td><td style=\\\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\\">{my_units_abbr}</td><td style=\\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"'''

with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'rows += "<tr onclick=' in l:
        lines[i] = '                    rows += f"<tr onclick=\\'window.location=' + repr(file_html) + '\\' style=\\'cursor:pointer\\' title=\\'Нажмите, чтобы открыть подробную карточку боя\\'><td style=\\'white-space:nowrap\\'>{dt_str}</td><td><span class=\\'{type_class}\\'>{type_str}</span></td><td style=\\'color:#58a6ff;font-family:\\'Inter\\',sans-serif;font-weight:600\\'>{opponent}</td><td style=\\'color:#8b949e;font-family:\\'Inter\\',sans-serif;font-size:0.75rem\\'>{opp_clan}</td><td style=\\'font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#58a6ff\\'>{my_units_abbr}</td><td style=\\'font-family:\\'Roboto Mono\\';font-size:0.75rem;color:#8b949e\\'>{enemy_units_abbr}</td><td><span class=\\'{res_class}\\'>{res_str}</span></td><td style=\\'text-align:right;font-family:\\'Roboto Mono\\';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"\\n'\n'

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed quotes with repr!")
