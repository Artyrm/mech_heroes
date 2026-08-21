import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_str = "delta = int(b.get('ourRatingDelta', 0))"
new_str = "delta = int(b.get('ourRatingDelta', 0))\n            opp_rating = int(b.get('opponentRating', 0))"

if old_str in text:
    text = text.replace(old_str, new_str)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed opp_rating!")
else:
    print("Not found")
