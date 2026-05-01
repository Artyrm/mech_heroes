import requests
import json
import os

CONFIG_FILE = 'clan_monitor/config.json'
CONF = json.load(open(CONFIG_FILE))
USER_ID, AUTH_KEY, VERSION = CONF['USER_ID'], CONF['AUTH_KEY'], CONF['VERSION']
BASE_URL = f"https://tanks.ya.patternmasters.ru/{VERSION}"

def analyze_strel_battle():
    p1 = {"data": {"userID": USER_ID, "authKey": AUTH_KEY}, "locale": "ru", "platform": "YandexGamesDesktop", "requestId": 1, "version": VERSION}
    r = requests.post(f"{BASE_URL}/init?userid={USER_ID}", json=p1).json()
    
    arena = r.get("data", {}).get("userState", {}).get("arena", {})
    history = arena.get("battlesHistory", [])
    
    # Ищем последний бой со Strel
    target_battle = None
    for b in history:
        if b.get("nick") == "Strel":
            target_battle = b
            break
            
    if not target_battle:
        print("Бой со Strel не найден в последних 20 записях.")
        return

    # Сохраняем полный отчет
    with open('strel_full_battle_data.json', 'w', encoding='utf-8') as f:
        json.dump(target_battle, f, indent=2, ensure_ascii=False)
    
    print("--- АНАЛИТИКА БОЯ СО STREL ---")
    print(f"Время боя: {target_battle.get('fightTime')}")
    print(f"Рейтинг врага: {target_battle.get('opponentRating')}")
    delta = target_battle.get('ourRatingDelta')
    print(f"Итог для нас: {delta} очков ({'ПОБЕДА' if int(delta) > 0 else 'ПОРАЖЕНИЕ'})")
    
    stats = target_battle.get("statistics", {})
    enemy = stats.get("enemy", {})
    gen = enemy.get("general", {})
    units = enemy.get("units", {})
    
    print("\n--- ГЕРОЙ (ГЕНЕРАЛ) ВРАГА ---")
    print(f"ID: {gen.get('defId')}")
    # Экипировка героя
    equips = gen.get("equipables", {})
    if equips:
        for eid, edata in equips.items():
            print(f"  - {edata.get('id')} (Lvl: {edata.get('level')})")
    else:
        print("  (Нет экипировки или не отображается)")

    print("\n--- ЮНИТЫ ВРАГА ---")
    for slot, udata in units.items():
        state = udata.get("state", {})
        u_stats = udata.get("statistics", {})
        
        print(f"Слот {slot}: {state.get('defId')} | Lvl: {state.get('level')} | Stars: {state.get('stars')}")
        print(f"  Урон: {u_stats.get('damageDone', '0')} | Потеряно HP: {u_stats.get('healthLost', '0')}")
        
        # Предметы юнита
        u_equips = state.get("equipables", {})
        if u_equips:
            print("  Снаряжение:")
            for eid, edata in u_equips.items():
                sharpening = edata.get("sharpening", {})
                sharp_str = ", ".join([f"{k}:{v}" for k, v in sharpening.items()])
                print(f"    * {edata.get('id')} (Lvl: {edata.get('level')}) [Заточки: {sharp_str}]")

if __name__ == "__main__":
    analyze_strel_battle()
