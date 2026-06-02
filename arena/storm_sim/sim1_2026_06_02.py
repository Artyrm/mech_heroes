import math
import random
import sys

# Полная база игроков сервера
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

def run_simulation(total_battles=100, num_sims=5000):
    final_player_ratings = []
    final_x3_ratings = []
    overtake_count = 0
    
    # Резервные "высотные катапульты" со 100% винрейтом
    preserves = ['Трандуил', 'ProStou', 'RaRik']
    
    total_fought = {}
    total_won = {}
    demo_log = []
    
    print(f"\n[1/2] Запуск детальной демонстрации одиночного штурма ({total_battles} боёв)...")
    
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
        for name, d in opponents_base.items():
            opps[name] = {
                'rating': d['rating'],
                'winrate': d['winrate'],
                'is_npc': d['is_npc'],
                'unlimited': d['unlimited'],
                'wins_left': 999 if d['unlimited'] else 4
            }
            
        # Ограничиваем Quack до 3 побед (из-за нестабильности его состава)
        opps['Quack']['wins_left'] = 3
        
        for step_idx in range(total_battles):
            progress_ratio = step_idx / total_battles
            allowed_targets = []
            
            # Разделение по фазам
            if progress_ratio < 0.25:
                # Фаза 1: Разгон (Низкие NPC + Квак до 3 побед). Резервы под строгим замком.
                mode = "Разгон"
                for name, d in opps.items():
                    if d['wins_left'] > 0 and name not in preserves and name not in ['x3', 'Проповедник']:
                        if d['is_npc'] or d['winrate'] >= 0.45:
                            allowed_targets.append(name)
            elif progress_ratio < 0.55:
                # Фаза 2: Веерный буст (Средние NPC + Князь + Шарк веером, чтобы не засадить их рейтинг)
                mode = "Буст"
                for name, d in opps.items():
                    if d['wins_left'] > 0 and name not in preserves and name not in ['x3', 'Проповедник']:
                        if d['is_npc'] or d['unlimited'] or d['winrate'] >= 0.60:
                            allowed_targets.append(name)
            elif progress_ratio < 0.85:
                # Фаза 3: Клинч с лидерами (Сближение с x3 и Проповедником на максимальной высоте)
                mode = "Клинч"
                allowed_targets = ['x3', 'Проповедник']
            else:
                # Фаза 4: Лазерный выстрел (Достаем из сейфа 100% лимиты, пробиваем 4456)
                mode = "Выстрел"
                for name in preserves:
                    if opps[name]['wins_left'] > 0:
                        allowed_targets.append(name)
                        
            if not allowed_targets:
                allowed_targets = [name for name, d in opps.items() if d['wins_left'] > 0]
                
            # Выбираем лучшего по текущему EV
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
            
            # Проводим бой
            is_win = random.random() < opp['winrate']
            change = win_pts if is_win else loss_pts
            
            if sim == 0:
                demo_log.append({
                    'Battle': step_idx + 1,
                    'Mode': mode,
                    'Opponent': best_opp,
                    'Outcome': "WIN" if is_win else "LOSS",
                    'Change': change,
                    'Player ELO': p_rating + change,
                    'Opp ELO': opp['rating'] - change
                })
                
            if is_win:
                p_rating += win_pts
                opp['rating'] -= win_pts  # Враг проседает при нашем выигрыше!
                if not opp['unlimited']:
                    opp['wins_left'] -= 1
                total_won[best_opp] = total_won.get(best_opp, 0) + 1
            else:
                p_rating += loss_pts
                opp['rating'] -= loss_pts  # Враг растет при нашем проигрыше
                
            total_fought[best_opp] = total_fought.get(best_opp, 0) + 1
            
        final_player_ratings.append(p_rating)
        final_x3_ratings.append(opps['x3']['rating'])
        
        # Условие победы: вы должны обойти LordDragon (4456) и итоговый рейтинг x3
        if p_rating > 4456 and p_rating > opps['x3']['rating']:
            overtake_count += 1
            
    # Вывод красивых результатов в терминал
    print("\n" + "="*95)
    print(" ДЕМОНСТРАЦИОННЫЙ ХОД ШТУРМА (СЦЕНАРИЙ: ГРАВИТАЦИОННЫЙ ЛИФТ)")
    print("="*95)
    print(f"{'Бой':<4} | {'Режим':<10} | {'Противник':<18} | {'Исход':<6} | {'Изменение':<10} | {'Ваш ELO':<8} | {'ELO Врага':<8}")
    print("-"*95)
    
    # Показываем ключевые моменты
    for row in demo_log[:25]: # Фаза 1 и начало Фазы 2
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Mode']:<10} | {row['Opponent']:<18} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8}")
    print("...")
    for row in demo_log[50:65]: # Фаза 3 (Клинч)
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Mode']:<10} | {row['Opponent']:<18} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8}")
    print("...")
    for row in demo_log[-10:]: # Решающие бои Фазы 4
        sign = "+" if row['Change'] >= 0 else ""
        print(f"{row['Battle']:<4} | {row['Mode']:<10} | {row['Opponent']:<18} | {row['Outcome']:<6} | {sign}{row['Change']:<8} | {row['Player ELO']:<8} | {row['Opp ELO']:<8}")
    print("="*95)
    
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
    print(f"Шанс занять ТОП-1 (>4456 и >x3):  {pct_overtake:.2f}%")
    print("-" * 65)
    print(f"{'Соперник':<18} | {'Ср. число боев':<16} | {'Ср. побед':<10}")
    print("-" * 65)
    
    sorted_opps = sorted(total_fought.items(), key=lambda x: x[1], reverse=True)
    for name, fought_sum in sorted_opps:
        avg_f = fought_sum / num_sims
        avg_w = total_won.get(name, 0) / num_sims
        if avg_f > 0.1:
            print(f"{name:<18} | {avg_f:<16.1f} | {avg_w:<10.1f}")
    print("=" * 65)

# Рекомендуемая длина сессии — 100-110 боев для максимальной реализации потенциала
run_simulation(total_battles=100, num_sims=5000)