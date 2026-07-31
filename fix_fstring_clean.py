with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's replace the whole generate_dossiers function or rewrite the loop for ksotar to avoid f-string escaping nightmares
start_idx = text.find('if nick == \'ksotar\':\n                    opponent')
if start_idx == -1:
    start_idx = text.find("if nick == 'ksotar':")

# Let's inspect lines 315 to 335
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[310:330], 311):
    print(f"{i}: {l.strip()}")

# Let's rewrite lines 317 to 325 cleanly using plain string formatting or simple concatenation
clean_replacement = '''                if nick == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    my_units_str = ", ".join(b.get('units', []))
                    enemy_units_str = ", ".join(b.get('enemy_units', []))
                    rows += "<tr onclick=\"window.location='" + file_html + "'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\">" \\
                            "<td>" + dt_str + "</td>" \\
                            "<td><span class=\"" + type_class + "\">" + type_str + "</span></td>" \\
                            "<td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">" + opponent + "</td>" \\
                            "<td style=\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\">" + opp_clan + "</td>" \\
                            "<td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\" title=\"" + my_units_str + "\">" + my_units_abbr + "</td>" \\
                            "<td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\" title=\"" + enemy_units_str + "\">" + enemy_units_abbr + "</td>" \\
                            "<td><span class=\"" + res_class + "\">" + res_str + "</span></td>" \\
                            "<td style=\"text-align:right;font-family:'Roboto Mono';color:" + delta_color + ";font-weight:bold\">" + delta_str + "</td></tr>"
'''

# Find where if nick == 'ksotar': starts after line 300
target_idx = -1
for idx, line in enumerate(lines):
    if idx > 300 and "if nick == 'ksotar':" in line:
        target_idx = idx
        break

if target_idx != -1:
    # Replace from target_idx to target_idx + 6 with clean_replacement
    lines[target_idx:target_idx+7] = [clean_replacement + "\n"]
    with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully replaced ksotar row generation with clean concatenation!")
else:
    print("Could not find ksotar row generation block")
