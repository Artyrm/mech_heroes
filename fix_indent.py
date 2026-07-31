with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    table_headers = "<tr>', 'table_headers = "<tr>')

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed indentation!")
