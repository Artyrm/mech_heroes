import json, os
from datetime import datetime
import matplotlib.pyplot as plt

snapshots_dir = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\snapshots'
files = sorted([f for f in os.listdir(snapshots_dir) if f.endswith('.json')])

times = []
total_energy = []
top_5_ratings = {i: [] for i in range(1, 6)}

print('Обработка снапшотов (ТОП-50 и ТОП-5)...')

for f_name in files:
    file_path = os.path.join(snapshots_dir, f_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            players = data.get("players", [])
            # Сортируем игроков по рейтингу (если ранг не гарантирует порядок)
            players.sort(key=lambda x: int(x.get("rating", 0)), reverse=True)
            
            # Сумма энергии ТОП-50
            current_energy = sum(int(p.get("rating", 0)) for p in players)
            
            # Рейтинги ТОП-5
            for i in range(5):
                top_5_ratings[i+1].append(int(players[i].get("rating", 0)) if len(players) > i else None)
            
            ts_str = f_name.replace('arena_', '').replace('.json', '')
            dt = datetime.strptime(ts_str, '%Y-%m-%dT%H-%M-%S')
            times.append(dt)
            total_energy.append(current_energy)
    except Exception as e:
        print(f"Ошибка в файле {f_name}: {e}")
        continue

# Визуализация
fig, ax1 = plt.subplots(figsize=(14, 7))

# Ось 1: Суммарная энергия
color1 = 'tab:blue'
ax1.set_xlabel('Дата')
ax1.set_ylabel('Суммарный рейтинг ТОП-50', color=color1, fontsize=12)
ax1.plot(times, total_energy, marker='o', linestyle='-', color=color1, label='Энергия ТОП-50')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, linestyle='--', alpha=0.5)

# Ось 2: Рейтинги 1-5 мест
ax2 = ax1.twinx()
colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#8A2BE2', '#DC143C'] # Золото, Серебро, Бронза и т.д.
for i in range(1, 6):
    ax2.plot(times, top_5_ratings[i], linestyle='--', label=f'Место {i}', color=colors[i-1])

ax2.set_ylabel('Рейтинг ТОП-5', color='black', fontsize=12)
ax2.legend(loc='upper left')

plt.title('Динамика энергии системы и ТОП-5 игроков Арены', fontsize=16)
fig.tight_layout()

out_file = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\arena_energy_and_top5.png'
plt.savefig(out_file, dpi=150)
print(f'График сохранен: {out_file}')
