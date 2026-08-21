import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = """        arena_data['players'].append({
            'userID': uid,
            'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else 0,
            'power': pe.get('power', 0) if pe else 0,
            'profileState': {"""

new_logic = """
        fallback_rating = 0
        nick = known_users.get(str(uid), str(uid))
        if not pe:
            timeline = player_timelines.get(nick, [])
            for b in reversed(timeline):
                if b['dt'] <= snap_dt:
                    fallback_rating = b.get('opp_rating', 0)
                    break

        arena_data['players'].append({
            'userID': uid,
            'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else fallback_rating,
            'power': pe.get('power', 0) if pe else 0,
            'profileState': {"""

text = text.replace(old_logic, new_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched generate_personal_stats.py missing uids!")
