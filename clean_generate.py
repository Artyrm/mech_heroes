with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's completely rewrite generate_dossiers rendering loop for ksotar to be clean and bug-free
old_target = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\\"window.location='{file_html}'\\" style=\\"cursor:pointer\\" title=\\"Нажмите, чтобы открыть подробную карточку боя\\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\\">{opponent}</td><td style=\\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\\">{opp_clan}</td><td style=\\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\\">{my_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\\">{delta_str}</td></tr>"                else:'''

new_target = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\"window.location='{file_html}'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">{opponent}</td><td style=\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\">{opp_clan}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\">{my_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>"
                else:'''

if old_target in text:
    text = text.replace(old_target, new_target)
    print("Successfully replaced dirty block with clean block!")
else:
    print("Old target not found exactly")

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)
