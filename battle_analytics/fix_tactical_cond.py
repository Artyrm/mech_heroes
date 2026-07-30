path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i == 230:
        new_lines.append('        if nick != \'ksotar\':\n')
        new_lines.append('            tactical_html = \'<div class=\"tactical-summary\"><h2>Тактический анализ (по составам)</h2>\'\n')
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Applied conditional tactical_html successfully!')
