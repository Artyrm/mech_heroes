
import json
import os

# Let's inspect arena/snapshots/ for the raw structure as well
import glob
snap_files = glob.glob(os.path.join('arena', 'snapshots', 'arena_*.json'))
if snap_files:
    with open(snap_files[-1], 'r', encoding='utf-8') as f:
        snap = json.load(f)
        # Check first player structure
        if snap['players']:
            print(f"Structure of player in snapshot: {json.dumps(snap['players'][0], indent=2, ensure_ascii=False)}")
