import json, os

path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
files = sorted([f for f in os.listdir(path) if f.startswith('points_utc_') and f.endswith('.json')])

last_rating = None
print('Анализ рейтинга клана (последние 100 снэпшотов):')

for f_name in files[-100:]:
    try:
        with open(os.path.join(path, f_name), 'r') as f:
            data = json.load(f)
            r = data.get('clanRating')
            if r is None: continue
            
            if last_rating is not None and r < last_rating - 5000:
                print(f'СБРОС обнаружен в {f_name}: {last_rating} -> {r}')
            
            last_rating = r
    except:
        continue
