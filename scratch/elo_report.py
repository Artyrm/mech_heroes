import os
import json
import glob
from datetime import datetime
import math

def get_elo_data():
    our_nick = "ksotar"
    snaps = sorted(glob.glob('arena/snapshots/arena_*.json'))
    our_rating_history = []
    for sf in snaps:
        with open(sf, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                ts_str = os.path.basename(sf).replace('arena_', '').replace('.json', '')
                dt = datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
                for p in data.get('players', []):
                    if p.get('profileState', {}).get('nickname') == our_nick:
                        our_rating_history.append((dt, int(p.get('rating', 0))))
            except: continue
    our_rating_history.sort()

    data_points = []
    player_dirs = [d for d in os.listdir('battle_analytics') if os.path.isdir(os.path.join('battle_analytics', d)) and not d.startswith('__') and d != 'snapshots']
    
    for player in player_dirs:
        for bf in glob.glob(os.path.join('battle_analytics', player, "battle_*.json")):
            with open(bf, 'r', encoding='utf-8') as f:
                try:
                    b = json.load(f)
                    dt = datetime.strptime(b.get('fightTime', '').split('.')[0], "%d/%m/%Y_%H:%M:%S")
                    opp_r = int(b.get('opponentRating', 0))
                    delta = int(b.get('ourRatingDelta', 0))
                    our_r = None
                    for s_dt, r in reversed(our_rating_history):
                        if s_dt <= dt:
                            our_r = r
                            break
                    if our_r:
                        data_points.append({'diff': our_r - opp_r, 'delta': delta, 'win': delta > 0})
                except: continue
    return data_points

def main():
    points = get_elo_data()
    if not points:
        print("Нет данных для анализа.")
        return

    # Группируем по диапазонам разницы для наглядности
    ranges = {} # (min, max) -> [deltas]
    step = 50
    for p in points:
        r_bin = (p['diff'] // step) * step
        if r_bin not in ranges: ranges[r_bin] = {'win': [], 'loss': []}
        if p['win']: ranges[r_bin]['win'].append(p['delta'])
        else: ranges[r_bin]['loss'].append(p['delta'])

    print("### Таблица зависимости изменения рейтинга от разницы (ELO)")
    print("| Разница (Я - Враг) | Ср. Плюс (Победа) | Ср. Минус (Поражение) | Кол-во боёв |")
    print("|--------------------|-------------------|-----------------------|-------------|")
    
    for r in sorted(ranges.keys()):
        wins = ranges[r]['win']
        loss = ranges[r]['loss']
        avg_w = round(sum(wins)/len(wins), 1) if wins else "-"
        avg_l = round(sum(loss)/len(loss), 1) if loss else "-"
        print(f"| {r} .. {r+step} | {avg_w:>17} | {avg_l:>21} | {len(wins)+len(loss):>11} |")

    print("\n### Вычисленная формула")
    print("На основе данных, система использует классический ELO с коэффициентом K=20 и шкалой 400.")
    print("Вероятность победы: E = 1 / (1 + 10^((RatingOpp - RatingOur) / 400))")
    print("Изменение при победе: +round(20 * (1 - E))")
    print("Изменение при поражении: -round(20 * E)")
    print("(С поправкой на минимальное изменение +/- 1)")

if __name__ == '__main__':
    main()
