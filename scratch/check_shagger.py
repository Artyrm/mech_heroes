import json
import glob
import os

files = sorted(glob.glob('arena/snapshots/arena_*.json'))
if not files:
    print("No snapshots found")
    exit()

f = files[-1]
print(f"Latest snap: {os.path.basename(f)}")

with open(f, 'r', encoding='utf-8') as file:
    d = json.load(file)

players = d.get('players', [])
shaggers = [p for p in players if 'Shagger' in p['profileState']['nickname']]

print(f"Found {len(shaggers)} players named Shagger")
for p in shaggers:
    uid = p['userID']
    nick = p['profileState']['nickname']
    has_history = os.path.exists(f"arena/squads/{uid}/history.json")
    print(f"Nick: {nick}, ID: {uid}, Has history file: {has_history}")

print("\nAll players in latest snap:")
for p in players[:5]: # Just top 5
    print(f"Rank: {p['rank']}, Nick: {p['profileState']['nickname']}, ID: {p['userID']}")
