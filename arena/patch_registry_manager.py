with open('arena/registry_manager.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Проверим, есть ли уже register_user с миграцией
if "pseudo_uid_to_remove" in text:
    print("Migration logic already in registry_manager.py")
else:
    # Заменим функцию register_user
    old_func = """def register_user(uid, nickname):
    registry = load_registry()
    known = registry.get('known_users', {})
    uid_str = str(uid)
    nick_clean = nickname.strip()
    if uid_str not in known or known[uid_str] != nick_clean:
        known[uid_str] = nick_clean
        registry['known_users'] = known
        save_registry(registry)
        return True
    return False"""

    new_func = """def register_user(uid, nickname):
    registry = load_registry()
    known = registry.get('known_users', {})
    uid_str = str(uid)
    nick_clean = nickname.strip()
    
    # Пытаемся найти, не был ли этот игрок фантомом (с отрицательным UID) с таким же ником
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
        registry['known_users'] = known
        save_registry(registry)
        return True
    return False"""

    if old_func in text:
        text = text.replace(old_func, new_func)
        with open('arena/registry_manager.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Successfully updated registry_manager.py with migration logic!")
    else:
        print("Could not find exact old_func match in registry_manager.py")
