import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as pf:
    text = pf.read()

idx = text.find('tactical-summary')
if idx != -1:
    line_start = text.rfind('\n', 0, idx)
    line_end = text.find('\n', idx)
    old_line = text[line_start+1:line_end]
    replacement = 'tactical_html = \"\"\n        if nick != \"ksotar\":\n            ' + old_line
    text = text.replace(old_line, replacement)
    with open(path, 'w', encoding='utf-8') as pf:
        pf.write(text)
    print('Patch script applied successfully!')
else:
    print('tactical-summary not found')
