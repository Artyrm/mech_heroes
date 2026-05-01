import json
import os

OLD_DUMP = 'Ответ на init от сервера_formatterd.json'
OUT_DIR = 'battle_analytics/Strel'
OLD_BATTLE_FILE = f'{OUT_DIR}/battle_2026-04-29.json'
NEW_BATTLE_FILE = f'{OUT_DIR}/battle_2026-05-01_22-29.json'

def extract_and_compare():
    if not os.path.exists(OLD_DUMP):
        print(f"Ошибка: Не найден старый дамп {OLD_DUMP}")
        return

    with open(OLD_DUMP, 'r', encoding='utf-8') as f:
        old_data = json.load(f)

    history = old_data.get('data', {}).get('userState', {}).get('arena', {}).get('battlesHistory', [])
    
    old_battle = None
    for b in history:
        if b.get('nick') == "Strel":
            # Ищем победный бой, он был одним из последних (или просто первый попавшийся, так как билд один)
            old_battle = b
            if int(b.get('ourRatingDelta', 0)) > 0:
                break # Если нашли победный - берём его

    if not old_battle:
        print("В старом дампе не найдено боев со Strel!")
        return

    with open(OLD_BATTLE_FILE, 'w', encoding='utf-8') as f:
        json.dump(old_battle, f, indent=2, ensure_ascii=False)
    
    print(f"Старый бой ({old_battle.get('fightTime')}) извлечен и сохранен!")

    # Сравнение с новым боем
    with open(NEW_BATTLE_FILE, 'r', encoding='utf-8') as f:
        new_battle = json.load(f)

    old_enemy = old_battle.get('statistics', {}).get('enemy', {}).get('units', {})
    new_enemy = new_battle.get('statistics', {}).get('enemy', {}).get('units', {})
    
    print("\n================ СРАВНЕНИЕ БИЛДА STREL (29 АПРЕЛЯ vs 1 МАЯ) ================\n")
    
    # Собираем словари юнитов по defId, чтобы слоты не мешали (если он их переставил)
    old_units_by_id = {u.get('state', {}).get('defId'): u for u in old_enemy.values()}
    new_units_by_id = {u.get('state', {}).get('defId'): u for u in new_enemy.values()}

    for defId, new_u in new_units_by_id.items():
        old_u = old_units_by_id.get(defId)
        new_state = new_u.get('state', {})
        print(f"--- Юнит: {defId.upper()} ---")
        
        if not old_u:
            print(f" НОВЫЙ ЮНИТ! В старом билде его не было.")
            print(f" Текущий уровень: {new_state.get('level')} | Звезды: {new_state.get('stars')}*")
            continue
            
        old_state = old_u.get('state', {})
        
        # Сравнение базовых статов
        old_lvl, new_lvl = old_state.get('level'), new_state.get('level')
        old_stars, new_stars = old_state.get('stars'), new_state.get('stars')
        
        level_diff = f"({old_lvl} -> {new_lvl})" if old_lvl != new_lvl else f"(без изменений: {new_lvl})"
        stars_diff = f"({old_stars}* -> {new_stars}*)" if old_stars != new_stars else f"(без изменений: {new_stars}*)"
        
        if old_lvl != new_lvl or old_stars != new_stars:
            print(f" ПРОКАЧКА ИЗМЕНИЛАСЬ:")
            print(f"   Уровень: {level_diff}")
            print(f"   Звезды:  {stars_diff}")
        else:
            print(f" Базовые статы: {level_diff}, {stars_diff}")

        # Сравнение экипировки (сравниваем по itemType: tracker, armor и тд, так как id (e.g. 1111) может меняться)
        # itemType не хранится отдельно удобно, но он есть в id предмета ("dodge_tracker_legendary" -> "tracker")
        def get_equips_mapped(state):
            eqs = {}
            for eid, eq in state.get('equipables', {}).items():
                eq_id = eq.get('id', '')
                part = "unknown"
                for p in ["weapon", "armor", "tracker", "engine", "foot", "ammunition"]:
                    if p in eq_id:
                        part = p
                        break
                eqs[part] = eq
            return eqs

        old_eqs = get_equips_mapped(old_state)
        new_eqs = get_equips_mapped(new_state)

        changes_found = False
        for part in ["weapon", "armor", "tracker", "engine", "foot", "ammunition"]:
            old_eq = old_eqs.get(part)
            new_eq = new_eqs.get(part)
            
            if old_eq and not new_eq:
                print(f"   [-] Предмет {part} был снят! (был: {old_eq.get('id')})")
                changes_found = True
            elif not old_eq and new_eq:
                print(f"   [+] Надет новый предмет {part}: {new_eq.get('id')} (Lvl {new_eq.get('level')})")
                changes_found = True
            elif old_eq and new_eq:
                if old_eq.get('id') != new_eq.get('id'):
                    print(f"   [~] Замена {part}: {old_eq.get('id')} -> {new_eq.get('id')}")
                    changes_found = True
                elif old_eq.get('level') != new_eq.get('level'):
                    print(f"   [^] Апгрейд {part}: {new_eq.get('id')} (Уровень {old_eq.get('level')} -> {new_eq.get('level')})")
                    changes_found = True
                else:
                    # Проверяем заточки
                    old_sharp = str(old_eq.get('sharpening', {}))
                    new_sharp = str(new_eq.get('sharpening', {}))
                    if old_sharp != new_sharp:
                        print(f"   [~] Перезаточка {part} ({new_eq.get('id')}):")
                        print(f"       Было: {old_eq.get('sharpening')}")
                        print(f"       Стало: {new_eq.get('sharpening')}")
                        changes_found = True
        
        if not changes_found:
            print("   Снаряжение не изменилось.")
        print()

if __name__ == "__main__":
    extract_and_compare()
