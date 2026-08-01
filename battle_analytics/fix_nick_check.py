# -*- coding: utf-8 -*-
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("if nick == 'ksotar':", "if nick.strip() == 'ksotar':")
text = text.replace('if nick == "ksotar":', 'if nick.strip() == "ksotar":')
text = text.replace('nick == "ksotar"', '(nick == "ksotar" or nick.strip() == "ksotar")')
text = text.replace("nick == 'ksotar'", "(nick == 'ksotar' or nick.strip() == 'ksotar')")

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated nick comparisons successfully!')
