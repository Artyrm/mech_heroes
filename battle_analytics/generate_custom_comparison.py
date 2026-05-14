import json
import os
import sys
from collections import defaultdict

SLOT_ORDER = ['tracker', 'armor', 'weapon', 'engine', 'ammunition', 'foot']

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
    stop_words = SLOT_ORDER + ['legendary']
    res = []
    for p in parts:
        if p in stop_words: break
        res.append(p)
    return '_'.join(res)

def get_slot_name(id_str):
    for s in SLOT_ORDER:
        if s in id_str: return s
    return "other"

def aggregate_unit(u_data):
    if not u_data: return None
    state = u_data.get('state', {})
    def_id = u_data.get('defId') or state.get('defId', 'Unknown')
    level = u_data.get('level') or state.get('level', '?')
    stars = u_data.get('stars') or state.get('stars', '?')
    equip = u_data.get('equipables') or state.get('equipables', {})
    
    sharps = defaultdict(int)
    mods = set()
    slot_lvls = {}
    for eq in equip.values():
        eq_id = eq.get('id', '')
        slot = get_slot_name(eq_id)
        lvl = int(eq.get('level', 0))
        slot_lvls[slot] = lvl
        mods.add(get_mod_type(eq_id))
        for t in eq.get('sharpening', {}).values():
            sharps[clean_stat(t)] += 1
            
    ordered_lvls = [f"{s}: {slot_lvls[s]}" for s in SLOT_ORDER if s in slot_lvls]
    if slot_lvls and all(l == list(slot_lvls.values())[0] for l in slot_lvls.values()) and len(slot_lvls) == 6:
        eq_str = str(list(slot_lvls.values())[0])
    else:
        eq_str = ", ".join(ordered_lvls)
        
    return {
        'defId': def_id, 'lvl': format_level(level), 'stars': stars,
        'mods': sorted(list(mods)), 'sharps': dict(sharps),
        'eq_lvls_str': eq_str, 'slot_lvls': slot_lvls
    }

def get_diff_summary(u1, u2):
    if not u1: return "Добавлен."
    if not u2: return "Убран."
    diffs = []
    if u1['lvl'] != u2['lvl']: diffs.append(f"Ур: {u1['lvl']} → {u2['lvl']}")
    if u1['stars'] != u2['stars']: diffs.append(f"★: {u1['stars']} → {u2['stars']}")
    if u1['slot_lvls'] != u2['slot_lvls']: diffs.append(f"Экип: {u1['eq_lvls_str']} → {u2['eq_lvls_str']}")
    all_keys = set(u1['sharps'].keys()) | set(u2['sharps'].keys())
    sharp_diffs = [f"{k}: {u1['sharps'].get(k, 0)}→{u2['sharps'].get(k, 0)}" for k in sorted(all_keys) if u1['sharps'].get(k,0) != u2['sharps'].get(k,0)]
    if sharp_diffs: diffs.append("Заточки: " + ", ".join(sharp_diffs))
    return "; ".join(diffs) if diffs else "Без изменений."

def get_battle_summary(path, side_to_use='enemy'):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    side = d['statistics'].get(side_to_use, {})
    return {
        'time': d.get('fightTime', '?'),
        'nick': d.get('nick') if side_to_use == 'enemy' else 'Игрок',
        'gen': aggregate_unit(side.get('general', {})),
        'units': {u['state'].get('defId'): aggregate_unit(u) for u in side.get('units', {}).values() if u.get('state')}
    }

def generate_custom_comparison(p1, p2, out_path, name1, name2):
    # Сравниваем ВРАГА из первого боя и ВРАГА из второго боя
    b1 = get_battle_summary(p1, 'enemy')
    b2 = get_battle_summary(p2, 'enemy')
    
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Сравнение: {name1} vs {name2}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1f; color: #e0e0e0; padding: 20px; }}
        .container {{ max-width: 1400px; margin: auto; }}
        .header {{ text-align: center; margin-bottom: 30px; background: #25252d; padding: 20px; border-radius: 8px; }}
        .comparison-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 40px; }}
        th, td {{ border: 1px solid #333; padding: 12px; vertical-align: top; }}
        th {{ background: #25252d; color: #fff; }}
        .row-header {{ background: #2d2d35; text-align: center; font-weight: bold; text-transform: uppercase; font-size: 0.85em; color: #aaa; }}
        .diff-summary {{ background: #4a1a1a; color: #ffabac; font-size: 0.9em; text-align: center; font-weight: bold; padding: 6px; }}
        .unit-name {{ font-weight: bold; color: #ffeb3b; font-size: 1.1em; }}
        .label {{ color: #888; font-size: 0.8em; text-transform: uppercase; }}
        .val-mods {{ color: #8bc34a; font-weight: bold; }}
        .val-sharps {{ color: #ffc107; font-weight: bold; }}
    </style></head><body><div class="container">
    <div class="header"><h1>Сравнение билдов: {name1} vs {name2}</h1></div>
    <table class="comparison-table">
    <tr><th>{name1} ({b1['time']})</th><th>{name2} ({b2['time']})</th></tr>
    """

    def render_row(u1, u2, title):
        diff = get_diff_summary(u1, u2)
        h = f'<tr class="unit-row"><td colspan="2" class="row-header">{title}</td></tr>'
        if diff != "Без изменений.": h += f'<tr><td colspan="2" class="diff-summary">{diff}</td></tr>'
        
        def cell(u):
            if not u: return "<td>-</td>"
            return f'<td><div class="unit-name">{u["defId"]} (Ур. {u["lvl"]} | {u["stars"]}★)</div><div style="margin-top:5px;"><span class="label">Экип:</span> <span class="val-sharps">{u["eq_lvls_str"]}</span><br><span class="label">Модули:</span> <span class="val-mods">{", ".join(u["mods"])}</span><br><span class="label">Заточки:</span> <span class="val-sharps">{", ".join([f"{k}: {v}" for k, v in sorted(u["sharps"].items())])}</span></div></td>'
        
        return h + f'<tr>{cell(u1)}{cell(u2)}</tr>'

    html += render_row(b1['gen'], b2['gen'], "ГЕНЕРАЛ")
    all_u = sorted(list(set(b1['units'].keys()) | set(b2['units'].keys())))
    for uid in all_u:
        html += render_row(b1['units'].get(uid), b2['units'].get(uid), f"ЮНИТ: {uid.upper()}")

    html += "</table></div></body></html>"
    with open(out_path, 'w', encoding='utf-8') as f: f.write(html)

if __name__ == "__main__":
    generate_custom_comparison(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
