import json
import os

SNAPSHOTS_DIR = 'snapshots'
# Берем данные из утреннего снапшота
source_file = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-05-01_00-56.json')
target_file = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_23-59.json')

with open(source_file, 'r') as f:
    data = json.load(f)

# Устанавливаем ТЕОРЕТИЧЕСКИЙ рейтинг до сгорания
# (Текущий рейтинг + ночная потеря)
data['clanRating'] = 11298363 

with open(target_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print(f"Снапшот {target_file} создан с рейтингом {data['clanRating']}")
