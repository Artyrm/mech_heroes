import json
import os
from datetime import datetime, timezone

SNAPSHOTS_DIR = 'snapshots'

def check():
    # Файл за 29 апреля (финал)
    f29 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-29_23-59.json')
    # Файл за 30 апреля (наш новый финал)
    f30 = os.path.join(SNAPSHOTS_DIR, 'points_utc_2026-04-30_20-59.json')
    
    if not os.path.exists(f29) or not os.path.exists(f30):
        print(f"Ошибка: Файлы не найдены. f29: {os.path.exists(f29)}, f30: {os.path.exists(f30)}")
        return

    with open(f29, 'r') as f: d29 = json.load(f).get('pts', {})
    with open(f30, 'r') as f: d30 = json.load(f).get('pts', {})
    
    uid = "371651" # Твой аккаунт (судя по цифрам)
    v29 = d29.get(uid, 0)
    v30 = d30.get(uid, 0)
    
    print(f"Игрок {uid}:")
    print(f"  Очки на 29.04 (финал): {v29}")
    print(f"  Очки на 30.04 (наш новый финал): {v30}")
    print(f"  Разница (рост за 30.04): {v30 - v29}")

if __name__ == "__main__":
    check()
