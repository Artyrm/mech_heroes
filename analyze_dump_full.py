import json
import os

DUMP_FILE = 'init_dumps/init_2026-05-22_12-55-06.json'

def analyze_dump():
    if not os.path.exists(DUMP_FILE):
        print(f"File not found: {DUMP_FILE}")
        return

    with open(DUMP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    arena = data.get('data', {}).get('userState', {}).get('arena', {})
    
    # 1. Анализ боев
    history = arena.get('battlesHistory', [])
    print(f"Total battles found: {len(history)}")
    if history:
        # Сортируем по fightTime (строковое сравнение для ISO-подобных форматов часто срабатывает, 
        # но тут DD/MM/YYYY_HH:MM:SS)
        # Преобразуем для корректной сортировки
        def get_time(b):
            t = b.get('fightTime', '00/00/0000_00:00:00')
            # Переводим в YYYYMMDD_HHMMSS
            parts = t.split('_')
            date_parts = parts[0].split('/')
            return f"{date_parts[2]}{date_parts[1]}{date_parts[0]}_{parts[1].replace(':', '')}"

        sorted_history = sorted(history, key=get_time, reverse=True)
        print(f"Latest battle: {sorted_history[0].get('fightTime')}")
        print(f"Oldest battle: {sorted_history[-1].get('fightTime')}")
        
        # Выведем 5 последних
        print("\nLast 5 battles:")
        for b in sorted_history[:5]:
            print(f"- {b.get('nick')}: {b.get('fightTime')}")

    # 2. Анализ Арены
    leaderboards = arena.get('leaderboards', {})
    print(f"\nArena LastUpdateTime: {leaderboards.get('lastUpdateTime')}")
    players = leaderboards.get('cachedPlayers', [])
    print(f"Total cached players: {len(players)}")

if __name__ == "__main__":
    analyze_dump()
