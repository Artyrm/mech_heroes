with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Убедимся, что enemy_units всегда определяется перед append
for i, line in enumerate(lines):
    if "'enemy_units': tuple(enemy_units)," in line:
        # Проверим, есть ли перед этим определение enemy_units
        print(f"Found enemy_units tuple at line {i+1}")

with open('battle_analytics/generate_personal_stats.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Заменим весь блок сбора all_ksotar_battles на чистый и корректный
start_idx = text.find('all_ksotar_battles = []')
end_idx = text.find('player_timelines[\'ksotar\'] = all_ksotar_battles')

print("Start idx:", start_idx, "End idx:", end_idx)
