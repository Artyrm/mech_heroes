path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Нам нужно изменить заголовок таблицы и строки в generate_dossiers для обычных игроков (nick != 'ksotar')
# Для ksotar оставляем колонку "Противник", а для остальных убираем.
# Также сделаем отображение состава отряда игрока и отряда противника с сокращением названий юнитов до двух заглавных букв.

print('Writing fix script for dossier columns and unit abbreviation...')
