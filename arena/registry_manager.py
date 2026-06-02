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
