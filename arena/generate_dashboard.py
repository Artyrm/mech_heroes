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

def parse_any_date(s):
    """Parse various date formats used in the system."""
    if not s: return datetime(1970, 1, 1)
    try:
        if 'T' in s: # YYYY-MM-DDTHH-MM-SS
            return datetime.strptime(s.split('.')[0], "%Y-%m-%dT%H-%M-%S")
        else: # DD/MM/YYYY_HH:MM:SS
            d, t = s.split('_')
            day, month, year = d.split('/')
            h, m, sec = t.split(':')
            return datetime(int(year), int(month), int(day), int(h), int(m), int(sec.split('.')[0]))
    except:
        return datetime(1970, 1, 1)

def get_rating_at(uid, target_ts, all_histories):
    """Find the best known rating for a player at a specific timestamp."""
    history = all_histories.get(uid, [])
    target_dt = parse_any_date(target_ts)
    best_rating = None
    for entry in history:
        if parse_any_date(entry["timestamp"]) <= target_dt:
            best_rating = int(entry.get('power', 0))
        else:
            break
    return best_rating

def generate():
    snaps_dir = "arena/snapshots"
    template_path = "arena/reports/template.html"
    output_path = "arena/reports/dashboard.html"
    
    if not os.path.exists(template_path):
        print("Template not found!")
        return

    # Load all snapshots
    all_snaps = {}
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
        except: pass
            
    if not all_snaps:
        print("No valid snapshots data found.")
        return

    # Load all player histories once
    all_histories = {}
    all_players_ever = {} # userID -> latest info
    for hf_path in glob.glob('arena/squads/*/history.json'):
        uid = int(os.path.basename(os.path.dirname(hf_path)))
        try:
            with open(hf_path, 'r', encoding='utf-8') as hf:
                history = json.load(hf)
                if history:
                    all_histories[uid] = history
                    latest = history[-1]
                    all_players_ever[uid] = {
                        'userID': uid,
                        'rating': latest.get('power', 0),
                        'profileState': {'nickname': os.path.basename(os.path.dirname(hf_path))},
                        'clanProfile': {'clanName': '-', 'clanTag': '-'}
                    }
        except: pass

    # Find players with squads & online history
    players_online_info = {}
    for uid_dir in os.listdir('arena/squads'):
        history_file = os.path.join('arena', 'squads', uid_dir, 'online_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    if history:
                        players_online_info[int(uid_dir)] = history[-1]
            except: pass

    # Find players with suppression core
    holders = set()
    for uid, history in all_histories.items():
        if history:
            latest = history[-1]
            equipables = latest.get('squad', {}).get('general', {}).get('equipables', {})
            if any(eq.get('id') == 'suppression_core' for eq in equipables.values()):
                holders.add(uid)

    # Collect ALL players ever seen
    sorted_timestamps = sorted(all_snaps.keys(), key=lambda x: parse_any_date(x))
    for ts in sorted_timestamps:
        for p in all_snaps[ts].get('players', []):
            all_players_ever[int(p['userID'])] = p

    # Process EVERY snapshot to include dropped players
    for ts in sorted_timestamps:
        snap = all_snaps[ts]
        current_uids = {int(p['userID']) for p in snap['players']}
        
        dropped_for_this_snap = []
        for uid, pdata in all_players_ever.items():
            if uid not in current_uids:
                rating = get_rating_at(uid, ts, all_histories)
                if rating is not None:
                    p_copy = dict(pdata)
                    p_copy['isDropped'] = True
                    p_copy['rating'] = rating
                    
                    if uid in all_histories and all_histories[uid]:
                        latest_hist = all_histories[uid][-1]
                        squad_info = latest_hist.get('squad', {})
                        p_copy['power'] = squad_info.get('general', {}).get('power', p_copy.get('power', 0))
                        if 'profileState' in latest_hist:
                             p_copy['profileState'] = latest_hist['profileState']
                    
                    dropped_for_this_snap.append(p_copy)
        
        # Apply global markers
        for p in snap['players'] + dropped_for_this_snap:
            uid = int(p['userID'])
            if uid in holders: p['hasSuppressionCore'] = True
            if uid in players_online_info: p['lastOnline'] = players_online_info[uid]

        # Add dropped players to the end
        dropped_for_this_snap.sort(key=lambda p: int(p.get('rating', 0)), reverse=True)
        snap['players'].extend(dropped_for_this_snap)

    users_with_squads = list(all_histories.keys())

    # Read template
    with open(template_path, 'r', encoding='utf-8') as tf:
        html = tf.read()
    
    # Inject data
    html = html.replace('SNAPSHOTS_DATA', json.dumps(all_snaps, ensure_ascii=False))
    html = html.replace('USERS_WITH_SQUADS', json.dumps(users_with_squads))
    
    # Inject last check time (MSK)
    now_msk = datetime.utcnow() + timedelta(hours=3)
    html = html.replace('LAST_CHECK_TIME', now_msk.strftime("%d.%m.%Y %H:%M:%S МСК"))
    
    with open(output_path, 'w', encoding='utf-8') as of:
        of.write(html)
        
    print(f"Dashboard generated: {output_path} with {len(all_snaps)} snapshots.")

if __name__ == "__main__":
    generate()
