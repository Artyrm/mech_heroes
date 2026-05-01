import json

def analyze_last_strel():
    with open('current_init_dump.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    history = data.get("data", {}).get("userState", {}).get("arena", {}).get("battlesHistory", [])
    # Последний бой со Strel (индекс 19 в массиве из 20 элементов, т.к. №20 в списке)
    target_battle = history[19] 
    
    if target_battle.get("nick") != "Strel":
        # На всякий случай ищем по нику с конца
        for b in reversed(history):
            if b.get("nick") == "Strel":
                target_battle = b
                break

    with open('last_battle_strel_real.json', 'w', encoding='utf-8') as f:
        json.dump(target_battle, f, indent=2, ensure_ascii=False)
    
    print(f"--- АНАЛИЗ ПОСЛЕДНЕГО БОЯ СО STREL ({target_battle.get('fightTime')}) ---")
    stats = target_battle.get("statistics", {})
    enemy = stats.get("enemy", {})
    gen = enemy.get("general", {})
    units = enemy.get("units", {})
    
    print(f"Генерал врага: {gen.get('defId')} (Level: {gen.get('level')})")
    for slot, u in units.items():
        state = u.get("state", {})
        u_stats = u.get("statistics", {})
        print(f"Слот {slot}: {state.get('defId')} | Lvl: {state.get('level')} | Stars: {state.get('stars')}")
        equips = state.get("equipables", {})
        if equips:
            for eid, edata in equips.items():
                print(f"  - {edata.get('id')} (Lvl: {edata.get('level')})")

if __name__ == "__main__":
    analyze_last_strel()
