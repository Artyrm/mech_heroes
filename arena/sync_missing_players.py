import os
import json
import hashlib
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from battle_analytics.generate_personal_stats import get_player_battles_timeline
import arena.registry_manager as rm

def get_pseudo_uid(nick):
    # Уникальный отрицательный ID на основе ника
    return -int(hashlib.md5(nick.encode()).hexdigest()[:8], 16)

def sync_missing():
    print("Syncing missing players from battle histories to global registry...")
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    
    # Обратный маппинг для быстрого поиска по нику
    nick_to_uid = {v: int(k) for k, v in known_users.items()}
    
    timelines = get_player_battles_timeline()
    
    added = 0
    for nick, battles in timelines.items():
        if nick == 'ksotar' or not nick: continue
        
        uid = nick_to_uid.get(nick)
        if not uid:
            uid = get_pseudo_uid(nick)
            reg['known_users'][str(uid)] = nick
            nick_to_uid[nick] = uid
            added += 1
            print(f"  Added {nick} with pseudo-UID {uid}")
            
        # Обновим profile_history.json для них, чтобы генераторы могли подтянуть рейтинг
        # Нам нужен самый актуальный рейтинг и клан
        if not battles: continue
        last_battle = max(battles, key=lambda x: x['dt'])
        rating = last_battle.get('opp_rating', 0)
        clan = last_battle.get('opponent_clan', '-')
        
        squad_dir = os.path.join('arena', 'squads', str(uid))
        os.makedirs(squad_dir, exist_ok=True)
        
        profile_path = os.path.join(squad_dir, 'profile_history.json')
        history = []
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except: pass
            
        # Добавляем или обновляем
        ts = last_battle['dt'].strftime("%Y-%m-%dT%H-%M-%S")
        
        # Проверяем, есть ли уже запись свежее или такая же
        found = False
        for entry in history:
            if entry.get('timestamp') == ts:
                found = True; break
        
        if not found:
            history.append({
                'timestamp': ts,
                'nickname': nick,
                'arenaRating': rating,
                'rating': rating,
                'clanProfile': {
                    'clanName': clan,
                    'clanTag': clan if clan != '-' else ''
                }
            })
            # Сортируем
            history.sort(key=lambda x: x['timestamp'])
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False)
                
    if added > 0:
        rm.save_registry(reg)
        print(f"Successfully synced {added} new users to registry.")
    else:
        print("No new users to sync.")

if __name__ == "__main__":
    sync_missing()
