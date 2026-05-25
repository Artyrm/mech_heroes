
import os
import json
from datetime import datetime, timedelta

file_path = 'clan_monitor/clan_accountant.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_block = """        for uid in players:
            daily_growths = [0] * 7
            presence = [False] * 7
            prev_day_end = 0
            
            for i in range(7):
                d_start = monday + timedelta(days=i)
                d_end = d_start + timedelta(days=1)
                day_snaps = sorted([s for s in sd if d_start <= s['time'] < d_end and uid in s['pts']], key=lambda x: x['time'])
                
                if not day_snaps:
                    daily_growths[i] = 0
                else:
                    vals = [s['pts'][uid] for s in day_snaps]
                    peak = max(vals)
                    if vals[-1] < peak * 0.5:
                        growth = (peak - prev_day_end) + vals[-1]
                    else:
                        growth = vals[-1] - prev_day_end
                    
                    daily_growths[i] = max(0, int(growth))
                    prev_day_end = vals[-1]
                
                d_str = d_start.strftime('%Y-%m-%d')
                sn_day = week['days'].get(d_str, [])
                ex = adj_db.get(d_str, {}).get(uid, [])
                if not isinstance(ex, list): ex = [ex]
                presence[i] = (any(uid in s['pts'] for s in sn_day) if sn_day else False) or bool(ex)
            
            pl_res[uid] = {'growths': daily_growths, 'total': sum(daily_growths), 'presence': presence, 'first_p': next((idx for idx, p in enumerate(presence) if p), 999), 'last_p': next((6-idx for idx, p in enumerate(reversed(presence)) if p), -1)}
"""

start_marker = '        for uid in players:'
end_marker = 'pl_res[uid] = {'
start_pos = content.find(start_marker)
end_pos = content.find(end_marker, start_pos)
end_pos = content.find(')', end_pos) + 1

new_content = content[:start_pos] + new_block + content[end_pos:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('OK')
