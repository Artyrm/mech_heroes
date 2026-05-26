import os, json, logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# ==============================================================================
# HOBBIT ACTIVITY ANALYZER v2.0
# ==============================================================================

# Конфигурация
USER_ID = "227408"  # Хоббит
TZ_OFFSET = 3       # UTC -> MSK
PATHS = {
    "online_history": os.path.join("arena", "squads", USER_ID, "online_history.json"),
    "battles_dir": os.path.join("battle_analytics", "Хоббит"),
    "holidays": os.path.join("arena", "graphs", "holidays.json"),
    "output_graph": os.path.join("arena", "graphs", "hobbit_activity_final_v24.png")
}

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_holidays():
    if os.path.exists(PATHS["holidays"]):
        with open(PATHS["holidays"], "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()
def load_activity_data():
    """Собирает все временные метки активности из разных источников."""
    activity_points = set()

    # 1. Загрузка из истории сессий
    if os.path.exists(PATHS["online_history"]):
        try:
            with open(PATHS["online_history"], "r", encoding="utf-8") as f:
                history = json.load(f)
                for ts_str in history:
                    dt = datetime.strptime(ts_str, "%d/%m/%Y_%H:%M:%S.%f")
                    activity_points.add(dt + timedelta(hours=TZ_OFFSET))
        except Exception as e: logging.error(f"Ошибка чтения online_history: {e}")

    # 2. Загрузка из логов боев (фильтрация по "НАПАДЕНИЕ")
    if os.path.exists(PATHS["battles_dir"]):
        battle_files = [f for f in os.listdir(PATHS["battles_dir"]) if f.startswith("battle_") and f.endswith(".html")]
        for f_name in battle_files:
            file_path = os.path.join(PATHS["battles_dir"], f_name)
            try:
                # Читаем файл, чтобы проверить тип боя
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ищем метку ЗАЩИТА (Хоббит нападал на ksotar)
                    if "ЗАЩИТА" in content:
                        parts = f_name.split("_")
                        ts_str = f"{parts[1]}_{parts[2]}"
                        dt = datetime.strptime(ts_str, "%Y-%m-%d_%H-%M-%S")
                        activity_points.add(dt + timedelta(hours=TZ_OFFSET))
            except Exception:
                continue
    return activity_points
def generate_graph(points):
    if not points: return

    min_date = min(pt.date() for pt in points)
    max_date = max(pt.date() for pt in points)
    all_dates = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
    
    num_days = len(all_dates)
    days_map = {d: i for i, d in enumerate(all_dates)}
    
    grid = np.zeros((24, num_days))
    for pt in points:
        grid[pt.hour, days_map[pt.date()]] = 1

    grid_masked = np.ma.masked_where(grid == 0, grid)
    holidays = load_holidays()

    fig, ax = plt.subplots(figsize=(num_days * 0.4 + 4, 10))

    # 1. Данные (zorder=1)
    ax.pcolormesh(grid_masked, cmap='Blues', vmin=0, vmax=1.2, zorder=1)

    # 2. Выходные и праздники (zorder=2)
    for i, d in enumerate(all_dates):
        is_holiday = d.weekday() >= 5 or d.strftime("%Y-%m-%d") in holidays
        if is_holiday:
            rect = patches.Rectangle((i, 0), 1, 24, facecolor='salmon', alpha=0.3, zorder=2)
            ax.add_patch(rect)

    # 3. Сетка (zorder=3)
    for i in range(num_days + 1): ax.axvline(i, color='#808080', linewidth=0.5, zorder=3)
    for i in range(25): ax.axhline(i, color='#808080', linewidth=0.5, zorder=3)
    
    ax.set_ylim(0, 24)
    ax.set_xlim(0, num_days)
    ax.set_yticks(np.arange(24) + 0.5)
    ax.set_yticklabels([f"{h:02d}:00" for h in range(24)])
    ax.set_xticks(np.arange(num_days) + 0.5)
    ax.set_xticklabels([d.strftime("%d.%m") for d in all_dates], rotation=45, ha='right', fontsize=9)
    plt.title(f'Активность игрока {USER_ID} (MSK)', fontsize=16, pad=20)
    plt.ylabel('Час суток', fontsize=12)
    plt.tight_layout()
    plt.savefig(PATHS["output_graph"], dpi=150)
    logging.info(f"График сохранен: {PATHS['output_graph']}")

if __name__ == "__main__":
    generate_graph(load_activity_data())
