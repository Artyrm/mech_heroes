import math
import random

# Базовые данные оппонентов
# is_npc: True для игроков без клана (фарм без ограничений)
# unlimited: True для тех, на кого нет ограничений по договоренности / механике
# winrate: реальные вероятности победы (включая 50% против x3 и 60% против Проповедника)
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

def run_simulation(total_battles=100, num_simulations=5000):
    final_player_ratings = []
    final_x3_ratings = []
    overtake_count = 0
    
    # Сбор статистики по боям
    total_fought = {}
    total_won = {}
    
    for _ in range(num_simulations):
        p_rating = 4222
        
        # Копируем состояние оппонентов для каждой симуляции отдельно
        # У лимитных игроков счетчик побед равен 4, у безлимитных — заглушка 999
        opps = {}
        for name, d in opponents_base.items():
            opps[name] = {
                'rating': d['rating'],
                'winrate': d['winrate'],
                'is_npc': d['is_npc'],
                'unlimited': d['unlimited'],
                'wins_left': 999 if d['unlimited'] else 4
            }
            
        for step_idx in range(total_battles):
            progress = step_idx / total_battles
            
            # Фильтруем доступных оппонентов согласно фазе
            allowed_targets = []
            for name, d in opps.items():
                if d['wins_left'] <= 0:
                    continue  # победы на этого игрока исчерпаны
                
                # ЭТАП 1: Фарм NPC и 100% целей на старте (первые 35% сессии)
                if progress < 0.35:
                    if d['is_npc'] or (not d['unlimited'] and d['winrate'] >= 0.75):
                        allowed_targets.append(name)
                
                # ЭТАП 2: Подключение средних лимитов и крепких безлимитов (до 70% сессии)
                elif progress < 0.70:
                    if d['is_npc'] or d['unlimited'] or d['winrate'] >= 0.50:
                        if name not in ['x3', 'Проповедник']:  # Рано для главных боссов
                            allowed_targets.append(name)
                
                # ЭТАП 3: Открываем все цели для решающего рывка
                else:
                    allowed_targets.append(name)
            
            # Страховочный фолбек: если на фазе целей не осталось, берем любого доступного
            if not allowed_targets:
                allowed_targets = [name for name, d in opps.items() if d['wins_left'] > 0]
            
            # Поиск цели с максимальным математическим ожиданием (EV)
            best_opp = None
            best_ev = -9999
            
            for name in allowed_targets:
                d = opps[name]
                win_pts, loss_pts = calc_elo_changes(p_rating, d['rating'])
                ev = d['winrate'] * win_pts + (1 - d['winrate']) * loss_pts
                if ev > best_ev:
                    best_ev = ev
                    best_opp = name
            
            if not best_opp:
                break  # Целей нет вообще (теоретически невозможно)
                
            opp = opps[best_opp]
            win_pts, loss_pts = calc_elo_changes(p_rating, opp['rating'])
            
            total_fought[best_opp] = total_fought.get(best_opp, 0) + 1
            
            # Симулируем исход боя
            if random.random() < opp['winrate']:
                p_rating += win_pts
                opp['rating'] -= win_pts
                if not opp['unlimited']:
                    opp['wins_left'] -= 1  # Лимит тратится только при победе!
                total_won[best_opp] = total_won.get(best_opp, 0) + 1
            else:
                p_rating += loss_pts
                opp['rating'] -= loss_pts
                
        final_player_ratings.append(p_rating)
        final_x3_ratings.append(opps['x3']['rating'])
        if p_rating > opps['x3']['rating']:
            overtake_count += 1
            
    # Вывод результатов
    avg_player = sum(final_player_ratings) / num_simulations
    avg_x3 = sum(final_x3_ratings) / num_simulations
    pct_overtake = (overtake_count / num_simulations) * 100
    
    print("=" * 60)
    print(f"СТАТИСТИКА ШТУРМА НА {total_battles} БОЕВ ({num_simulations} СИМУЛЯЦИЙ)")
    print("=" * 60)
    print(f"Ваш средний итоговый рейтинг:    {avg_player:.1f}")
    print(f"Худший исход (мин):              {min(final_player_ratings)}")
    print(f"Лучший исход (макс):             {max(final_player_ratings)}")
    print(f"Средний итоговый рейтинг x3:     {avg_x3:.1f}")
    print(f"Шанс занять ТОП-1:               {pct_overtake:.2f}%")
    print("-" * 60)
    print(f"{'Соперник':<18} | {'Ср. число боев':<16} | {'Ср. побед':<10}")
    print("-" * 60)
    
    # Сортируем по убыванию сыгранных боев
    sorted_opps = sorted(total_fought.items(), key=lambda x: x[1], reverse=True)
    for name, fought_sum in sorted_opps:
        avg_f = fought_sum / num_simulations
        avg_w = total_won.get(name, 0) / num_simulations
        if avg_f > 0.1:  # Выводим только тех, с кем провели хоть сколько-то боев
            print(f"{name:<18} | {avg_f:<16.1f} | {avg_w:<10.1f}")
    print("=" * 60)

# Пример запуска симуляции на 100 боев
run_simulation(total_battles=100)