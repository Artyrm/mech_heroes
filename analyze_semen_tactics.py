import os
import glob
import re
from collections import Counter

battle_dir = r'battle_analytics/Семён 444'
files = glob.glob(os.path.join(battle_dir, 'battle_*.html'))

stats = []

# Регулярные выражения для поиска данных в HTML
# <div class="status win">ПОБЕДА (13 очков)</div>
re_status = re.compile(r'class="status\s+(win|lose)"', re.IGNORECASE)
# <span>Слот 1: bhramarah</span>
re_unit = re.compile(r'<span>Слот \d+: ([^<]+)</span>', re.IGNORECASE)

for f_path in files:
    try:
        with open(f_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Ищем результат
            status_match = re_status.search(content)
            if not status_match: continue
            is_win = status_match.group(1).lower() == 'win'
            
            # Ищем наш отряд (он идет первым в HTML)
            our_team_section = content.split('Наш Отряд')[1].split('Отряд Врага')[0]
            units = re_unit.findall(our_team_section)
            units = tuple(sorted([u.strip() for u in units])) # Сортируем для уникальности состава
            
            if units:
                stats.append({'units': units, 'win': is_win})
    except Exception as e:
        print(f"Error parsing {f_path}: {e}")

# Агрегация результатов
compositions = {}
for s in stats:
    u = s['units']
    if u not in compositions:
        compositions[u] = {'wins': 0, 'losses': 0}
    if s['win']:
        compositions[u]['wins'] += 1
    else:
        compositions[u]['losses'] += 1

print("\n--- АНАЛИЗ СОСТАВОВ ПРОТИВ СЕМЁН 444 ---")
# Сортируем по количеству боев
sorted_comps = sorted(compositions.items(), key=lambda x: (x[1]['wins'] + x[1]['losses']), reverse=True)

for units, res in sorted_comps:
    total = res['wins'] + res['losses']
    wr = (res['wins'] / total) * 100
    print(f"\nСостав: {', '.join(units)}")
    print(f"Боёв: {total} | Винрейт: {wr:.1f}% (Побед: {res['wins']}, Поражений: {res['losses']})")

if not sorted_comps:
    print("Не удалось извлечь данные о составах из файлов.")
