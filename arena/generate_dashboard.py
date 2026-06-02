import json
import os
import glob
import sys
from datetime import datetime, timedelta

def parse_any_date(s):
    if not s: return datetime(1970, 1, 1)
    try:
        if 'T' in s: # YYYY-MM-DDTHH-MM-SS
            return datetime.strptime(s.split('.')[0], "%Y-%m-%dT%H-%M-%S")
        else: # DD/MM/YYYY_HH:MM:SS
            d, t = s.split('_')
            day, month, year = d.split('/')
            h, m, sec = t.split(':')
            return datetime(int(year), int(month), int(day), int(h), int(m), int(sec.split('.')[0]))
    except: return datetime(1970, 1, 1)

def get_rating_at(uid, target_ts, all_histories):
    history = all_histories.get(uid, [])
    target_dt = parse_any_date(target_ts)
    best_rating = None
    for entry in history:
        if parse_any_date(entry["timestamp"]) <= target_dt:
            best_rating = int(entry.get('power', 0))
        else: break
    return best_rating

def generate():
    snaps_dir = "arena/snapshots"
    template_path = "arena/reports/template.html"
    output_path = "arena/reports/dashboard.html"
    data_dir = "arena/reports/data"
    os.makedirs(data_dir, exist_ok=True)
    
    update_history = "--update_history" in sys.argv
    
    if not os.path.exists(template_path):
        print("Template not found!")
        return

    # 1. Получаем список снимков
    snap_files = sorted(glob.glob(os.path.join(snaps_dir, "arena_*.json")))
    if not snap_files:
        print("No snapshots found.")
        return

    # По умолчанию берем только последние 50 снимков для скорости
    if not update_history and len(snap_files) > 50:
        print(f"Incremental mode: Processing only last 50 snapshots. Use --update_history for full rebuild.")
        snap_files = snap_files[-50:]

    # 2. Загружаем истории игроков (нужно для рейтинга выпавших)
    all_histories = {}
    all_players_ever = {} 
    for hf_path in glob.glob('arena/squads/*/history.json'):
        uid = int(os.path.basename(os.path.dirname(hf_path)))
        try:
            with open(hf_path, 'r', encoding='utf-8') as hf:
                history = json.load(hf)
                if history:
                    all_histories[uid] = history
                    latest = history[-1]
                    all_players_ever[uid] = {
                        'userID': uid, 'rating': latest.get('power', 0),
                        'profileState': {'nickname': os.path.basename(os.path.dirname(hf_path))},
                        'clanProfile': {'clanName': '-', 'clanTag': '-'}
                    }
        except: pass

    # 3. Доп. инфо (ядро, онлайн)
    players_online_info = {}
    holders = set()
    for uid_dir in os.listdir('arena/squads'):
        if not uid_dir.isdigit(): continue
        u_int = int(uid_dir)
        # Online
        online_file = os.path.join('arena', 'squads', uid_dir, 'online_history.json')
        if os.path.exists(online_file):
            try:
                with open(online_file, 'r', encoding='utf-8') as f:
                    oh = json.load(f)
                    if oh: players_online_info[u_int] = oh[-1]
            except: pass
        # Core
        if u_int in all_histories:
            latest = all_histories[u_int][-1]
            eq = latest.get('squad', {}).get('general', {}).get('equipables', {})
            if any(e.get('id') == 'suppression_core' for e in eq.values()):
                holders.add(u_int)

    # 4. Обработка снимков
    processed_snaps = {}
    for f in snap_files:
        try:
            with open(f, 'r', encoding='utf-8') as sf:
                data = json.load(sf)
            ts = data['timestamp']
            current_uids = {int(p['userID']) for p in data['players']}
            
            # Добавляем выпавших
            dropped = []
            for uid, pdata in all_players_ever.items():
                if uid not in current_uids:
                    rating = get_rating_at(uid, ts, all_histories)
                    if rating is not None:
                        p_copy = dict(pdata)
                        p_copy.update({'isDropped': True, 'rating': rating})
                        if uid in all_histories:
                            lh = all_histories[uid][-1]
                            p_copy['power'] = lh.get('squad', {}).get('general', {}).get('power', p_copy.get('power', 0))
                        dropped.append(p_copy)
            
            # Маркеры
            for p in data['players'] + dropped:
                u_id = int(p['userID'])
                if u_id in holders: p['hasSuppressionCore'] = True
                if u_id in players_online_info: p['lastOnline'] = players_online_info[u_id]
            
            dropped.sort(key=lambda x: int(x.get('rating', 0)), reverse=True)
            data['players'].extend(dropped)
            
            # Сохраняем как отдельный JSON для ленивой загрузки
            clean_ts = ts.replace('/', '-').replace(':', '-').replace('.', '_')
            data_filename = f"snap_{clean_ts}.json"
            with open(os.path.join(data_dir, data_filename), 'w', encoding='utf-8') as df:
                json.dump(data, df, ensure_ascii=False)
            
            # В дашборде оставляем только метаданные (для списка выбора)
            processed_snaps[ts] = {"data_file": data_filename}
        except Exception as e:
            print(f"Error processing {f}: {e}")

    # Последний снимок вшиваем целиком для мгновенного старта
    latest_ts = sorted(processed_snaps.keys(), key=lambda x: parse_any_date(x))[-1]
    with open(os.path.join(data_dir, processed_snaps[latest_ts]["data_file"]), 'r', encoding='utf-8') as lf:
        processed_snaps[latest_ts]["full_data"] = json.load(lf)

    users_with_squads = list(all_histories.keys())

    # 5. Инъекция в HTML
    with open(template_path, 'r', encoding='utf-8') as tf:
        html = tf.read()
    
    html = html.replace('SNAPSHOTS_DATA', json.dumps(processed_snaps, ensure_ascii=False))
    html = html.replace('USERS_WITH_SQUADS', json.dumps(users_with_squads))
    now_msk = datetime.utcnow() + timedelta(hours=3)
    html = html.replace('LAST_CHECK_TIME', now_msk.strftime("%d.%m.%Y %H:%M:%S МСК"))
    
    with open(output_path, 'w', encoding='utf-8') as of:
        of.write(html)
        
    print(f"Dashboard generated: {output_path}. {len(processed_snaps)} snapshots linked.")

if __name__ == "__main__":
    generate()
