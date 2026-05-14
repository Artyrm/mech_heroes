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
    except: return str(raw_lvl)

def clean_stat(s):
    if not s: return ""
    if s.startswith('e_'): s = s[2:]
    return s.replace('_sharpening', '').replace('sharpening_', '').replace('sharpening', '')

def get_mod_type(id_str):
    if not id_str: return "?"
    parts = id_str.split('_')
    stop_words = ['weapon', 'armor', 'engine', 'tracker', 'foot', 'ammunition', 'legendary']
    res = []
    for p in parts:
        if p in stop_words: break
        res.append(p)
    return '_'.join(res)

def aggregate_unit(u_data):
    if not u_data: return None
    
    # Handle both top-level (generals) and nested (units) structures
    state = u_data.get('state', {})
    def_id = u_data.get('defId') or state.get('defId', 'Unknown')
    level = u_data.get('level') or state.get('level', '?')
    stars = u_data.get('stars') or state.get('stars', '?')
    
    equip = u_data.get('equipables') or state.get('equipables', {})
    
    sharps = defaultdict(int)
    mods = set()
    for eq in equip.values():
        mods.add(get_mod_type(eq.get('id', '')))
        for t in eq.get('sharpening', {}).values():
            sharps[clean_stat(t)] += 1
            
    return {
        'defId': def_id,
        'lvl': format_level(level),
        'stars': stars,
        'mods': sorted(list(mods)),
        'sharps': dict(sharps),
        'raw_lvl': level
    }

def get_diff_summary(u1, u2):
    if not u1: return "Юнит добавлен."
    if not u2: return "Юнит убран."
    
    diffs = []
    if u1['lvl'] != u2['lvl']:
        diffs.append(f"Ур: {u1['lvl']} → {u2['lvl']}")
    if u1['stars'] != u2['stars']:
        diffs.append(f"★: {u1['stars']} → {u2['stars']}")
    
    # Compare sharpenings
    all_keys = set(u1['sharps'].keys()) | set(u2['sharps'].keys())
    sharp_diffs = []
    for k in sorted(all_keys):
        v1 = u1['sharps'].get(k, 0)
        v2 = u2['sharps'].get(k, 0)
        if v1 != v2:
            sharp_diffs.append(f"{k}: {v1}→{v2}")
    
    if sharp_diffs:
        diffs.append("Заточки: " + ", ".join(sharp_diffs))
        
    return "; ".join(diffs) if diffs else "Без изменений."

def get_battle_summary(path):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    stats = d.get('statistics', {})
    
    def get_side_data(side_key):
        side = stats.get(side_key, {})
        return {
            'gen': aggregate_unit(side.get('general', {})),
            'units': {slot: aggregate_unit(u) for slot, u in side.get('units', {}).items()}
        }

    return {
        'time': d.get('fightTime', '?'),
        'nick': d.get('nick', 'Оппонент'),
        'delta': d.get('ourRatingDelta', '0'),
        'player': get_side_data('player'),
        'enemy': get_side_data('enemy')
    }

def render_unit_comparison(u1, u2, title):
    if not u1 and not u2: return ""
    
    diff_text = get_diff_summary(u1, u2)
    is_diff = diff_text != "Без изменений."
    
    status_class = "diff" if is_diff else "same"
    diff_tag = f'<span class="changes-tag">ИЗМЕНЕНО</span>' if is_diff else ''
    
    def render_cell(u):
        if not u: return "<td>-</td>"
        sharps_str = ', '.join([f"{k}: {v}" for k, v in sorted(u['sharps'].items())])
        return f"""
            <td class="{status_class}">
                <div class="unit-name">{u['defId']} (Ур. {u['lvl']} | {u['stars']}★)</div>
                <div style="margin-top:5px;">
                    <span class="label">Модули:</span> <span class="val-mods">{', '.join(u['mods'])}</span><br>
                    <span class="label">Заточки:</span> <span class="val-sharps">{sharps_str}</span>
                </div>
            </td>
        """

    return f"""
        <tr class="unit-row"><td colspan="2" class="row-header">{title} {diff_tag}</td></tr>
        {f'<tr><td colspan="2" class="diff-summary">{diff_text}</td></tr>' if is_diff else ''}
        <tr>{render_cell(u1)}{render_cell(u2)}</tr>
    """

def generate_comparison_html(p1, p2, out_path):
    b1 = get_battle_summary(p1)
    b2 = get_battle_summary(p2)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Сравнение боев: {b2['nick']}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1f; color: #e0e0e0; padding: 20px; }}
            .container {{ max-width: 1400px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 30px; background: #25252d; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
            .comparison-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
            th, td {{ border: 1px solid #333; padding: 12px; vertical-align: top; }}
            th {{ background: #25252d; font-size: 1.1em; color: #fff; }}
            .row-header {{ background: #2d2d35; text-align: center; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1.5px; color: #aaa; }}
            .diff-summary {{ background: #4a1a1a; color: #ffabac; font-size: 0.9em; text-align: center; font-weight: bold; padding: 6px; border: 1px solid #f44336; }}
            .unit-name {{ font-weight: bold; color: #ffeb3b; font-size: 1.1em; }}
            .diff {{ background: #2c1e1e; border-left: 5px solid #f44336; }}
            .same {{ opacity: 0.7; }}
            .label {{ color: #888; font-size: 0.8em; text-transform: uppercase; }}
            .val-mods {{ color: #8bc34a; font-weight: bold; font-size: 0.9em; }}
            .val-sharps {{ color: #ffc107; font-weight: bold; font-size: 0.9em; }}
            .changes-tag {{ background: #f44336; color: #fff; font-size: 0.7em; padding: 2px 6px; border-radius: 3px; margin-left: 10px; vertical-align: middle; }}
            .section-title {{ background: #121217; padding: 15px; border-radius: 4px; margin: 30px 0 10px 0; border-bottom: 3px solid #00bcd4; color: #00bcd4; font-size: 1.6em; text-align: center; font-weight: bold; }}
            .win-marker {{ color: #4caf50; font-weight: bold; }}
            .lose-marker {{ color: #f44336; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Сравнение эволюции билдов</h1>
                <p>Бой 1: {b1['time']} (Дельта: <span class="win-marker">{b1['delta']}</span>) | Бой 2: {b2['time']} (Дельта: <span class="lose-marker">{b2['delta']}</span>)</p>
            </div>

            <div class="section-title">МОЙ ОТРЯД (Player)</div>
            <table class="comparison-table">
                <tr>
                    <th>Ранее ({b1['time']})</th>
                    <th>Сейчас ({b2['time']})</th>
                </tr>
                {render_unit_comparison(b1['player']['gen'], b2['player']['gen'], "ГЕНЕРАЛ")}
    """
    
    p1_u = {u['defId']: u for u in b1['player']['units'].values() if u}
    p2_u = {u['defId']: u for u in b2['player']['units'].values() if u}
    all_p_ids = sorted(list(set(p1_u.keys()) | set(p2_u.keys())))
    for uid in all_p_ids:
        html += render_unit_comparison(p1_u.get(uid), p2_u.get(uid), f"ЮНИТ: {uid.upper()}")

    html += f"""
            </table>

            <div class="section-title">ОТРЯД ВРАГА ({b2['nick']})</div>
            <table class="comparison-table">
                <tr>
                    <th>Ранее ({b1['time']})</th>
                    <th>Сейчас ({b2['time']})</th>
                </tr>
                {render_unit_comparison(b1['enemy']['gen'], b2['enemy']['gen'], "ГЕНЕРАЛ")}
    """

    e1_u = {u['defId']: u for u in b1['enemy']['units'].values() if u}
    e2_u = {u['defId']: u for u in b2['enemy']['units'].values() if u}
    all_e_ids = sorted(list(set(e1_u.keys()) | set(e2_u.keys())))
    for uid in all_e_ids:
        html += render_unit_comparison(e1_u.get(uid), e2_u.get(uid), f"ЮНИТ: {uid.upper()}")

    html += """
            </table>
        </div>
    </body>
    </html>
    """
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        generate_comparison_html(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python generate_comparison_report.py <json1> <json2> <output_html>")
