import os
import json
import glob
import hashlib
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arena.registry_manager as rm

def get_pseudo_uid(nick):
    return -int(hashlib.md5(nick.encode()).hexdigest()[:8], 16)

def register_and_generate_ghosts():
    print("--- Phase 3: Registering ghosts and generating profile history stubs ---")
    
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    
    # Сделаем обратный маппинг существующих ников
    existing_nicks_lower = {n.strip().lower() for n in known_users.values()}
    
    analytics_dir = 'battle_analytics'
    player_dirs = [d for d in os.listdir(analytics_dir) if os.path.isdir(os.path.join(analytics_dir, d)) and not d.startswith('__') and d != 'snapshots']
    
    added_count = 0
    
    for p_nick in player_dirs:
        if p_nick == 'ksotar' or p_nick.startswith('--'): continue
        
        # Соберем все бои этого игрока, чтобы вытащить его рейтинг и клан
        p_dir = os.path.join(analytics_dir, p_nick)
        battles = []
        for bf in glob.glob(os.path.join(p_dir, "battle_*.json")):
            try:
                with open(bf, 'r', encoding='utf-8') as f:
                    b_data = json.load(f)
                    
                    dt_str = b_data.get('fightTime', '')
                    # Попробуем распарсить дату
                    # формат: 19/05/2026_14:13:16.0090
                    dt = None
                    try:
                        parts = dt_str.replace('/', '_').replace('.', '_').replace(':', '_').split('_')
                        if len(parts) >= 6:
                            dt = datetime(int(parts[2]), int(parts[1]), int(parts[0]), int(parts[3]), int(parts[4]), int(parts[5]))
                    except:
                        dt = datetime.now()
                        
                    sd = b_data.get('statistics', {})
                    p_u_data = sd.get('player', {}).get('units', {})
                    e_u_data = sd.get('enemy', {}).get('units', {})
                    p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
                    e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
                    is_attack = p_min < e_min
                    
                    p_name = sd.get('player', {}).get('name', p_nick)
                    e_name = sd.get('enemy', {}).get('name', 'Противник')
                    
                    opponent = e_name if is_attack else p_name
                    opp_rating = int(b_data.get('opponentRating', 0))
                    
                    p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
                    e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
                    p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
                    e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
                    opponent_clan = e_clan if is_attack else p_clan
                    
                    battles.append({
                        'dt': dt,
                        'dt_str': dt.strftime("%Y-%m-%dT%H-%M-%S"),
                        'opponent': opponent.strip(),
                        'rating': opp_rating,
                        'clan': opponent_clan if opponent_clan != '-' else ''
                    })
            except: pass
            
        if not battles: continue
        
        # Определим имя оппонента (папка battle_analytics/Experd содержала бои против Experd или где он был участником)
        # Нам нужен реальный ник этого игрока. Если p_nick это ник оппонента:
        ghost_nick = p_nick.strip()
        if ghost_nick.lower() in existing_nicks_lower:
            continue # Уже есть в реестре с нормальным ID
            
        # Генерируем псевдо-ID
        pseudo_uid = get_pseudo_uid(ghost_nick)
        uid_str = str(pseudo_uid)
        
        known_users[uid_str] = ghost_nick
        existing_nicks_lower.add(ghost_nick.lower())
        added_count += 1
        
        # Создаем историю профиля в squads
        squad_dir = os.path.join('arena', 'squads', uid_str)
        os.makedirs(squad_dir, exist_ok=True)
        profile_path = os.path.join(squad_dir, 'profile_history.json')
        
        # Сортируем бои по времени
        battles.sort(key=lambda x: x['dt'])
        
        history = []
        for b in battles:
            history.append({
                'timestamp': b['dt_str'],
                'nickname': ghost_nick,
                'arenaRating': b['rating'],
                'rating': b['rating'],
                'clanProfile': {
                    'clanName': b['clan'],
                    'clanTag': b['clan']
                }
            })
            
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        print(f"  + Added ghost '{ghost_nick}' with pseudo UID {pseudo_uid} ({len(history)} battle snapshots)")

    if added_count > 0:
        reg['known_users'] = known_users
        rm.save_registry(reg)
        print(f"Successfully registered {added_count} ghosts in registry and created stubs.")
    else:
        print("No new ghosts to register.")

if __name__ == '__main__':
    register_and_generate_ghosts()
