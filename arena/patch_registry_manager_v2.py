path = 'arena/registry_manager.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

migration_code = """
def register_user(uid, nickname):
    reg = load_registry()
    known = reg.get('known_users', {})
    uid_str = str(uid)
    nick_clean = nickname.strip()
    
    pseudo_uid_to_remove = None
    for existing_uid, existing_nick in known.items():
        if int(existing_uid) < 0 and existing_nick.lower() == nick_clean.lower():
            pseudo_uid_to_remove = existing_uid
            break
            
    if pseudo_uid_to_remove:
        print(f"Migrating phantom user {nick_clean} (pseudo UID {pseudo_uid_to_remove}) to real UID {uid_str}")
        old_squad_dir = os.path.join('arena', 'squads', pseudo_uid_to_remove)
        new_squad_dir = os.path.join('arena', 'squads', uid_str)
        if os.path.exists(old_squad_dir):
            os.makedirs(os.path.dirname(new_squad_dir), exist_ok=True)
            if os.path.exists(new_squad_dir):
                try:
                    old_history = []
                    with open(os.path.join(old_squad_dir, 'profile_history.json'), 'r', encoding='utf-8') as f:
                        old_history = json.load(f)
                    new_history = []
                    new_hist_path = os.path.join(new_squad_dir, 'profile_history.json')
                    if os.path.exists(new_hist_path):
                        with open(new_hist_path, 'r', encoding='utf-8') as f:
                            new_history = json.load(f)
                    combined = old_history + new_history
                    seen_ts = set()
                    unique_comb = []
                    for h in sorted(combined, key=lambda x: x.get('timestamp', '')):
                        ts = h.get('timestamp')
                        if ts not in seen_ts:
                            seen_ts.add(ts)
                            unique_comb.append(h)
                    with open(new_hist_path, 'w', encoding='utf-8') as f:
                        json.dump(unique_comb, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Error merging squad history for migration: {e}")
            else:
                import shutil
                shutil.move(old_squad_dir, new_squad_dir)
            
            try:
                import shutil
                shutil.rmtree(old_squad_dir)
            except: pass
            
        if pseudo_uid_to_remove in known:
            del known[pseudo_uid_to_remove]
        
    if uid_str not in known or known[uid_str] != nick_clean:
        known[uid_str] = nick_clean
        reg['known_users'] = known
        save_registry(reg)
        return True
    return False
"""

if "def register_user" not in text:
    text += "\n" + migration_code
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully appended register_user with migration logic to registry_manager.py!")
else:
    print("register_user already exists.")
