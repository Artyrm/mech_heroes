path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'tactical_html = ""' in line or 'tactical_html = \'\'\n' in line:
        new_lines.append('        tactical_html = \'\'\n')
    elif 'if nick != "ksotar":' in line or "if nick != 'ksotar':" in line:
        new_lines.append('        if nick != \'ksotar\':\n')
    elif 'tactical-summary' in line and 'tactical_html +=' not in line:
        new_lines.append('            tactical_html = \'<div class=\"tactical-summary\"><h2>Тактический анализ (по составам)</h2>\'\n')
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Indentation fixed via fix_indent.py!')
