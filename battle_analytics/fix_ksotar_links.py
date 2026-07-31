with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Заменим формирование file_html для ksotar
target = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}" if p_folder else f"../{b.get(\'file_html\', \'#\')}"'
replacement = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}" if p_folder else f"../{b.get(\'file_html\', \'#\')}"'

# Убедимся, что путь правильный: относительный путь из battle_analytics/ksotar/ до battle_analytics/<p_folder>/<file>.html
# Это ровно "../{p_folder}/{file_html}"
print("Checking file_html logic...")
