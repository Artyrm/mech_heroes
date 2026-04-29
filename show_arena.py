import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\Ответ на init от сервера.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

arena = data['data']['userState']['arena']
history = arena['battlesHistory']
rating = arena['ratingState']['rating']
wins = arena['victories']
loses = arena['loses']
div = arena['division']

print(f"Всего боёв в истории (в ините): {len(history)}")
print(f"Победы всего: {wins}")
print(f"Поражения всего: {loses}")
print(f"W/L ratio: {round(int(wins)/(int(wins)+int(loses))*100, 1)}%")
print(f"Текущий рейтинг: {rating}")
print(f"Очки дивизиона: {div['arenaPoints']}")
print(f"Место в дивизионе (прошлое): {div['pastPlace']}")
print(f"Сброс дивизиона: {div['resetTime']}")
print()

for i, b in enumerate(history[:2]):
    delta = int(b.get('ourRatingDelta', '0'))
    result = 'ПОБЕДА  ✓' if delta > 0 else 'ПОРАЖЕНИЕ ✗'
    print(f"=== БОЙ #{i+1} — {result} ===")
    print(f"  Время: {b['fightTime']}")
    print(f"  Противник: '{b['nick']}'")
    print(f"  Роль противника в клане: {b['clanRole']}")
    print(f"  Рейтинг противника: {b['opponentRating']}")
    delta_str = str(delta)
    sign = '+' if delta > 0 else ''
    print(f"  Наше изменение рейтинга: {sign}{delta_str}")

    stats = b.get('statistics', {})
    our_general = stats.get('general', {})
    enemy = stats.get('enemy', {})
    enemy_general = enemy.get('general', {})
    our_ach = stats.get('bestUnitAcievements', [])

    print(f"  Наш генерал: {our_general.get('defId', '?')}")
    print(f"  Генерал врага: {enemy_general.get('defId', '?')}")
    print(f"  Наш лучший юнит (слот №): {stats.get('bestUnit', '?')}")
    print(f"  Достижения нашего лучшего юнита: {our_ach}")
    print(f"  Лучший юнит врага (слот №): {enemy.get('bestUnit', '?')}")

    # Аватар противника
    av = b.get('avatarConfiguration', {})
    print(f"  Аватар врага: голова={av.get('head','?')}, одежда={av.get('clothes','?')}")
    print()

print("=== ВСЕ 20 боёв (краткая сводка) ===")
print(f"{'#':>2}  {'Время':<30}  {'Противник':<20}  {'Рейтинг':>8}  {'Δ рейтинг':>10}  Итог")
for i, b in enumerate(history):
    delta = int(b.get('ourRatingDelta', '0'))
    result = 'WIN' if delta > 0 else 'LOSE'
    nick = b.get('nick', '?')
    print(f"{i+1:>2}  {b['fightTime']:<30}  {nick:<20}  {b['opponentRating']:>8}  {delta:>+10}  {result}")
