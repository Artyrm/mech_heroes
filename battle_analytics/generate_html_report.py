import json
import os
import sys
from collections import defaultdict

def format_num(val_str):
    try:
        val = float(val_str.replace(',', '.'))
        if val == 0: return "0"
        thousands = int(val // 1000)
        if thousands > 0:
            return "{:,}".format(thousands).replace(',', ' ') + "k"
        return str(int(val))
    except:
        return val_str

def format_level(raw_lvl):
    try:
        raw = int(raw_lvl)
        lvl = (raw // 4) + 1
        step = (raw % 4) + 1
        if step == 1:
            return str(lvl)
        return f"{lvl}.{step}"
    except:
        return raw_lvl

def clean_stat(s):
    if s.startswith('e_'):
        s = s[2:]
    s = s.replace('_sharpening', '').replace('sharpening_', '').replace('sharpening', '')
    return s

def get_mod_type(id_str):
    parts = id_str.split('_')
    stop_words = ['weapon', 'armor', 'engine', 'tracker', 'foot', 'ammunition', 'legendary']
    type_parts = []
    for p in parts:
        if p in stop_words: break
        type_parts.append(p)
    return '_'.join(type_parts)

def aggregate_unit_stats(u_data):
    state = u_data.get('state', {})
    if 'equipables' not in state and 'equipables' in u_data:
        equipables = u_data.get('equipables', {})
    else:
        equipables = state.get('equipables', {})
        
    sharps = defaultdict(int)
    mod_types = set()
    for eq in equipables.values():
        mod_types.add(get_mod_type(eq.get('id', '')))
        for t in eq.get('sharpening', {}).values():
            sharps[clean_stat(t)] += 1
    return {
        'mod_types': sorted(list(mod_types)),
        'sharpening_summary': dict(sharps)
    }

def generate_html(json_file, output_html):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fight_time = data.get('fightTime', 'Неизвестно')
    nick = data.get('nick', 'Оппонент')
    rating = data.get('opponentRating', '0')
    delta = data.get('ourRatingDelta', '0')
    
    delta_val = 0
    try: delta_val = int(delta)
    except: pass
    
    result_class = "win" if delta_val > 0 else "lose"
    result_text = "ПОБЕДА" if delta_val > 0 else "ПОРАЖЕНИЕ"

    stats_data = data.get('statistics', {})
    p_units = stats_data.get('player', {}).get('units', {})
    e_units = stats_data.get('enemy', {}).get('units', {})
    
    p_min = min([int(s) for s in p_units.keys()]) if p_units else 99
    e_min = min([int(s) for s in e_units.keys()]) if e_units else 99
    
    is_attack = p_min < e_min
    battle_type = "НАПАДЕНИЕ" if is_attack else "ЗАЩИТА"
    type_color = "#2196f3" if is_attack else "#ff9800"

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Бой с игроком: {nick}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e24; color: #fff; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            .header {{ background-color: #2b2b36; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .header h1 {{ margin: 0; color: #e5e5e5; }}
            .battle-type {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-bottom: 10px; background-color: {type_color}; }}
            .status {{ font-size: 24px; font-weight: bold; margin-top: 10px; }}
            .win {{ color: #4caf50; }}
            .lose {{ color: #f44336; }}
            .info {{ display: flex; justify-content: center; gap: 20px; margin-top: 10px; color: #bbb; }}
            .team-container {{ display: flex; gap: 20px; }}
            .team {{ flex: 1; background-color: #2b2b36; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .team h2 {{ border-bottom: 2px solid #444; padding-bottom: 10px; margin-top: 0; text-align: center; }}
            .unit {{ background-color: #383845; padding: 15px; margin-bottom: 15px; border-radius: 6px; border-left: 4px solid #555; }}
            .unit-header {{ display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #ffeb3b; }}
            .unit-stats {{ display: flex; gap: 10px; font-size: 13px; margin-bottom: 10px; color: #ccc; flex-wrap: wrap; }}
            .stat-box {{ background-color: #222; padding: 5px 8px; border-radius: 4px; white-space: nowrap; }}
            
            .agg-box {{ margin-top: 10px; background-color: #1a1a20; padding: 10px; border-radius: 4px; font-size: 12px; border: 1px solid #444; line-height: 1.6; }}
            .agg-label {{ color: #9e9e9e; font-weight: normal; margin-right: 5px; }}
            .mod-types {{ color: #8bc34a; font-weight: bold; }}
            .sharpening-summary {{ color: #ffc107; font-weight: bold; }}
            
            .equips {{ font-size: 11px; color: #888; margin-top: 10px; border-top: 1px solid #444; padding-top: 5px; }}
            .equips ul {{ padding-left: 15px; margin: 5px 0 0 0; list-style-type: square; }}
            .sharpening {{ color: #666; font-style: italic; }}
            .general-box {{ background-color: #4a3b2c; border-left-color: #ff9800; }}
            .enemy-box {{ background-color: #3b2c2c; border-left-color: #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="battle-type">{battle_type}</div>
                <h1>Бой с игроком: {nick}</h1>
                <div class="info">
                    <span>Время: {fight_time}</span>
                    <span>Рейтинг врага: {rating}</span>
                </div>
                <div class="status {result_class}">{result_text} ({delta} очков)</div>
            </div>
            <div class="team-container">
    """

    def render_team(title, data_dict, is_enemy=False):
        res = f"<div class='team'><h2>{title}</h2>"
        gen = data_dict.get('general', {})
        res += f"""
        <div class="unit general-box">
            <div class="unit-header">
                <span>Генерал: {gen.get('defId', 'Unknown')}</span>
                <span>Ур. {format_level(gen.get('level', '?'))}</span>
            </div>
        """
        
        agg = aggregate_unit_stats(gen)
        if agg['mod_types']:
            res += f"""
            <div class="agg-box">
                <div class="mod-types"><span class="agg-label">Модули:</span> {', '.join(agg['mod_types'])}</div>
                <div class="sharpening-summary"><span class="agg-label">Заточки:</span> {', '.join([f'{k}: {v}' for k, v in sorted(agg['sharpening_summary'].items())])}</div>
            </div>
            """

        res += f"""
            <div class="equips">
                <strong>Детали экипировки:</strong>
                <ul>
        """
        equip_source = gen.get('equipables', {})
        for eid, eq in equip_source.items():
            sharp = eq.get('sharpening', {})
            sharp_str = ", ".join([f"{k}: {clean_stat(v)}" for k, v in sharp.items()])
            res += f"<li>{eq.get('id')} (Ур. {eq.get('level', '?')}) <span class='sharpening'>[{sharp_str}]</span></li>"
        res += "</ul></div></div>"

        units = data_dict.get('units', {})
        for slot, u in sorted(units.items(), key=lambda x: int(x[0])):
            state = u.get('state', {})
            stats = u.get('statistics', {})
            box_class = "enemy-box" if is_enemy else ""
            
            dmg = format_num(stats.get('damageDone', '0'))
            hl = format_num(stats.get('healthLost', '0'))
            hh = format_num(stats.get('healthHealed', '0'))
            kills = stats.get('killsCount', '0')
            
            res += f"""
            <div class="unit {box_class}">
                <div class="unit-header">
                    <span>Слот {slot}: {state.get('defId', 'Unknown')}</span>
                    <span>Ур. {format_level(state.get('level', '?'))} | {state.get('stars', '?')}★</span>
                </div>
                <div class="unit-stats">
                    <div class="stat-box">⚔️ {dmg}</div>
                    <div class="stat-box">💔 {hl}</div>
                    <div class="stat-box">💚 {hh}</div>
                    <div class="stat-box">💀 {kills}</div>
                </div>
            """

            agg = aggregate_unit_stats(u)
            if agg['mod_types']:
                res += f"""
                <div class="agg-box">
                    <div class="mod-types"><span class="agg-label">Модули:</span> {', '.join(agg['mod_types'])}</div>
                    <div class="sharpening-summary"><span class="agg-label">Заточки:</span> {', '.join([f'{k}: {v}' for k, v in sorted(agg['sharpening_summary'].items())])}</div>
                </div>
                """

            res += f"""
                <div class="equips">
                    <strong>Снаряжение:</strong>
                    <ul>
            """
            for eid, eq in state.get('equipables', {}).items():
                sharp = eq.get('sharpening', {})
                sharp_str = ", ".join([f"{k}: {clean_stat(v)}" for k, v in sharp.items()])
                res += f"<li>{eq.get('id')} (Ур. {eq.get('level', '?')}) <span class='sharpening'>[{sharp_str}]</span></li>"
            res += "</ul></div></div>"
            
        res += "</div>"
        return res

    stats = data.get('statistics', {})
    player = stats.get('player', {})
    enemy = stats.get('enemy', {})

    html += render_team("Наш Отряд", player, is_enemy=False)
    html += render_team(f"Отряд Врага ({nick})", enemy, is_enemy=True)

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_html(sys.argv[1], sys.argv[1].replace('.json', '.html'))
