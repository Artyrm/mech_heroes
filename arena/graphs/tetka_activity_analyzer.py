import os, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# Конфигурация
USER_NAME = "tetka_s_veslom"
USER_ID = "44228"
TZ_OFFSET = 3       # UTC -> MSK
PATHS = {
    "online_history": os.path.join("arena", "squads", USER_ID, "online_history.json"),
    "battles_dir": os.path.join("battle_analytics", "тетка с веслом"),
    "holidays": os.path.join("arena", "graphs", "holidays.json"),
    "graphs_dir": os.path.join("arena", "graphs")
}

def load_data():
    online = set()
    battles = set()
    
    if os.path.exists(PATHS["online_history"]):
        with open(PATHS["online_history"], "r", encoding="utf-8") as f:
            for ts in json.load(f):
                dt = datetime.strptime(ts, "%d/%m/%Y_%H:%M:%S.%f") + timedelta(hours=TZ_OFFSET)
                online.add((dt.date(), dt.hour))
    
    if os.path.exists(PATHS["battles_dir"]):
        for f_name in os.listdir(PATHS["battles_dir"]):
            if f_name.startswith("battle_") and f_name.endswith(".html"):
                parts = f_name.split("_")
                try:
                    dt = datetime.strptime(f"{parts[1]}_{parts[2]}", "%Y-%m-%d_%H-%M-%S") + timedelta(hours=TZ_OFFSET)
                    battles.add((dt.date(), dt.hour))
                except: continue
    return online, battles

def load_holidays():
    if os.path.exists(PATHS["holidays"]):
        with open(PATHS["holidays"], "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def generate_graph():
    online, battles = load_data()
    all_known_dates = sorted(list(set([pt[0] for pt in online] + [pt[0] for pt in battles])))
    if not all_known_dates: 
        print(f"Нет данных активности для {USER_NAME}")
        return
    
    min_d, max_d = all_known_dates[0], all_known_dates[-1]
    all_dates = [min_d + timedelta(days=i) for i in range((max_d - min_d).days + 1)]
    
    num_days = len(all_dates)
    date_map = {d: i for i, d in enumerate(all_dates)}
    
    grid_all = np.logical_or(
        np.array([[1 if (all_dates[j], h) in online else 0 for j in range(num_days)] for h in range(24)]),
        np.array([[1 if (all_dates[j], h) in battles else 0 for j in range(num_days)] for h in range(24)])
    )

    fig, ax = plt.subplots(figsize=(num_days * 0.4 + 4, 10))
    holidays = load_holidays()
    for i, d in enumerate(all_dates):
        if d.weekday() >= 5 or d.strftime("%Y-%m-%d") in holidays:
            ax.add_patch(patches.Rectangle((i, 0), 1, 24, facecolor='salmon', alpha=0.3, zorder=0))

    ax.pcolormesh(grid_all, cmap='Blues', vmin=0, vmax=1, zorder=1)

    for i in range(num_days + 1): ax.axvline(i, color='#808080', linewidth=0.5, zorder=3)
    for i in range(25): ax.axhline(i, color='#808080', linewidth=0.5, zorder=3)

    ax.set_ylim(0, 24); ax.set_xlim(0, num_days)
    ax.set_yticks(np.arange(24) + 0.5); ax.set_yticklabels([f"{h:02d}:00" for h in range(24)])
    ax.set_xticks(np.arange(num_days) + 0.5); ax.set_xticklabels([d.strftime("%d.%m") for d in all_dates], rotation=45, ha='right', fontsize=9)
    plt.title(f'Активность {USER_NAME} (Синий - любая активность)', fontsize=14, pad=20)
    plt.tight_layout()

    out_path = os.path.join(PATHS["graphs_dir"], f"{USER_NAME}_activity_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.png")
    plt.savefig(out_path, dpi=150)
    print(f'График сохранен: {out_path}')

if __name__ == "__main__":
    generate_graph()
