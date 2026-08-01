with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "if nick.strip() == 'ksotar':" in line and idx > 150:
        # Check next lines for table_headers
        if "table_headers =" in lines[idx+1]:
            lines[idx+1] = '            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"\n'
        if "table_headers =" in lines[idx+3]:
            lines[idx+3] = '            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\\"text-align:right\\">Δ Рейтинг</th></tr>"\n'
        break

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully updated table_headers cleanly via lines!")
