import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_str = "delta = int(b_data.get('ourRatingDelta', 0))"
new_str = "delta = int(b_data.get('ourRatingDelta', 0))\n            opp_rating = int(b_data.get('opponentRating', 0))"
text = text.replace(old_str, new_str)

old_dict = """battles.append({
                'dt': dt, 
                'is_win': delta > 0, 
                'is_attack': is_attack, 
                'delta': delta,"""

new_dict = """battles.append({
                'dt': dt, 
                'is_win': delta > 0, 
                'is_attack': is_attack, 
                'delta': delta,
                'opp_rating': opp_rating,"""

text = text.replace(old_dict, new_dict)

old_logic = """            arena_data['players'].append({
                'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else 0,
                'power': pe.get('power', 0) if pe else 0,"""

new_logic = """
            # Ищем последний известный рейтинг в боях, если pe нет
            fallback_rating = 0
            if not pe:
                timeline = player_timelines.get(nick, [])
                for b in reversed(timeline):
                    if b['dt'] <= snap_dt:
                        fallback_rating = b.get('opp_rating', 0)
                        break

            arena_data['players'].append({
                'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else fallback_rating,
                'power': pe.get('power', 0) if pe else 0,"""
                
text = text.replace(old_logic, new_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched generate_personal_stats.py!")
