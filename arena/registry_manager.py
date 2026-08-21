import json
import os
import glob
import hashlib
from datetime import datetime

REGISTRY_FILE = os.path.join('arena', 'registry.json')

def load_registry(force_rebuild=False):
    if not force_rebuild and os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return rebuild_registry()

def save_registry(registry):
    registry['last_update'] = datetime.utcnow().isoformat()
    os.makedirs('arena', exist_ok=True)
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)

def compute_players_hash(players):
    """Копия функции из fetch_arena для синхронизации логики хэширования."""
    sorted_players = sorted(players, key=lambda p: p.get('userID', 0))
    hash_data = []
    for p in sorted_players:
        ps = p.get('profileState', {})
        hash_data.append(
            f"{p.get('userID')}:{p.get('rating')}:"
            f"{ps.get('winCount',0)}:{ps.get('defeatCount',0)}:"
            f"{p.get('power','0')}"
        )
    return hashlib.md5("|".join(hash_data).encode()).hexdigest()

def load_clan_members():
    db_path = os.path.join('clan_monitor', 'members_name_db.json')
    if not os.path.exists(db_path):
        return {}
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {uid: info.get('nick', 'Unknown') for uid, info in data.items()}
    except:
        return {}

def rebuild_registry():
    print("[REGISTRY] Rebuilding arena registry from all files (Slow mode)...")
    reg = {
        "known_users": {}, # userID (str) -> nickname
        "snapshots": {},   # filename -> content_hash
        "last_update": None
    }
    
    snapshot_files = sorted(glob.glob(os.path.join('arena', 'snapshots', 'arena_*.json')))
    for fpath in snapshot_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ОЧЕНЬ ВАЖНО: считаем хэш именно так, как это делает fetch_arena
                c_hash = data.get('content_hash')
                if not c_hash and 'players' in data:
                    c_hash = compute_players_hash(data['players'])
                
                reg['snapshots'][fname] = c_hash
                for p in data.get('players', []):
                    uid = str(p['userID'])
                    nick = p.get('profileState', {}).get('nickname', 'Unknown')
                    reg['known_users'][uid] = nick
        except:
            print(f"[REGISTRY] Warning: Failed to read {fname}")

    # Add clan members with lower priority
    clan_members = load_clan_members()
    for uid, nick in clan_members.items():
        if uid not in reg['known_users']:
            reg['known_users'][uid] = nick

    squads_base = os.path.join('arena', 'squads')
    if os.path.exists(squads_base):
        for uid_dir in os.listdir(squads_base):
            if uid_dir.isdigit() and uid_dir not in reg['known_users']:
                hist_path = os.path.join(squads_base, uid_dir, 'history.json')
                if os.path.exists(hist_path):
                    try:
                        with open(hist_path, 'r', encoding='utf-8') as f:
                            hist = json.load(f)
                            if hist:
                                # Можно вытянуть ник из истории если нужно
                                pass
                    except: pass
    
    save_registry(reg)
    print(f"[REGISTRY] Success: {len(reg['known_users'])} users, {len(reg['snapshots'])} snapshots.")
    return reg

def update_registry_with_snapshot(fname, content_hash, players):
    reg = load_registry()
    reg['snapshots'][fname] = content_hash
    for p in players:
        uid = str(p['userID'])
        nick = p.get('profileState', {}).get('nickname', 'Unknown')
        reg['known_users'][uid] = nick
    save_registry(reg)


def register_user(uid, nickname):
    reg = load_registry()
    known = reg.get('known_users', {})
    uid_str = str(uid)
    nick_clean = nickname.strip()
    
    pseudo_uid_to_remove = None
    for existing_uid, existing_nick in known.items():
        if int(existing_uid) < 0 and existing_nick.lower() == nick_clean.lower():
            pseudo_uid_to_remove = existing_uid
            break
            
    if pseudo_uid_to_remove:
        print(f"Migrating phantom user {nick_clean} (pseudo UID {pseudo_uid_to_remove}) to real UID {uid_str}")
        old_squad_dir = os.path.join('arena', 'squads', pseudo_uid_to_remove)
        new_squad_dir = os.path.join('arena', 'squads', uid_str)
        if os.path.exists(old_squad_dir):
            os.makedirs(os.path.dirname(new_squad_dir), exist_ok=True)
            if os.path.exists(new_squad_dir):
                try:
                    old_history = []
                    with open(os.path.join(old_squad_dir, 'profile_history.json'), 'r', encoding='utf-8') as f:
                        old_history = json.load(f)
                    new_history = []
                    new_hist_path = os.path.join(new_squad_dir, 'profile_history.json')
                    if os.path.exists(new_hist_path):
                        with open(new_hist_path, 'r', encoding='utf-8') as f:
                            new_history = json.load(f)
                    combined = old_history + new_history
                    seen_ts = set()
                    unique_comb = []
                    for h in sorted(combined, key=lambda x: x.get('timestamp', '')):
                        ts = h.get('timestamp')
                        if ts not in seen_ts:
                            seen_ts.add(ts)
                            unique_comb.append(h)
                    with open(new_hist_path, 'w', encoding='utf-8') as f:
                        json.dump(unique_comb, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Error merging squad history for migration: {e}")
            else:
                import shutil
                shutil.move(old_squad_dir, new_squad_dir)
            
            try:
                import shutil
                shutil.rmtree(old_squad_dir)
            except: pass
            
        if pseudo_uid_to_remove in known:
            del known[pseudo_uid_to_remove]
        
    if uid_str not in known or known[uid_str] != nick_clean:
        known[uid_str] = nick_clean
        reg['known_users'] = known
        save_registry(reg)
        return True
    return False
