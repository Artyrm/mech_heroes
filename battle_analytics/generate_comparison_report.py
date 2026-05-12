import json
import os
import sys
from collections import defaultdict

def format_level(raw_lvl):
    try:
        raw = int(raw_lvl)
        lvl = (raw // 4) + 1
        step = (raw % 4) + 1
        return str(lvl) if step == 1 else f"{lvl}.{step}"
    except: return raw_lvl

def clean_stat(s):
    if s.startswith('e_'): s = s[2:]
    return s.replace('_sharpening', '').replace('sharpening_', '').replace('sharpening', '')

def get_mod_type(id_str):
    parts = id_str.split('_')
    stop = ['weapon', 'armor', 'engine', 'tracker', 'foot', 'ammunition', 'legendary']
    res = []
    for p in parts:
        if p in stop: break
        res.append(p)
    return '_'.join(res)

def aggregate_unit(u_data):
    state = u_data.get('state', {})
    equip = state.get('equipables', {}) if 'equipables' in state else u_data.get('equipables', {})
    sharps = defaultdict(int)
    mods = set()
    for eq in equip.values():
        mods.add(get_mod_type(eq.get('id', '')))
        for t in eq.get('sharpening', {}).values():
            sharps[clean_stat(t)] += 1
    return {
        'defId': state.get('defId', 'Unknown'),
        'lvl': format_level(state.get('level', '?')),
        'stars': state.get('stars', '?'),
        'mods': sorted(list(mods)),
        'sharps': dict(sharps)
    }

def get_battle_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    enemy = d.get('statistics', {}).get('enemy', {})
    res = {
        'time': d.get('fightTime', '?'),
        'gen': aggregate_unit(enemy.get('general', {})),
        'units': {slot: aggregate_unit(u) for slot, u in enemy.get('units', {}).items()}
    }
    return res

def generate_comparison_html(p1, p2, out_path):
    d1 = get_battle_data(p1)
    d2 = get_battle_data(p2)
    nick = "Хоббит"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Сравнение билда: {nick}</title>
        <style>
            body {{ font-family: sans-serif; background: #1e1e24; color: #fff; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .comparison-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
            th, td {{ border: 1px solid #444; padding: 15px; vertical-align: top; }}
            th {{ background: #2b2b36; font-size: 1.2em; }}
            .unit-row {{ background: #252530; }}
            .unit-name {{ font-weight: bold; color: #ffeb3b; font-size: 1.1em; }}
            .diff {{ background: #3b2c2c; border-left: 4px solid #f44336; }}
            .same {{ opacity: 0.7; }}
            .label {{ color: #9e9e9e; font-size: 0.9em; }}
            .val-mods {{ color: #8bc34a; font-weight: bold; }}
            .val-sharps {{ color: #ffc107; font-weight: bold; }}
            .changes-tag {{ background: #f44336; color: #fff; font-size: 0.7em; padding: 2px 5px; border-radius: 3px; margin-left: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Сравнение эволюции билда: {nick}</h1>
            <p>Слева: {d1['time']} | Справа: {d2['time']}</p>
        </div>
        <table class="comparison-table">
            <tr>
                <th>Старый билд (05.05)</th>
                <th>Текущий билд (Сегодня)</th>
            </tr>
    """

    def render_unit_cell(u):
        if not u or u.get('defId') == 'Unknown': return "<td>-</td>"
        sharps_str = ', '.join([f"{k}: {v}" for k, v in sorted(u['sharps'].items())])
        return f"""
            <td>
                <div class="unit-name">{u['defId']} (Ур. {u['lvl']} | {u['stars']}★)</div>
                <div style="margin-top:5px;">
                    <span class="label">Модули:</span> <span class="val-mods">{', '.join(u['mods'])}</span><br>
                    <span class="label">Заточки:</span> <span class="val-sharps">{sharps_str}</span>
                </div>
            </td>
        """

    # General
    is_diff = d1['gen']['sharps'] != d2['gen']['sharps'] or d1['gen']['lvl'] != d2['gen']['lvl']
    diff_tag = '<span class="changes-tag">ИЗМЕНЕНО</span>' if is_diff else ''
    html += f"<tr class='unit-row'><td colspan='2' style='text-align:center; background:#4a3b2c;'>ГЕНЕРАЛ {diff_tag}</td></tr>"
    html += f"<tr>{render_unit_cell(d1['gen'])}{render_unit_cell(d2['gen'])}</tr>"

    # Units (Match by defId for meaningful comparison)
    u1_by_id = {u['defId']: u for u in d1['units'].values()}
    u2_by_id = {u['defId']: u for u in d2['units'].values()}
    all_ids = sorted(list(set(u1_by_id.keys()) | set(u2_by_id.keys())))

    for uid in all_ids:
        u1 = u1_by_id.get(uid)
        u2 = u2_by_id.get(uid)
        is_diff = False
        if u1 and u2:
            is_diff = u1['sharps'] != u2['sharps'] or u1['lvl'] != u2['lvl'] or u1['stars'] != u2['stars']
        else:
            is_diff = True # Added or removed
            
        diff_tag = '<span class="changes-tag">ИЗМЕНЕНО</span>' if is_diff else ''
        html += f"<tr class='unit-row'><td colspan='2' style='text-align:center;'>ЮНИТ: {uid.upper()} {diff_tag}</td></tr>"
        
        c1 = render_unit_cell(u1)
        c2 = render_unit_cell(u2)
        if is_diff:
            # Highlight cells if different
            c1 = c1.replace('<td>', '<td class="diff">')
            c2 = c2.replace('<td>', '<td class="diff">')
        else:
            c1 = c1.replace('<td>', '<td class="same">')
            c2 = c2.replace('<td>', '<td class="same">')
            
        html += f"<tr>{c1}{c2}</tr>"

    html += """
        </table>
    </body>
    </html>
    """
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    p1 = sys.argv[1]
    p2 = sys.argv[2]
    out = sys.argv[3]
    generate_comparison_html(p1, p2, out)
