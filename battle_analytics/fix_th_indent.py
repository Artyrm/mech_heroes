# -*- coding: utf-8 -*-
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('table_headers =')
end_pos = text.find('\n', pos)

# Find exact indentation
line_start = text.rfind('\n', 0, pos) + 1
indent = text[line_start:pos]

new_th_line = indent + 'table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick.strip() == "ksotar" else "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"'
text = text[:line_start] + new_th_line + text[end_pos:]

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed table_headers indentation successfully!')
