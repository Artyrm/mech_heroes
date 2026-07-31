with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Заменим формирование file_html для ksotar
old_str = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}" if p_folder else f"../{b.get(\'file_html\', \'#\')}"'
new_str = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}"'

if old_str in text:
    text = text.replace(old_str, new_str)
    with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated file_html generation!")
else:
    print("Marker not found")
