import math
import random
import sys
import time

# Исходная база данных игроков на Арене
opponents_base = {
    'x3': {'rating': 4503, 'winrate': 0.50, 'is_npc': False, 'unlimited': True},
    'LordDragon': {'rating': 4456, 'winrate': 0.0, 'is_npc': False, 'unlimited': False},
    'Проповедник': {'rating': 4432, 'winrate': 0.60, 'is_npc': False, 'unlimited': True},
    'Хоббит': {'rating': 4362, 'winrate': 0.132, 'is_npc': False, 'unlimited': True}, 
    'тетка с веслом': {'rating': 4360, 'winrate': 0.208, 'is_npc': False, 'unlimited': False},
    'Уксус': {'rating': 4300, 'winrate': 0.312, 'is_npc': False, 'unlimited': False},
    'Quack': {'rating': 4281, 'winrate': 0.45, 'is_npc': False, 'unlimited': True},
    'Mike': {'rating': 4279, 'winrate': 0.0, 'is_npc': False, 'unlimited': False},
    'Shark': {'rating': 4262, 'winrate': 0.667, 'is_npc': False, 'unlimited': True},
    'Лиса': {'rating': 4246, 'winrate': 0.20, 'is_npc': False, 'unlimited': False},
    'Князь': {'rating': 4234, 'winrate': 0.818, 'is_npc': False, 'unlimited': True},
    'unc1e_Sam': {'rating': 4227, 'winrate': 0.889, 'is_npc': True, 'unlimited': True},
    'meshher': {'rating': 4226, 'winrate': 0.565, 'is_npc': False, 'unlimited': False},
    'Трандуил': {'rating': 4215, 'winrate': 1.0, 'is_npc': False, 'unlimited': False},
    'acdc': {'rating': 4211, 'winrate': 0.277, 'is_npc': False, 'unlimited': False},
    'CDV': {'rating': 4210, 'winrate': 0.375, 'is_npc': False, 'unlimited': False},
    'ди': {'rating': 4204, 'winrate': 0.538, 'is_npc': False, 'unlimited': False},
    'Семён 444': {'rating': 4193, 'winrate': 0.70, 'is_npc': False, 'unlimited': False},
    'ДИКАРИУС': {'rating': 4171, 'winrate': 0.70, 'is_npc': True, 'unlimited': True},
    'RaRik': {'rating': 4169, 'winrate': 0.923, 'is_npc': False, 'unlimited': False},
    '<без имени>': {'rating': 4163, 'winrate': 0.50, 'is_npc': True, 'unlimited': True},
    'Strel': {'rating': 4159, 'winrate': 0.288, 'is_npc': False, 'unlimited': False},
    'Mmv': {'rating': 4156, 'winrate': 0.88, 'is_npc': True, 'unlimited': True},
    'Hunter': {'rating': 4150, 'winrate': 0.875, 'is_npc': True, 'unlimited': True},
    'Flashserker': {'rating': 4150, 'winrate': 0.333, 'is_npc': True, 'unlimited': True},
    'Настойки лучше': {'rating': 4147, 'winrate': 0.833, 'is_npc': True, 'unlimited': True},
    'Multik': {'rating': 4145, 'winrate': 0.50, 'is_npc': False, 'unlimited': False},
    'ProStou': {'rating': 4143, 'winrate': 1.0, 'is_npc': False, 'unlimited': False},
    'Фаервол': {'rating': 4142, 'winrate': 0.538, 'is_npc': False, 'unlimited': False},
    'Shagger': {'rating': 4139, 'winrate': 0.60, 'is_npc': False, 'unlimited': False},
    '-=Hefas†agon=-': {'rating': 4132, 'winrate': 0.50, 'is_npc': False, 'unlimited': False}
}

def calc_elo_changes(player_rating, opp_rating):
    diff = opp_rating - player_rating
    step = math.trunc(diff / 20)
    win_points = max(1, 10 + step)
    loss_points = min(-1, -10 + step)
    return win_points, loss_points

def run_simulation(total_battles=80, num_sims=5000):
    final_player_ratings = []
    final_x3_ratings = []
    overtake_count = 0
    
    # Статистика боев
    total_fought = {}
    total_won = {}
    
    # Лог первого (демонстрационного) штурма
    demo_log = []
    
    print(f"\n[1/2] Запуск детальной демонстрации одиночного штурма ({total_battles} боёв)...")
    
    # Запускаем цикл симуляций
    for sim in range(num_sims):
        # Рисуем индикатор выполнения (ProgressBar) каждые 50 симуляций
        if sim % 50 == 0 or sim == num_sims - 1:
            progress = int((sim / (num_sims - 1)) * 100)
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            sys.stdout.write(f"\r[2/2] Симуляция сценариев: [{bar}] {progress}% ({sim + 1}/{num_sims})")
            sys.stdout.flush()
            
        p_rating = 4222
        
        # Глубокое копирование базы для этой конкретной симуляции
        opps = {}
        for name, d in opponents_base.items():
            opps[name] = {
                'rating': d['rating'],
                'winrate': d['winrate'],
                'is_npc': d['is_npc'],
                'unlimited': d['unlimited'],
                'wins_left': 999 if d['unlimited'] else 4
            }
            
        last_battle_was_risky_loss = False
        
        for step_idx in range(total_battles):
            allowed_targets = []
            is_phase_1 = (step_idx < 15)
            
            # 1. Определение режима боя (До боя)
            if is_phase_1:
                mode_used = "Разгон"
            elif last_battle_was_risky_loss:
                mode_used = "СЕЙВ"  # Включаем Recovery Mode
            else:
                mode_used = "Штурм"
                
            # 2. Фильтрация пула целей по режиму
            if mode_used == "Разгон":
                # Только NPC и игроки с винрейтом >= 75%
                for name, d in opps.items():
                    if d['wins_left'] > 0 and (d['is_npc'] or (not d['unlimited'] and d['winrate'] >= 0.75)):
                        allowed_targets.append(name)
            elif mode_used == "СЕЙВ":
                # Только надежные цели (винрейт >= 66%), без x3 и Проповедника
                for name, d in opps.items():
                    if d['wins_left'] > 0 and (d['is_npc'] or d['unlimited'] or d['winrate'] >= 0.66):
                        if name not in ['x3', 'Проповедник']:
                            allowed_targets.append(name)
            else:
                # Штурм: доступны абсолютно все, у кого остались лимиты побед
                for name, d in opps.items():
                    if d['wins_left'] > 0:
                        allowed_targets.append(name)
                        
            # Если пулы пусты (страховка), разрешаем любого доступного
            if not allowed_targets:
                allowed_targets = [name for name, d in opps.items() if d['wins_left'] > 0]
                
            # 3. Выбор цели с наилучшим EV из разрешенных
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
            
            # 4. Проведение боя
            is_win = random.random() < opp['winrate']
            change = win_pts if is_win else loss_pts
            
            # Записываем шаг для Демо-Лога (только из первой симуляции)
            if sim == 0:
                demo_log.append({
                    'Battle': step_idx + 1,
                    'Mode': mode_used,
                    'Opponent': best_opp,
                    'Outcome': "WIN" if is_win else "LOSS",
                    'Change': change,
                    'Player ELO': p_rating + change,
                    'Opp ELO': opp['rating'] - change
                })
                
            # Обновление показателей
            if is_win:
                p_rating += win_pts
                opp['rating'] -= win_pts
                if not opp['unlimited']:
                    opp['wins_left'] -= 1
                last_battle_was_risky_loss = False
                total_won[best_opp] = total_won.get(best_opp, 0) + 1
            else:
                p_rating += loss_pts
                opp['rating'] -= loss_pts
                # Если проиграли сложному оппоненту (винрейт < 65%), активируем сейв-режим
                if opp['winrate'] < 0.65:
                    last_battle_was_risky_loss = True
                else:
                    last_battle_was_risky_loss = False
                    
            total_fought[best_opp] = total_fought.get(best_opp, 0) + 1
            
        final_player_ratings.append(p_rating)
        final_x3_ratings.append(opps['x3']['rating'])
        if p_rating > opps['x3']['rating']:
            overtake_count += 1
            
    # --- ВЫВОД РЕЗУЛЬТАТОВ ---
    
    # 1. Печатаем демо-лог одного штурма
    print("\n" + "="*95)
    print(" ДЕМОНСТРАЦИОННЫЙ ХОД ОДНОГО ШТУРМА (СЦЕНАРИЙ: КИНЖАЛЬНЫЙ УДАР / РАКЕТА)")
    print("="*95)
    print(f"{'Бой':<4} | {'Режим':<10} | {'Противник':<18} | {'Исход':<6} | {'Изменение':<10} | {'Ваш ELO':<8} | {'ELO Врага':<8}")
    print("-"*95)
    
    # Показываем первые 20 боев (разгон + начало штурма) и последние 10 боев
    for row in demo_log[:20]:
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Mode']:<10} | {row['Opponent']:<18} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8}")
    print("...")
    for row in demo_log[-10:]:
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Mode']:<10} | {row['Opponent']:<18} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8}")
    print("="*95)
    
    # 2. Вывод итоговой статистики
    avg_player = sum(final_player_ratings) / num_sims
    avg_x3 = sum(final_x3_ratings) / num_sims
    pct_overtake = (overtake_count / num_sims) * 100
    
    print("\n" + "="*65)
    print(f" ИТОГОВАЯ СТАТИСТИКА {num_sims} ШТУРМОВ (ДЛИНА СЕССИИ: {total_battles} БОЁВ)")
    print("="*65)
    print(f"Ваш средний итоговый рейтинг:    {avg_player:.1f}")
    print(f"Худший исход (минимум):          {min(final_player_ratings)}")
    print(f"Лучший исход (максимум):         {max(final_player_ratings)}")
    print(f"Средний итоговый рейтинг x3:     {avg_x3:.1f}")
    print(f"Шанс занять ТОП-1:               {pct_overtake:.2f}%")
    print("-" * 65)
    print(f"{'Соперник':<18} | {'Ср. число боев':<16} | {'Ср. побед':<10}")
    print("-" * 65)
    
    sorted_opps = sorted(total_fought.items(), key=lambda x: x[1], reverse=True)
    for name, fought_sum in sorted_opps:
        avg_f = fought_sum / num_sims
        avg_w = total_won.get(name, 0) / num_sims
        if avg_f > 0.05:  # Показываем только тех, на кого ушло значимое число атак
            print(f"{name:<18} | {avg_f:<16.1f} | {avg_w:<10.1f}")
    print("=" * 65)

# Можете поменять число боев на 100 или 120 для проверки роста вероятностей
run_simulation(total_battles=80, num_sims=5000)