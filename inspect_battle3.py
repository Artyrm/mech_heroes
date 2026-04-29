import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\Ответ на init от сервера.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

history = data['data']['userState']['arena']['battlesHistory']
b = history[0]  # первый бой — ПОБЕДА над Князем
stats = b['statistics']

def print_units(units_dict, label):
    print(f"\n  --- {label} ---")
    for slot, unit_data in sorted(units_dict.items(), key=lambda x: int(x[0])):
        state = unit_data.get('state', {})
        us = unit_data.get('statistics', {})
        equip = state.get('equipables', {})
        equip_names = [f"{eq.get('id','?')}(lv{eq.get('level','?')})" for eq in equip.values()]
        print(f"  Слот {slot}: [{state.get('defId','?')}] lv{state.get('level','?')} ★{state.get('stars','?')}")
        print(f"           Снаряга: {', '.join(equip_names)}")
        dmg = us.get('damageDone', '-')
        hp_lost = us.get('healthLost', '-')
        hp_heal = us.get('healthHealed', '-')
        kills = us.get('killsCount', 0)
        ach = us.get('achievements', [])
        merged = us.get('mergedStatistics', [])
        print(f"           dmg={dmg}  hpLost={hp_lost}  heal={hp_heal}  kills={kills}")
        if ach:
            print(f"           achievements: {ach}")
        if merged:
            print(f"           mergedStats: {merged}")

def print_general(gen_dict, label):
    if not gen_dict:
        print(f"\n  --- {label}: (нет данных) ---")
        return
    print(f"\n  --- {label}: [{gen_dict.get('defId','?')}] ---")
    for eid, eq in gen_dict.get('equipables', {}).items():
        print(f"    {eq.get('id','?')} lv{eq.get('level','?')}")
    gen_stats = gen_dict.get('statistics', {})
    if gen_stats:
        print(f"    Stats: {gen_stats}")

for bi, b in enumerate(history[:2]):
    stats = b['statistics']
    delta = int(b['ourRatingDelta'])
    result = 'ПОБЕДА' if delta > 0 else 'ПОРАЖЕНИЕ'
    sign = '+' if delta > 0 else ''
    print()
    print("=" * 70)
    print(f"БОЙ #{bi+1} — {result} ({sign}{delta}) vs '{b['nick']}' (рейтинг {b['opponentRating']})")
    print(f"Время: {b['fightTime']}")
    print("=" * 70)

    player = stats.get('player', {})
    enemy = stats.get('enemy', {})

    print(f"\n  bestUnit нашей стороны: слот {stats.get('bestUnit','?')}")
    print(f"  bestUnit врага: слот {enemy.get('bestUnit','?')}")
    best_ach = stats.get('bestUnitAcievements', [])
    if best_ach:
        print(f"  Достижения нашего лучшего: {best_ach}")

    lost_units = player.get('lostUnits', [])
    print(f"\n  Наши потери (погибшие юниты): {lost_units if lost_units else 'нет'}")

    print_general(player.get('general', {}), "НАШ Генерал")
    print_general(enemy.get('general', {}), "Генерал ВРАГА")

    our_units = player.get('units', {})
    enemy_units = enemy.get('units', {})

    print_units(our_units, "НАШИ юниты")
    print_units(enemy_units, "Юниты ВРАГА")
