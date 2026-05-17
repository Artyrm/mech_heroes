"""
Миграция: переименование файлов из DD-MM-YYYYTHH-MM-SS в YYYY-MM-DDTHH-MM-SS
и обновление timestamps в history.json отрядов.
"""
import os
import re
import json
import glob

def convert_timestamp(old_ts):
    """Конвертирует DD-MM-YYYYTHH-MM-SS в YYYY-MM-DDTHH-MM-SS"""
    m = re.match(r'(\d{2})-(\d{2})-(\d{4})T(.*)', old_ts)
    if m:
        day, month, year, rest = m.groups()
        return f"{year}-{month}-{day}T{rest}"
    # Формат YYYY-MM-DDTHH-MM-SS (из sync_from_init) — оставляем как есть
    m2 = re.match(r'(\d{4})-(\d{2})-(\d{2})T(.*)', old_ts)
    if m2:
        return old_ts
    return old_ts

# 1. Переименование снимков Арены
snapshots_dir = "arena/snapshots"
for fname in os.listdir(snapshots_dir):
    if not fname.startswith("arena_") or not fname.endswith(".json"):
        continue
    # Извлекаем timestamp из имени файла
    ts_part = fname[len("arena_"):-len(".json")]
    new_ts = convert_timestamp(ts_part)
    if new_ts != ts_part:
        old_path = os.path.join(snapshots_dir, fname)
        new_fname = f"arena_{new_ts}.json"
        new_path = os.path.join(snapshots_dir, new_fname)
        print(f"Rename: {fname} -> {new_fname}")
        os.rename(old_path, new_path)

# 2. Обновление timestamps в history.json отрядов
squads_dir = "arena/squads"
for history_file in glob.glob(os.path.join(squads_dir, "*/history.json")):
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    changed = False
    for entry in history:
        old_ts = entry.get('timestamp', '')
        new_ts = convert_timestamp(old_ts)
        if new_ts != old_ts:
            entry['timestamp'] = new_ts
            changed = True
    
    if changed:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        uid = os.path.basename(os.path.dirname(history_file))
        print(f"Updated timestamps in squads/{uid}/history.json")

print("\nMigration complete.")
