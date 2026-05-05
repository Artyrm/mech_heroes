import json
import os
import sys

def format_num(val_str):
    try:
        val = float(val_str.replace(',', '.'))
        if val == 0: return "0"
        # Display as thousands with 'k' suffix and space separator
        thousands = int(val // 1000)
        return "{:,}".format(thousands).replace(',', ' ') + "k"
    except:
        return val_str

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

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Отчет о бое: {nick}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e24; color: #fff; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            .header {{ background-color: #2b2b36; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .header h1 {{ margin: 0; color: #e5e5e5; }}
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
            
            .equips {{ font-size: 13px; color: #aaa; }}
            .equips ul {{ padding-left: 20px; margin: 5px 0 0 0; }}
            .sharpening {{ color: #888; font-style: italic; }}
            
            .general-box {{ background-color: #4a3b2c; border-left-color: #ff9800; }}
            .enemy-box {{ background-color: #3b2c2c; border-left-color: #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Отчет о бое против {nick}</h1>
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
                <span>Ур. {gen.get('level', '?')}</span>
            </div>
            <div class="equips">
                <strong>Экипировка:</strong>
                <ul>
        """
        for eid, eq in gen.get('equipables', {}).items():
            sharp = eq.get('sharpening', {})
            sharp_str = ", ".join([f"{k}: {v.replace('_sharpening', '')}" for k, v in sharp.items()])
            res += f"<li>{eq.get('id')} (Lvl: {eq.get('level')}) <span class='sharpening'>[{sharp_str}]</span></li>"
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
                    <span>Lvl {state.get('level', '?')} | {state.get('stars', '?')}★</span>
                </div>
                <div class="unit-stats">
                    <div class="stat-box">⚔️ Нанёс: {dmg}</div>
                    <div class="stat-box">💔 Получил: {hl}</div>
                    <div class="stat-box">💚 Хил: {hh}</div>
                    <div class="stat-box">💀 Убил: {kills}</div>
                </div>
                <div class="equips">
                    <strong>Снаряжение:</strong>
                    <ul>
            """
            for eid, eq in state.get('equipables', {}).items():
                sharp = eq.get('sharpening', {})
                sharp_str = ", ".join([f"{k}: {v.replace('_sharpening', '')}" for k, v in sharp.items()])
                res += f"<li>{eq.get('id')} (Lvl {eq.get('level')}) <span class='sharpening'>[{sharp_str}]</span></li>"
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
    import sys
    if len(sys.argv) > 1:
        generate_html(sys.argv[1], sys.argv[1].replace('.json', '.html'))
    else:
        # По умолчанию генерируем для последнего боя со Strel
        generate_html('battle_analytics/Strel/battle_2026-05-01_22-29.json', 'battle_analytics/Strel/battle_report_Strel.html')
