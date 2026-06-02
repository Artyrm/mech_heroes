import json
import os
import glob
import hashlib
from datetime import datetime
import re
import sys

def parse_file_ts(filename):
    """Извлекает метку времени из имени файла (init_YYYY-MM-DD_HH-MM-SS.json)."""
    m = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', filename)
    if m:
        try: return datetime.strptime(m.group(1), "%Y-%m-%d_%H-%M-%S")
        except: return datetime.min
    return datetime.min

def get_latest_snapshot_time(snapshots_dir):
    """Находит время последнего созданного снимка."""
    latest_dt = datetime.min
    for fpath in glob.glob(os.path.join(snapshots_dir, "arena_*.json")):
        fname = os.path.basename(fpath)
        # arena_YYYY-MM-DDTHH-MM-SS.json
        m = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})', fname)
        if m:
            try:
                dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H-%M-%S")
                if dt > latest_dt: latest_dt = dt
            except: pass
    return latest_dt

def compute_players_hash(players):
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

def load_existing_hashes(snapshots_dir):
    hashes = {}
    for fpath in glob.glob(os.path.join(snapshots_dir, "arena_*.json")):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'players' in data:
                h = compute_players_hash(data['players'])
                hashes[h] = os.path.basename(fpath)
        except: pass
    return hashes

def sync():
    snapshots_dir = "arena/snapshots"
    os.makedirs(snapshots_dir, exist_ok=True)
    update_history = "--update_history" in sys.argv

    # Последнее время снимка
    latest_snap_dt = get_latest_snapshot_time(snapshots_dir)
    print(f"Latest existing snapshot time: {latest_snap_dt}")

    # Sources of init dumps
    sources = ["current_init_dump.json", "init_dumps/*.json", "Ответ на init от сервера.json"]
    found_files = []
    for pattern in sources: found_files.extend(glob.glob(pattern))

    # ФИЛЬТРАЦИЯ по времени
    if not update_history:
        filtered_files = []
        for f in found_files:
            f_dt = parse_file_ts(os.path.basename(f))
            if f_dt > latest_snap_dt:
                filtered_files.append(f)
        found_files = filtered_files
        print(f"Incremental mode: Processing only {len(found_files)} files newer than {latest_snap_dt}.")
    else:
        print(f"Full scan mode: Found {len(found_files)} potential init dumps.")

    existing_hashes = load_existing_hashes(snapshots_dir)
    synced_count, skipped_identical = 0, 0

    for file_path in found_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            d = data.get('data', data)
            user_state = d.get('userState', {})
            if isinstance(user_state, str): user_state = json.loads(user_state)
            
            arena = user_state.get('arena', {})
            leaderboards = arena.get('leaderboards', {})
            players = leaderboards.get('cachedPlayers', [])
            last_update = leaderboards.get('lastUpdateTime')

            if not players or not last_update: continue

            content_hash = compute_players_hash(players)
            if content_hash in existing_hashes:
                skipped_identical += 1
                continue

            # Генерация нового имени файла
            safe_name = last_update.replace('/', '-').replace(':', '-').replace('_', 'T').split('.')[0]
            target_path = os.path.join(snapshots_dir, f"arena_{safe_name}.json")
            if os.path.exists(target_path):
                i = 2
                while os.path.exists(os.path.join(snapshots_dir, f"arena_{safe_name}_{i}.json")): i += 1
                target_path = os.path.join(snapshots_dir, f"arena_{safe_name}_{i}.json")

            snapshot = {"timestamp": last_update, "source_file": os.path.basename(file_path), "content_hash": content_hash, "players": players}
            with open(target_path, 'w', encoding='utf-8') as f: json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
            existing_hashes[content_hash] = os.path.basename(target_path)
            print(f"Synced: {os.path.basename(file_path)} -> {os.path.basename(target_path)}")
            synced_count += 1
        except Exception as e: print(f"Error processing {file_path}: {e}")

    print(f"\nTotal new snapshots synced: {synced_count}")
    if skipped_identical > 0: print(f"Skipped (identical content): {skipped_identical}")

if __name__ == "__main__":
    sync()
