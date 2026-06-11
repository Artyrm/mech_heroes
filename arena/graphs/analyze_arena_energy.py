import json, os
from datetime import datetime
import matplotlib.pyplot as plt

snapshots_dir = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\snapshots'
files = [f for f in os.listdir(snapshots_dir) if f.endswith('.json')]

print('Обработка снапшотов (ТОП-50 и ТОП-5)...')

def parse_ts(s):
    try:
        # Пытаемся распарсить ISO формат (YYYY-MM-DD)
        return datetime.strptime(s, '%Y-%m-%dT%H-%M-%S')
    except:
        try:
            # Пытаемся распарсить формат DD-MM-YYYY
            return datetime.strptime(s, '%d-%m-%YT%H-%M-%S')
        except:
            return None

# Собираем данные в список для последующей сортировки
raw_data = []

for f_name in files:
    file_path = os.path.join(snapshots_dir, f_name)
    try:
        ts_str = f_name.replace('arena_', '').replace('.json', '')
        dt = parse_ts(ts_str)
        if not dt:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            players = data.get("players", [])
            players.sort(key=lambda x: int(x.get("rating", 0)), reverse=True)
            
            energy = sum(int(p.get("rating", 0)) for p in players)
            top5 = [int(players[i].get("rating", 0)) if len(players) > i else None for i in range(5)]
            
            raw_data.append({
                "dt": dt,
                "energy": energy,
                "top5": top5
            })
    except Exception as e:
        print(f"Ошибка в файле {f_name}: {e}")
        continue

# Сортируем все данные строго ХРОНОЛОГИЧЕСКИ
raw_data.sort(key=lambda x: x["dt"])

# Распаковываем отсортированные данные
times = [x["dt"] for x in raw_data]
total_energy = [x["energy"] for x in raw_data]
top_5_ratings = {i+1: [x["top5"][i] for x in raw_data] for i in range(5)}

if not times:
    print("Данные не найдены!")
    exit()

# Визуализация
fig, ax1 = plt.subplots(figsize=(14, 7))

# Ось 1: Суммарная энергия
color1 = 'tab:blue'
ax1.set_xlabel('Дата')
ax1.set_ylabel('Суммарный рейтинг ТОП-50', color=color1, fontsize=12)
ax1.plot(times, total_energy, marker='o', linestyle='-', color=color1, label='Энергия ТОП-50', markersize=3)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, linestyle='--', alpha=0.5)

# Ось 2: Рейтинги 1-5 мест
ax2 = ax1.twinx()
colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#8A2BE2', '#DC143C'] # Золото, Серебро, Бронза и т.д.
for i in range(1, 6):
    ax2.plot(times, top_5_ratings[i], linestyle='--', label=f'Место {i}', color=colors[i-1])

ax2.set_ylabel('Рейтинг ТОП-5', color='black', fontsize=12)
ax2.legend(loc='upper left')

plt.title('Динамика энергии системы и ТОП-5 игроков Арены (ХРОНОЛОГИЯ)', fontsize=16)
fig.tight_layout()

out_file = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\arena\graphs\arena_energy_and_top5.png'
plt.savefig(out_file, dpi=150)
print(f'График обновлен и исправлен: {out_file}')
