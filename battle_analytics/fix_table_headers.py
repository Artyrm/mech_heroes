# -*- coding: utf-8 -*-
with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('table_headers =')
end_pos = text.find('\n', pos)
print('Current line:', text[pos:end_pos])

new_line = '        table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>" if nick == "ksotar" else "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"'
text = text[:pos] + new_line + text[end_pos:]

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated table_headers line successfully via script!')
