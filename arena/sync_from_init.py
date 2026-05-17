import json
import os
import glob
import hashlib
from datetime import datetime
import re

def compute_players_hash(players):
    """
    Вычисляет MD5-хэш по ключевым полям всех игроков.
    Если данные реально изменились (рейтинг, победы, поражения) —
    хэш будет другим, даже если lastUpdateTime совпадает.
    """
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
    """Загружает все существующие снимки и вычисляет их хэши."""
    hashes = {}
    for fpath in glob.glob(os.path.join(snapshots_dir, "arena_*.json")):
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'players' in data:
                h = compute_players_hash(data['players'])
                hashes[h] = os.path.basename(fpath)
        except:
            pass
    return hashes

def extract_file_timestamp(filename):
    """
    Извлекает временную метку из имени файла дампа.
    init_2026-05-17_05-18-34.json -> 2026-05-17T05-18-34
    """
    m = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(?:-\d{2})?)', filename)
    if m:
        return m.group(1).replace('_', 'T')
    return None

def sync():
    snapshots_dir = "arena/snapshots"
    os.makedirs(snapshots_dir, exist_ok=True)

    # Sources of init dumps
    sources = [
        "current_init_dump.json",
        "init_dumps/*.json",
        "Ответ на init от сервера.json"
    ]

    found_files = []
    for pattern in sources:
        found_files.extend(glob.glob(pattern))

    print(f"Found {len(found_files)} potential init dumps.")

    # Предварительно вычисляем хэши всех существующих снимков
    existing_hashes = load_existing_hashes(snapshots_dir)
    print(f"Existing snapshots: {len(existing_hashes)} (unique by content)")

    synced_count = 0
    skipped_identical = 0

    for file_path in found_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Navigate to arena data
            # Check different possible structures (some might be raw response, some parsed)
            d = data.get('data', data)
            user_state = d.get('userState', {})

            # If userState is a string (as seen in some logs)
            if isinstance(user_state, str):
                user_state = json.loads(user_state)

            arena = user_state.get('arena', {})
            leaderboards = arena.get('leaderboards', {})
            players = leaderboards.get('cachedPlayers', [])
            last_update = leaderboards.get('lastUpdateTime')

            if not players or not last_update:
                continue

            # Дедупликация по содержимому, а не по lastUpdateTime
            content_hash = compute_players_hash(players)

            if content_hash in existing_hashes:
                skipped_identical += 1
                continue

            # Данные реально новые — определяем имя файла.
            # Приоритет: временная метка из имени файла-источника (она точнее),
            # fallback — lastUpdateTime с сервера.
            file_ts = extract_file_timestamp(os.path.basename(file_path))
            if file_ts:
                safe_name = file_ts
            else:
                safe_name = last_update.replace('/', '-').replace(':', '-').replace('_', 'T').split('.')[0]

            target_path = os.path.join(snapshots_dir, f"arena_{safe_name}.json")

            # Если файл с таким именем уже есть (коллизия имён при разном содержимом) —
            # добавляем суффикс
            if os.path.exists(target_path):
                i = 2
                while os.path.exists(os.path.join(snapshots_dir, f"arena_{safe_name}_{i}.json")):
                    i += 1
                target_path = os.path.join(snapshots_dir, f"arena_{safe_name}_{i}.json")

            snapshot = {
                "timestamp": last_update,
                "source_file": os.path.basename(file_path),
                "content_hash": content_hash,
                "players": players
            }

            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)

            # Регистрируем новый хэш, чтобы не дублировать при обработке
            # следующих файлов в этом же прогоне
            existing_hashes[content_hash] = os.path.basename(target_path)

            print(f"Synced: {os.path.basename(file_path)} -> {os.path.basename(target_path)}")
            synced_count += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nTotal new snapshots synced: {synced_count}")
    if skipped_identical > 0:
        print(f"Skipped (identical content): {skipped_identical}")

if __name__ == "__main__":
    sync()
