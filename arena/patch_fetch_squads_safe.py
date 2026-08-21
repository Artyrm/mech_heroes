with open('arena/fetch_squads.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_str = "user_ids = [int(uid) for uid in reg['known_users'].keys()]"
new_str = "user_ids = [int(uid) for uid in reg['known_users'].keys() if int(uid) > 0]"

if old_str in text:
    text = text.replace(old_str, new_str)
    with open('arena/fetch_squads.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully patched fetch_squads.py to ignore negative UIDs.")
else:
    print("Already patched or target string not found.")
