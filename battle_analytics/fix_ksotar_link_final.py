with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Заменим в generate_personal_stats.py формирование file_html для ksotar
# Нам нужно, чтобы file_html для ksotar был "../" + p_folder + "/" + b.get('file_html')
old_line = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}"'
new_line = 'file_html = f"../{p_folder}/{b.get(\'file_html\', \'#\')}"'

# Если в коде сгенерировалось с лишними ../, исправим:
text = text.replace('f"../../', 'f"../')

with open('battle_analytics/generate_personal_stats.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed double ../ in file_html generation!")
