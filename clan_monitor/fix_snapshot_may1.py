import json
import os

RAW_FILE = 'clan_monitor/snapshots/2026-05-01/init_response.json'
SNAPSHOTS_DIR = 'clan_monitor/snapshots'

def convert_init_to_snapshot():
    if not os.path.exists(RAW_FILE):
        print(f"Ошибка: Файл {RAW_FILE} не найден.")
        return

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    data = full_data.get('data', {})
    
    # 1. Используем фиксированное время (конец дня 1 мая)
    timestamp_str = "2026-05-01_23-59"
    
    # 2. Извлекаем данные клана
    clan_state = data.get('clanData', {}).get('clanState', {})
    hier = clan_state.get('hierarchy', {})
    
    pts_map = {}
    
    # Лидер
    leader = hier.get('leader', {})
    l_member = leader.get('member', {})
    if l_member:
        pts_map[str(l_member.get('userId'))] = int(l_member.get('points', 0))
    
    # Слоты
    for slot in hier.get('slots', []):
        member = slot.get('member', {})
        if member:
            pts_map[str(member.get('userId'))] = int(member.get('points', 0))
            
    # Рейтинг клана
    clan_rating = clan_state.get('rating', 0)
    
    # 3. Формируем структуру снэпшота
    snapshot = {
        "pts": pts_map,
        "clanRating": clan_rating
    }
    
    output_filename = f"points_utc_{timestamp_str}.json"
    output_path = os.path.join(SNAPSHOTS_DIR, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
    print(f"Успех! Снэпшот сформирован: {output_path}")
    print(f"Установленное время: 2026-05-01 23:59 (Конец дня)")
    print(f"Рейтинг клана: {clan_rating}")
    print(f"Игроков в снэпшоте: {len(pts_map)}")

if __name__ == "__main__":
    convert_init_to_snapshot()
