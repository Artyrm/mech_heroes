import os
import json
import glob
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arena.registry_manager as rm

def analyze_nicks():
    print("--- Phase 1: Scanning nicknames and searching for IDs ---")
    
    # 1. Загружаем текущий реестр
    reg = rm.load_registry(force_rebuild=True)
    known_users = reg.get('known_users', {}) # uid_str -> nick
    
    # Сделаем обратный словарь для быстрого поиска (приведем ник к lowercase без пробелов)
    # nick_lower -> uid
    nick_to_uid = {}
    for uid, nick in known_users.items():
        if nick:
            nick_to_uid[nick.strip().lower()] = uid

    # 2. Посмотрим в last_init_dump.json, если есть
    init_dump_path = os.path.join('arena', 'last_init_dump.json')
    if os.path.exists(init_dump_path):
        try:
            with open(init_dump_path, 'r', encoding='utf-8') as f:
                dump_data = json.load(f)
                # Поищем везде, где могут быть юзеры с ID
                # Например, в лиге, друзьях, сокланах
                def scan_dict(d):
                    if isinstance(d, dict):
                        uid = d.get('userID', d.get('userId'))
                        nick = d.get('nickname') or d.get('profileState', {}).get('nickname')
                        if uid and nick:
                            n_clean = nick.strip().lower()
                            if n_clean not in nick_to_uid:
                                nick_to_uid[n_clean] = str(uid)
                        for k, v in d.items():
                            scan_dict(v)
                    elif isinstance(d, list):
                        for item in d:
                            scan_dict(item)
                scan_dict(dump_data)
        except Exception as e:
            print(f"Error reading init dump: {e}")

    # 3. Собираем все уникальные ники противников из папки battle_analytics
    analytics_dir = 'battle_analytics'
    battle_nicks = set()
    
    player_dirs = [d for d in os.listdir(analytics_dir) if os.path.isdir(os.path.join(analytics_dir, d)) and not d.startswith('__') and d != 'snapshots']
    
    for p_nick in player_dirs:
        p_dir = os.path.join(analytics_dir, p_nick)
        for bf in glob.glob(os.path.join(p_dir, "battle_*.json")):
            try:
                with open(bf, 'r', encoding='utf-8') as f:
                    b_data = json.load(f)
                    sd = b_data.get('statistics', {})
                    
                    # Определяем, кто был противником
                    p_u_data = sd.get('player', {}).get('units', {})
                    e_u_data = sd.get('enemy', {}).get('units', {})
                    p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
                    e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
                    is_attack = p_min < e_min
                    
                    p_name = sd.get('player', {}).get('name', p_nick)
                    e_name = sd.get('enemy', {}).get('name', 'Противник')
                    
                    opponent = e_name if is_attack else p_name
                    if opponent and opponent.strip() and opponent != 'Противник':
                        battle_nicks.add(opponent.strip())
            except: pass

    # Также добавим владельцев папок в battle_analytics
    for p_nick in player_dirs:
        if p_nick != 'ksotar':
            battle_nicks.add(p_nick.strip())

    print(f"Total unique nicknames found in battle analytics & folders: {len(battle_nicks)}")

    matched_count = 0
    ghosts = []

    for nick in sorted(battle_nicks):
        n_clean_lower = nick.lower()
        if n_clean_lower in nick_to_uid:
            matched_count += 1
        else:
            ghosts.append(nick)

    print(f"  - Matched with existing IDs (Registry or Init Dump): {matched_count}")
    print(f"  - True Ghosts (No ID found anywhere): {len(ghosts)}")
    print("\nSample of True Ghosts:")
    for g in ghosts[:20]:
        print(f"    * {g}")

if __name__ == '__main__':
    analyze_nicks()
