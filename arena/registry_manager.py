import json
import os
import glob
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

def rebuild_registry():
    """Полное сканирование папок для первичного наполнения или принудительного обновления."""
    print("[REGISTRY] Rebuilding arena registry from all files (Slow mode)...")
    reg = {
        "known_users": {}, # userID (str) -> nickname
        "snapshots": {},   # filename -> content_hash
        "last_update": None
    }
    
    # 1. Сканируем снимки Арены
    snapshot_files = sorted(glob.glob(os.path.join('arena', 'snapshots', 'arena_*.json')))
    for fpath in snapshot_files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reg['snapshots'][fname] = data.get('content_hash', 'legacy')
                for p in data.get('players', []):
                    uid = str(p['userID'])
                    nick = p.get('profileState', {}).get('nickname', 'Unknown')
                    reg['known_users'][uid] = nick
        except:
            print(f"[REGISTRY] Warning: Failed to read {fname}")

    # 2. Дополняем из папок отрядов (для игроков, не попавших в Топ-50)
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
                                # Ищем ник в истории (если есть) или ставим дефолт
                                reg['known_users'][uid_dir] = 'Unknown'
                    except: pass
    
    save_registry(reg)
    print(f"[REGISTRY] Success: {len(reg['known_users'])} users, {len(reg['snapshots'])} snapshots.")
    return reg

def update_registry_with_snapshot(fname, content_hash, players):
    """Инкрементальное обновление при добавлении нового снимка."""
    reg = load_registry()
    reg['snapshots'][fname] = content_hash
    for p in players:
        uid = str(p['userID'])
        nick = p.get('profileState', {}).get('nickname', 'Unknown')
        reg['known_users'][uid] = nick
    save_registry(reg)
