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
    'Tranduil': {'rating': 4215, 'winrate': 1.0, 'unlimited': False}, # 100% презерв на финал!
    'Semen 444': {'rating': 4193, 'winrate': 0.70, 'unlimited': False}, # Сжигаем в начале!
    'Dikarius': {'rating': 4171, 'winrate': 0.70, 'unlimited': True},
    'RaRik': {'rating': 4169, 'winrate': 0.923, 'unlimited': False}, # Сжигаем в начале/середине!
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
    
    # В резерве на финал оставляем ТОЛЬКО 100% Трандуила. 
    # RaRik и Semen 444 разрешены к использованию на средних высотах.
    preserves = {'Tranduil'}
    
    total_fought = {}
    total_won = {}
    demo_log = []
    
    print(f"\n[1/2] Запуск симуляции штурма с автоматическим разрывом клинча ({total_battles} боёв)...")
    
    for sim in range(num_sims):
        if sim % 50 == 0 or sim == num_sims - 1:
            progress = int((sim / (num_sims - 1)) * 100)
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            sys.stdout.write(f"\r[2/2] Симуляция сценариев: [{bar}] {progress}% ({sim + 1}/{num_sims})")
            sys.stdout.flush()
            
        p_rating = 4222
        
        opps = {}
        for name, d in opponents_data.items():
            opps[name] = {
                'rating': d['rating'],
                'starting_rating': d['rating'],
                'winrate': d['winrate'],
                'unlimited': d['unlimited']
            }
            
        opps['Quack']['wins_left'] = 3
        
        x3_converged = False
        prop_converged = False
        
        for step_idx in range(total_battles):
            battles_left = total_battles - step_idx
            allowed_targets = []
            
            # 1. Авто-детектор плато (Схождение с лидерами)
            # Если мы приблизились к x3 ближе чем на 12 очков на высоте выше 4410 ELO - блокируем его!
            if abs(p_rating - opps['x3']['rating']) <= 12 and p_rating >= 4410:
                x3_converged = True
                
            # Если приблизились к Проповеднику на 10 очков на высоте выше 4410 ELO - блокируем его
            if abs(p_rating - opps['Propovednik']['rating']) <= 10 and p_rating >= 4410:
                prop_converged = True
            
            # Условия разблокировки высотного резерва (Трандуил)
            use_tranduil = (battles_left <= 15) or (p_rating >= 4435)
            
            # Не лезем на якоря, пока не наберем 4350 ELO, чтобы сберечь их высоту
            use_anchors = (battles_left <= 45) or (p_rating >= 4350)
            
            for name, d in opps.items():
                if name == 'Tranduil' and not use_tranduil:
                    continue  # Трандуил заперт
                if name in ['x3', 'Propovednik'] and not use_anchors:
                    continue  # Якоря заперты
                
                # Активный блок: если схождение достигнуто, выходим из дуэли!
                if name == 'x3' and x3_converged:
                    continue
                if name == 'Propovednik' and prop_converged:
                    continue
                
                if not d['unlimited']:
                    if name == 'Quack' and opps['Quack']['wins_left'] <= 0:
                        continue
                    if d['rating'] < d['starting_rating'] - 30:
                        continue
                
                allowed_targets.append(name)
                
            if not allowed_targets:
                allowed_targets = [name for name, d in opps.items() if d['unlimited'] or d['rating'] >= d['starting_rating'] - 30]
                
            # Считаем EV для всех разрешенных целей
            evs = {}
            max_ev = -9999
            for name in allowed_targets:
                d = opps[name]
                win_pts, loss_pts = calc_elo_changes(p_rating, d['rating'])
                ev = d['winrate'] * win_pts + (1 - d['winrate']) * loss_pts
                evs[name] = ev
                if ev > max_ev:
                    max_ev = ev
            
            # Чередуем близкие цели в пределах 1.5 очков (севооборот)
            candidates = [name for name, ev in evs.items() if (max_ev - ev) <= 1.5]
            best_opp = random.choice(candidates)
            
            opp = opps[best_opp]
            win_pts, loss_pts = calc_elo_changes(p_rating, opp['rating'])
            
            is_win = random.random() < opp['winrate']
            change = win_pts if is_win else loss_pts
            
            if sim == 0:
                demo_log.append({
                    'Battle': step_idx + 1,
                    'Opponent': best_opp,
                    'Outcome': "WIN" if is_win else "LOSS",
                    'Change': change,
                    'Player ELO': p_rating + change,
                    'Opp ELO': opp['rating'] - change,
                    'Opp Sunk': opp['starting_rating'] - (opp['rating'] - change),
                    'x3_blocked': x3_converged
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
        
        if p_rating > 4456 and p_rating > opps['x3']['rating']:
            overtake_count += 1
            
    print("\n" + "="*95)
    print(" ДЕМОНСТРАЦИОННЫЙ ХОД ШТУРМА (РАЗРЫВ КЛИНЧА - СЕССИЯ 100 БИЛЕТОВ)")
    print("="*95)
    print(f"{'Бой':<4} | {'Противник':<15} | {'Исход':<6} | {'Изменение':<10} | {'Ваш ELO':<8} | {'ELO Врага':<8} | {'Блок x3':<8}")
    print("-"*95)
    
    for row in demo_log[:20]: # Фаза 1: Сбалансированный разгон
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | {str(row['x3_blocked']):<8}")
    print("...")
    for row in demo_log[50:65]: # Фаза 2: Клинч и разрыв дуэли с x3
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | {str(row['x3_blocked']):<8}")
    print("...")
    for row in demo_log[-15:]: # Фаза 3: Прыжок через LordDragon на Трандуиле
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Opponent']:<15} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8} | {str(row['x3_blocked']):<8}")
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

run_simulation(total_battles=100, num_sims=5000)