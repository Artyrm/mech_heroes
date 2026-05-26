import json, os

path = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\snapshots'
files = sorted([f for f in os.listdir(path) if f.startswith('points_utc_') and f.endswith('.json')])

# Твой ID, который нужно отследить
# Найдем его в последнем файле, чтобы быть уверенными в ID
ksotar_id = None
with open(os.path.join(path, files[-1]), 'r') as f:
    data = json.load(f)
    # Поиск ksotar через базу имен
    with open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\clan_monitor\members_name_db.json', 'r', encoding='utf-8') as db:
        names = json.load(db)
        for uid, info in names.items():
            if 'ksotar' in info['nick'].lower():
                ksotar_id = uid
                break

if not ksotar_id:
    print("Не удалось найти ID для ksotar в members_name_db.json")
    exit()

print(f'Анализ очков для ksotar (ID: {ksotar_id}) (последние 100 снэпшотов):')

last_pts = None
for f_name in files[-100:]:
    try:
        with open(os.path.join(path, f_name), 'r') as f:
            data = json.load(f)
            pts = data.get('pts', {}).get(ksotar_id)
            if pts is None: continue
            
            # Ищем падение более чем на 5000
            if last_pts is not None and pts < last_pts - 5000:
                print(f'СБРОС обнаружен в {f_name}: {last_pts} -> {pts}')
            
            last_pts = pts
    except:
        continue
