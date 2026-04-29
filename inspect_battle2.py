import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\Ответ на init от сервера.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

history = data['data']['userState']['arena']['battlesHistory']
b = history[0]
stats = b['statistics']

print("=== TOP-LEVEL statistics KEYS ===")
for k, v in stats.items():
    if isinstance(v, dict):
        print(f"  {k}: dict ({len(v)} keys) -> {list(v.keys())}")
    elif isinstance(v, list):
        print(f"  {k}: list ({len(v)} items)")
    else:
        print(f"  {k}: {type(v).__name__} = {v}")

print()
print("=== our units (statistics -> ключи-числа = слоты нашей стороны) ===")
# числовые ключи = слоты юнитов нашей стороны
our_slots = {k: v for k, v in stats.items() if str(k).isdigit()}
for slot, unit_data in sorted(our_slots.items(), key=lambda x: int(x[0])):
    state = unit_data.get('state', {})
    unit_stats = unit_data.get('statistics', {})
    print(f"\n  Слот {slot}: {state.get('defId','?')} (lv{state.get('level','?')} ★{state.get('stars','?')}) [{state.get('unitType','?')}]")
    # снаряжение
    equip = state.get('equipables', {})
    if equip:
        for eid, eq in equip.items():
            print(f"    Gear: {eq.get('id','?')} lv{eq.get('level','?')}")
    # статистика боя этого юнита
    print(f"    dmgDone: {unit_stats.get('damageDone', '-')}")
    print(f"    hpLost:  {unit_stats.get('healthLost', '-')}")
    print(f"    hpHeal:  {unit_stats.get('healthHealed', '-')}")
    print(f"    kills:   {unit_stats.get('killsCount', '-')}")
    ach = unit_stats.get('achievements', [])
    if ach:
        print(f"    achievements: {ach}")

print()
print("=== enemy section ===")
enemy = stats.get('enemy', {})
print(f"  enemy keys: {list(enemy.keys())}")

# General нашей стороны
our_gen = stats.get('general', {})
print(f"\n=== our general ===")
if our_gen:
    print(f"  defId: {our_gen.get('defId','?')}")
    eq = our_gen.get('equipables', {})
    for eid, item in list(eq.items())[:4]:
        print(f"    Gear: {item.get('id','?')} lv{item.get('level','?')}")
else:
    print("  (пустой)")

# General врага
enemy_gen = enemy.get('general', {})
print(f"\n=== enemy general ===")
if enemy_gen:
    print(f"  defId: {enemy_gen.get('defId','?')}")
    eq = enemy_gen.get('equipables', {})
    for eid, item in list(eq.items())[:4]:
        print(f"    Gear: {item.get('id','?')} lv{item.get('level','?')}")

print()
print("=== enemy units (слоты) ===")
enemy_slots = {k: v for k, v in enemy.items() if str(k).isdigit()}
for slot, unit_data in sorted(enemy_slots.items(), key=lambda x: int(x[0])):
    state = unit_data.get('state', {})
    unit_stats = unit_data.get('statistics', {})
    print(f"  Слот {slot}: {state.get('defId','?')} (lv{state.get('level','?')} ★{state.get('stars','?')})")
    print(f"    dmgDone: {unit_stats.get('damageDone', '-')}")
    print(f"    hpLost:  {unit_stats.get('healthLost', '-')}")
    kills = unit_stats.get('killsCount')
    if kills:
        print(f"    kills:   {kills}")
