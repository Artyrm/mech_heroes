import math
import random
import sys

opponents_data = {
    'x3': {'rating': 4503, 'winrate': 0.50, 'unlimited': True},
    'LordDragon': {'rating': 4456, 'winrate': 0.0, 'unlimited': False},
    'Propovednik': {'rating': 4432, 'winrate': 0.60, 'unlimited': True},
    'Shark': {'rating': 4262, 'winrate': 0.667, 'unlimited': True},
    'Knyaz': {'rating': 4234, 'winrate': 0.818, 'unlimited': True},
    'unc1e_Sam': {'rating': 4227, 'winrate': 0.889, 'unlimited': True},
    'Tranduil': {'rating': 4215, 'winrate': 1.0, 'unlimited': False}, # 100% винрейт, всегда доступен
    'Semen 444': {'rating': 4193, 'winrate': 0.70, 'unlimited': False}, # 70% винрейт, всегда доступен
    'Dikarius': {'rating': 4171, 'winrate': 0.70, 'unlimited': True},
    'RaRik': {'rating': 4169, 'winrate': 0.923, 'unlimited': False}, # Доступен долго
    'no_name': {'rating': 4163, 'winrate': 0.50, 'unlimited': True},
    'Mmv': {'rating': 4156, 'winrate': 0.88, 'unlimited': True},
    'Hunter': {'rating': 4150, 'winrate': 0.875, 'unlimited': True},
    'Nastoyki': {'rating': 4147, 'winrate': 0.833, 'unlimited': True},
    'tetka': {'rating': 4360, 'winrate': 0.208, 'unlimited': False},
    'Uksus': {'rating': 4300, 'winrate': 0.312, 'unlimited': False},
    'Quack': {'rating': 4281, 'winrate': 0.45, 'unlimited': True},
    'meshher': {'rating': 4226, 'winrate': 0.565, 'unlimited': False},
    'acdc': {'rating': 4211, 'winrate': 0.277, 'unlimited': False},
    'CDV': {'rating': 4210, 'winrate': 0.375, 'unlimited': False},
    'di': {'rating': 4204, 'winrate': 0.538, 'unlimited': False},
    'Strel': {'rating': 4159, 'winrate': 0.288, 'unlimited': False},
    'Multik': {'rating': 4145, 'winrate': 0.50, 'unlimited': False},
    'Firewall': {'rating': 4142, 'winrate': 0.538, 'unlimited': False},
    'Shagger': {'rating': 4139, 'winrate': 0.60, 'unlimited': False},
    'Hefastagon': {'rating': 4132, 'winrate': 0.50, 'unlimited': False}
}

def calc_elo_changes(player_rating, opp_rating):
    diff = opp_rating - player_rating
    step = math.trunc(diff / 20)
    win_points = max(1, 10 + step)
    loss_points = min(-1, -10 + step)
    return win_points, loss_points

def run_simulation(total_battles=100, num_sims=5000):
    final_player_ratings = []
    final_x3_ratings = []
    overtake_count = 0
    
    total_fought = {}
    total_won = {}
    demo_log = []
    
    print(f"\n[1/2] Запуск демонстрации одиночного штурма по Закону Сохранения Якорей ({total_battles} боёв)...")
    
    for sim in range(num_sims):
        # Отрисовка ProgressBar
        if sim % 50 == 0 or sim == num_sims - 1:
            progress = int((sim / (num_sims - 1)) * 100)
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            sys.stdout.write(f"\r[2/2] Симуляция сценариев: [{bar}] {progress}% ({sim + 1}/{num_sims})")
            sys.stdout.flush()
            
        p_rating = 4222
        
        # Копируем состояние оппонентов
        opps = {}
        for name, d in opponents_data.items():
            opps[name] = {
                'rating': d['rating'],
                'starting_rating': d['rating'],
                'winrate': d['winrate'],
                'unlimited': d['unlimited']
            }
            
        # Квак ограничен до 3 победных боев (из-за нестабильности)
        opps['Quack']['wins_left'] = 3
        
        for step_idx in range(total_battles):
            battles_left = total_battles - step_idx
            allowed_targets = []
            
            # Условие разблокировки Трандуила (высотное оружие)
            use_tranduil = (battles_left <= 15) or (p_rating >= 4435)
            
            # Условие разблокировки Якорей (x3 и Проповедник)
            # Не трогаем их, пока не наберем 4350 ELO, чтобы не просадить их раньше времени
            use_anchors = (battles_left <= 45) or (p_rating >= 4350)
            
            for name, d in opps.items():
                if name == 'Tranduil' and not use_tranduil:
                    continue  # Трандуил в сейфе
                if name in ['x3', 'Propovednik'] and not use_anchors:
                    continue  # Якоря в сейфе
                
                # Поправка на погружение: лимитированный игрок не должен просесть более чем на 30 очков
                if not d['unlimited']:
                    # Для Квака проверяем лимит побед
                    if name == 'Quack' and opps['Quack']['wins_left'] <= 0:
                        continue
                    if d['rating'] < d['starting_rating'] - 30:
                        continue
                
                allowed_targets.append(name)
                
            if not allowed_targets:
                allowed_targets = [name for name, d in opps.items()]
                
            # Ищем цель с максимальным EV
            best_opp = None
            best_ev = -9999
            for name in allowed_targets:
                d = opps[name]
                win_pts, loss_pts = calc_elo_changes(p_rating, d['rating'])
                ev = d['winrate'] * win_pts + (1 - d['winrate']) * loss_pts
                if ev > best_ev:
                    best_ev = ev
                    best_opp = name
            
            opp = opps[best_opp]
            win_pts, loss_pts = calc_elo_changes(p_rating, opp['rating'])
            
            # Проведение боя
            is_win = random.random() < opp['winrate']
            change = win_pts if is_win else loss_pts
            
            # Записываем лог первой демонстрационной попытки
            if sim == 0:
                demo_log.append({
                    'Battle': step_idx + 1,
                    'Opponent': best_opp,
                    'Outcome': "WIN" if is_win else "LOSS",
                    'Change': change,
                    'Player ELO': p_rating + change,
                    'Opp ELO': opp['rating'] - change,
                    'Opp Sunk': opp['starting_rating'] - (opp['rating'] - change)
                })
                
            if is_win:
                p_rating += win_pts
                opp['rating'] -= win_pts
                if best_opp == 'Quack':
                    opps['Quack']['wins_left'] -= 1
                total_won[best_opp] = total_won.get(best_opp, 0) + 1
            else:
                p_rating += loss_pts
                opp['rating'] -= loss_pts
                
            total_fought[best_opp] = total_fought.get(best_opp, 0) + 1
            
        final_player_ratings.append(p_rating)
        final_x3_ratings.append(opps['x3']['rating'])
        
        # Условие победы: вы должны обойти LordDragon (4456) и итоговый рейтинг x3
        if p_rating > 4456 and p_rating > opps['x3']['rating']:
            overtake_count += 1
            
    # Вывод результатов в консоль
    print("\n" + "="*95)
    print(" ДЕМОНСТРАЦИОННЫЙ ХОД ШТУРМА (СЦЕНАРИЙ: ГРАВИТАЦИОННЫЙ ЛИФТ - 100 БИЛЕТОВ)")
    print("="*95)
    print(f"{'Бой':<4} | {'Противник':<15} | {'Исход':<6} | {'Изменение':<10} | {'Ваш ELO':<8} | {'ELO Врага':<8} | {'Просадка врага':<12}")
    print("-"*95)
    
    # Показываем ключевые фазы (начало, переход на лидеров, финальные 10 боев на резервах)
    for row in demo_log[:20]: # Фаза 1: Разгон на NPC
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | -{row['Opp Sunk']:.1f}")
    print("...")
    for row in demo_log[50:65]: # Фаза 2: Клинч с лидерами
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | -{row['Opp Sunk']:.1f}")
    print("...")
    for row in demo_log[-15:]: # Фаза 3: Финальный безопасный подъем на Трандуиле
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | -{row['Opp Sunk']:.1f}")
    print("="*95)
    
    avg_player = sum(final_player_ratings) / num_sims
    avg_x3 = sum(final_x3_ratings) / num_sims
    pct_overtake = (overtake_count / num_sims) * 100
    
    print("\n" + "="*65)
    print(f" ИТОГОВАЯ СТАТИСТИКА {num_sims} ШТУРМОВ (БИЛЕТОВ НА СЕССИЮ: {total_battles})")
    print("="*65)
    print(f"Ваш средний итоговый рейтинг:    {avg_player:.1f}")
    print(f"Худший исход (минимум):          {min(final_player_ratings)}")
    print(f"Лучший исход (максимум):         {max(final_player_ratings)}")
    print(f"Средний итоговый рейтинг x3:     {avg_x3:.1f}")
    print(f"Шанс занять ТОП-1 (>4456 и >x3):  {pct_overtake:.2f}%")
    print("-" * 65)
    print(f"{'Соперник':<18} | {'Ср. число боев':<16} | {'Ср. побед':<10}")
    print("-" * 65)
    
    sorted_opps = sorted(total_fought.items(), key=lambda x: x[1], reverse=True)
    for name, f_sum in sorted_opps:
        avg_f = f_sum / num_sims
        avg_w = total_won.get(name, 0) / num_sims
        if avg_f > 0.1:
            print(f"{name:<18} | {avg_f:<16.1f} | {avg_w:<10.1f}")
    print("=" * 65)

# Запуск оптимальной сессии на 100 билетов
run_simulation(total_battles=100, num_sims=5000)