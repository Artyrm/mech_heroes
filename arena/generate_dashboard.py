import json
import os
import glob
import sys
from datetime import datetime, timedelta

# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arena.registry_manager as rm

def parse_any_date(s):
    if not s: return datetime(1970, 1, 1)
    try:
        if 'T' in s:
            return datetime.strptime(s.split('.')[0], "%Y-%m-%dT%H-%M-%S")
        else:
            d, t = s.split('_')
            day, month, year = d.split('/')
            h, m, sec = t.split(':')
            return datetime(int(year), int(month), int(day), int(h), int(m), int(sec.split('.')[0]))
    except: return datetime(1970, 1, 1)

def get_history_entry_at(uid, target_dt, all_histories):
    history = all_histories.get(uid, [])
    best_entry = None
    for entry in history:
        if parse_any_date(entry["timestamp"]) <= target_dt:
            best_entry = entry
        else: break
    return best_entry

def generate():
    snaps_dir = "arena/snapshots"
    template_path = "arena/reports/template.html"
    output_path = "arena/reports/dashboard.html"
    
    update_history = "--update_history" in sys.argv
    
    if not os.path.exists(template_path):
        print("Template not found!")
        return

    # 1. Загружаем Реестр
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})

    # 2. Получаем список снимков
    snap_files = sorted(glob.glob(os.path.join(snaps_dir, "arena_*.json")))
    if not snap_files: return

    # Для дашборда берем последние 100
    if not update_history and len(snap_files) > 100:
        snap_files = snap_files[-100:]

    # 3. Загружаем истории
    all_histories = {}
    for hf_path in glob.glob('arena/squads/*/history.json'):
        uid = int(os.path.basename(os.path.dirname(hf_path)))
        try:
            with open(hf_path, 'r', encoding='utf-8') as hf:
                hist = json.load(hf)
                if hist: all_histories[uid] = hist
        except: pass

    # 4. Доп. инфо
    players_online_info = {}
    holders = set()
    for uid_str, nick in known_users.items():
        u_int = int(uid_str)
        online_file = os.path.join('arena', 'squads', uid_str, 'online_history.json')
        if os.path.exists(online_file):
            try:
                with open(online_file, 'r', encoding='utf-8') as f:
                    oh = json.load(f)
                    if oh: players_online_info[u_int] = oh[-1]
            except: pass
        if u_int in all_histories:
            latest = all_histories[u_int][-1]
            eq = latest.get('squad', {}).get('general', {}).get('equipables', {})
            if any(e.get('id') == 'suppression_core' for e in eq.values()):
                holders.add(u_int)

    # 5. Обработка
    processed_snaps = {}
    print(f"Processing {len(snap_files)} snapshots for Dashboard...")

    for f in snap_files:
        try:
            with open(f, 'r', encoding='utf-8') as sf:
                data = json.load(sf)
            
            ts = data['timestamp']
            current_dt = parse_any_date(ts)
            current_uids = {int(p.get('userID', p.get('userId'))) for p in data['players'] if p.get('userID') or p.get('userId')}
            
            # Добавляем ВСЕХ зарегистрированных игроков, которых нет в этом снимке
            all_known_uids = {int(uid) for uid in known_users.keys()}
            missing_uids = all_known_uids - current_uids
            
            for uid in missing_uids:
                he = get_history_entry_at(uid, current_dt, all_histories)
                if he:
                    squad = he.get('squad', {})
                    gen = squad.get('general', {})
                    data['players'].append({
                        'userID': uid,
                        'rating': he.get('power', 0),
                        'isDropped': True,
                        'power': gen.get('power', 0),
                        'profileState': {
                            'nickname': known_users.get(str(uid), str(uid)),
                            'winCount': gen.get('winCount', 0),
                            'defeatCount': gen.get('defeatCount', 0)
                        },
                        'clanProfile': {
                            'clanName': squad.get('clanName', '-'),
                            'clanTag': squad.get('clanTag', '')
                        }
                    })
            
            # Маркеры
            for p in data['players']:
                uid = int(p.get('userID', p.get('userId')))
                if uid in holders: p['hasSuppressionCore'] = True
                if uid in players_online_info: p['lastOnline'] = players_online_info[uid]
            
            # Сортировка по рейтингу
            data['players'].sort(key=lambda x: int(x.get('rating', 0)), reverse=True)
            
            # Вшиваем ВСЁ в один объект
            processed_snaps[ts] = {"players": data['players']}
        except Exception as e:
            print(f"Error: {e}")

    users_with_squads = [int(u) for u in all_histories.keys()]

    with open(template_path, 'r', encoding='utf-8') as tf:
        html = tf.read()
    
    html = html.replace('SNAPSHOTS_DATA', json.dumps(processed_snaps, ensure_ascii=False))
    html = html.replace('USERS_WITH_SQUADS', json.dumps(users_with_squads))
    now_msk = datetime.utcnow() + timedelta(hours=3)
    html = html.replace('LAST_CHECK_TIME', now_msk.strftime("%d.%m.%Y %H:%M:%S МСК"))
    
    with open(output_path, 'w', encoding='utf-8') as of:
        of.write(html)
        
    print(f"Dashboard generated: {output_path}. {len(processed_snaps)} snapshots inlined.")

if __name__ == "__main__":
    generate()
