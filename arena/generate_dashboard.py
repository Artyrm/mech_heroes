import json
import os
import glob
from datetime import datetime, timedelta

def parseInternalDate(s):
    """Parse server timestamp like '17/05/2026_10:58:41.0000' into datetime."""
    try:
        d, t = s.split('_')
        day, month, year = d.split('/')
        h, m, sec = t.split(':')
        sec = sec.split('.')[0]
        return datetime(int(year), int(month), int(day), int(h), int(m), int(sec))
    except:
        return datetime(1970, 1, 1)

def generate():
    snaps_dir = "arena/snapshots"
    template_path = "arena/reports/template.html"
    output_path = "arena/reports/dashboard.html"
    
    if not os.path.exists(template_path):
        print("Template not found!")
        return

    # Load all snapshots
    all_snaps = {}
    # Make sure we use a robust glob and sorting by modification time
    snap_files = sorted(glob.glob(os.path.join(snaps_dir, "arena_*.json")))
    
    if not snap_files:
        print(f"No snapshot files found in {snaps_dir}")
        return

    for f in snap_files:
        try:
            with open(f, 'r', encoding='utf-8') as sf:
                data = json.load(sf)
                if 'timestamp' in data and 'players' in data:
                    all_snaps[data['timestamp']] = data
                else:
                    print(f"Warning: {f} has invalid structure.")
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not all_snaps:
        print("No valid snapshots data found.")
        return

    # Find players with suppression core
    holders = set()
    for f in glob.glob('arena/squads/*/history.json'):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                history = json.load(file)
                if history:
                    latest = history[-1]
                    squad = latest.get('squad', {})
                    general = squad.get('general', {})
                    equipables = general.get('equipables', {})
                    if any(eq.get('id') == 'suppression_core' for eq in equipables.values()):
                        uid = os.path.basename(os.path.dirname(f))
                        holders.add(int(uid))
        except: pass

    # Mark players in all snapshots
    for snap in all_snaps.values():
        for p in snap.get('players', []):
            if int(p['userID']) in holders:
                p['hasSuppressionCore'] = True

    # Find players with squads
    users_with_squads = []
    for f in glob.glob('arena/squads/*/history.json'):
        uid = os.path.basename(os.path.dirname(f))
        users_with_squads.append(int(uid))

    # Collect ALL players ever seen across all snapshots
    all_players_ever = {}  # userID -> latest player data
    sorted_timestamps = sorted(all_snaps.keys(), key=lambda s: parseInternalDate(s))
    for ts in sorted_timestamps:
        snap = all_snaps[ts]
        for p in snap.get('players', []):
            uid = int(p['userID'])
            all_players_ever[uid] = p

    # Find players in the LATEST snapshot
    latest_ts = sorted_timestamps[-1] if sorted_timestamps else None
    current_ids = set()
    if latest_ts:
        for p in all_snaps[latest_ts].get('players', []):
            current_ids.add(int(p['userID']))

    # Construct dropped players
    dropped_players = []
    for uid, pdata in all_players_ever.items():
        if uid not in current_ids:
            p_copy = dict(pdata)
            p_copy['isDropped'] = True
            
            # Try to get the latest rating from history.json
            history_file = os.path.join('arena', 'squads', str(uid), 'history.json')
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as hf:
                        history = json.load(hf)
                        if history:
                            latest_entry = history[-1]
                            # In history, "power" was used to store arenaRating
                            p_copy['rating'] = int(latest_entry.get('power', p_copy.get('rating', 0)))
                except:
                    pass
                    
            if uid in holders:
                p_copy['hasSuppressionCore'] = True
            dropped_players.append(p_copy)

    # Sort dropped by rating descending
    dropped_players.sort(key=lambda p: int(p.get('rating', 0)), reverse=True)

    # Append dropped players to the LATEST snapshot
    if latest_ts and dropped_players:
        all_snaps[latest_ts]['players'].extend(dropped_players)

    # Read template
    with open(template_path, 'r', encoding='utf-8') as tf:
        html = tf.read()
    
    # Inject data as a JSON string
    data_json = json.dumps(all_snaps, ensure_ascii=False)
    html = html.replace('SNAPSHOTS_DATA', data_json)
    
    users_with_squads_json = json.dumps(users_with_squads)
    html = html.replace('USERS_WITH_SQUADS', users_with_squads_json)
    
    # Inject last check time (MSK)
    now_msk = datetime.utcnow() + timedelta(hours=3)
    now_str = now_msk.strftime("%d.%m.%Y %H:%M:%S МСК")
    html = html.replace('LAST_CHECK_TIME', now_str)
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as of:
        of.write(html)
        
    print(f"Dashboard generated: {output_path} with {len(all_snaps)} snapshots.")

if __name__ == "__main__":
    generate()
