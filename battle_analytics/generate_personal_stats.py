import json
import os
import glob
import sys
from datetime import datetime

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ANALYTICS_DIR = os.path.join(ROOT_DIR, 'battle_analytics')
ARENA_SNAPSHOTS = os.path.join(ROOT_DIR, 'arena', 'snapshots')
OUTPUT_FILE = os.path.join(ANALYTICS_DIR, 'personal_stats.html')

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def fmt_num(val_str):
    try:
        val = float(str(val_str).replace(',', '.'))
        if val > 1000000:
            return f"{int(val // 1000):,}k".replace(',', ' ')
        return f"{int(val):,}".replace(',', ' ')
    except:
        return val_str

def get_latest_arena_players():
    snaps = sorted(glob.glob(os.path.join(ARENA_SNAPSHOTS, "arena_*.json")))
    if not snaps: return []
    data = load_json(snaps[-1])
    players = []
    # Rank is based on the position in the list (1-based)
    for i, p in enumerate(data.get('players', []), 1):
        players.append({
            'rank': i,
            'nick': p.get('profileState', {}).get('nickname'),
            'clan': p.get('clanProfile', {}).get('clanName', '-'),
            'power': fmt_num(p.get('power')),
            'rating': fmt_num(p.get('rating'))
        })
    return players

def parse_fight_time_msk(ft_str):
    # 17/05/2026_23:53:08.2390 -> datetime (UTC) -> MSK
    try:
        dt = datetime.strptime(ft_str.split('.')[0], "%d/%m/%Y_%H:%M:%S")
        # Assuming source is UTC, convert to MSK
        return dt + timedelta(hours=3)
    except:
        return datetime.min

from datetime import timedelta

def analyze_battles():
    stats = {}
    for item in os.listdir(ANALYTICS_DIR):
        player_dir = os.path.join(ANALYTICS_DIR, item)
        if not os.path.isdir(player_dir) or item.startswith('__'): continue
        
        nick = item
        player_battles = []
        battle_files = glob.glob(os.path.join(player_dir, "battle_*.json"))
        
        for bf in battle_files:
            b = load_json(bf)
            delta = int(b.get('ourRatingDelta', 0))
            is_win = delta > 0
            
            stats_data = b.get('statistics', {})
            p_units = stats_data.get('player', {}).get('units', {})
            e_units = stats_data.get('enemy', {}).get('units', {})
            
            p_min = min([int(s) for s in p_units.keys()]) if p_units else 99
            e_min = min([int(s) for s in e_units.keys()]) if e_units else 99
            is_attack = p_min < e_min
            
            player_battles.append({
                'time_str': b.get('fightTime'),
                'time_dt_msk': parse_fight_time_msk(b.get('fightTime')),
                'delta': delta,
                'is_win': is_win,
                'is_attack': is_attack,
                'file_html': os.path.basename(bf).replace('.json', '.html')
            })
            
        if player_battles:
            player_battles.sort(key=lambda x: x['time_dt_msk'], reverse=True)
            wins = sum(1 for b in player_battles if b['is_win'])
            total = len(player_battles)
            stats[nick] = {
                'total': total,
                'wins': wins,
                'losses': total - wins,
                'winrate': round(wins/total * 100, 1),
                'last_battle_msk': player_battles[0]['time_dt_msk'],
                'history': player_battles
            }
    return stats

def generate_summary_pages(stats):
    for nick, data in stats.items():
        rows = ""
        for b in data['history']:
            res_class = "win" if b['is_win'] else "loss"
            res_text = "ПОБЕДА" if b['is_win'] else "ПОРАЖЕНИЕ"
            type_text = "АТАКА" if b['is_attack'] else "ЗАЩИТА"
            type_class = "attack" if b['is_attack'] else "defense"
            delta_color = "#3fb950" if b['delta'] > 0 else ("#f85149" if b['delta'] < 0 else "#8b949e")
            
            time_display = b['time_dt_msk'].strftime("%d.%m.%Y %H:%M:%S")
            
            rows += f"""
            <tr onclick="window.location='{b['file_html']}'" style="cursor:pointer">
                <td>{time_display}</td>
                <td><span class="type-tag {type_class}">{type_text}</span></td>
                <td><span class="res-tag {res_class}">{res_text}</span></td>
                <td style="text-align:right; font-family:'Roboto Mono'; color:{delta_color}">{"+" if b['delta']>0 else ""}{b['delta']}</td>
            </tr>"""
            
        html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
        <title>История: {nick}</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet">
        <style>
            body {{ background: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ font-family: 'Orbitron'; color: #fff; text-align: center; }}
            .back-link {{ color: #58a6ff; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; }}
            th {{ background: #21262d; padding: 12px; text-align: left; font-size: 0.8rem; text-transform: uppercase; color: #8b949e; }}
            td {{ padding: 12px; border-bottom: 1px solid #30363d; }}
            tr:hover {{ background: #1c2128; }}
            .res-tag {{ padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }}
            .win {{ background: rgba(63, 185, 80, 0.2); color: #3fb950; }}
            .loss {{ background: rgba(248, 81, 73, 0.2); color: #f85149; }}
            .type-tag {{ font-size: 0.65rem; padding: 2px 6px; border-radius: 3px; border: 1px solid #30363d; }}
            .attack {{ color: #58a6ff; border-color: rgba(88, 166, 255, 0.3); }}
            .defense {{ color: #f2cc60; border-color: rgba(242, 204, 96, 0.3); }}
        </style></head><body><div class="container">
        <a href="../personal.html" class="back-link">← К списку игроков</a>
        <h1>ДОСЬЕ: {nick}</h1>
        <table><thead><tr><th>Дата и время (МСК)</th><th>Тип</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr></thead>
        <tbody>{rows}</tbody></table></div></body></html>"""
        
        with open(os.path.join(ANALYTICS_DIR, nick, 'summary.html'), 'w', encoding='utf-8') as f:
            f.write(html)

def generate_main_dashboard(arena_players, battle_stats):
    rows = ""
    for p in arena_players:
        nick = p['nick']
        s = battle_stats.get(nick)
        
        if s:
            wr = s['winrate']
            wr_color = "#3fb950" if wr >= 49.5 else ("#f2cc60" if wr >= 29.5 else "#f85149")
            last_dt = s['last_battle_msk'].strftime("%d.%m %H:%M")
            count_link = f"<a href='{nick}/summary.html' style='color:#58a6ff; text-decoration:none'>{s['total']}</a>"
            win_loss = f"<span style='color:#3fb950'>{s['wins']}</span> / <span style='color:#f85149'>{s['losses']}</span>"
            wr_display = f"<span style='color:{wr_color}; font-weight:700'>{wr}%</span>"
        else:
            count_link = "0"
            win_loss = "-"
            wr_display = "<span style='opacity:0.3'>-</span>"
            last_dt = "<span style='opacity:0.3'>никогда</span>"

        rows += f"""
        <tr>
            <td style="text-align:center; color:#8b949e">{p['rank']}</td>
            <td><a href="{nick}/summary.html" class="nick-link">{nick}</a></td>
            <td style="color:#8b949e; font-size:0.85rem">{p['clan']}</td>
            <td style="text-align:center; font-family:'Roboto Mono'; font-size:0.85rem; color:#58a6ff">{p['rating']}</td>
            <td style="text-align:right; font-family:'Roboto Mono'; font-size:0.85rem; color:#d29922">{p['power']}</td>
            <td style="text-align:center">{wr_display}</td>
            <td style="text-align:center; font-family:'Roboto Mono'; font-size:0.9rem">{win_loss}</td>
            <td style="text-align:center">{count_link}</td>
            <td style="text-align:center; font-size:0.8rem; color:#8b949e">{last_dt}</td>
        </tr>"""

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
    <title>Личная статистика боёв</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --error: #f85149; --border: #30363d; }}
        body {{ background: var(--bg); color: #c9d1d9; font-family: 'Inter', sans-serif; margin: 25px; }}
        header {{ text-align: center; margin-bottom: 30px; }}
        h1 {{ font-family: 'Orbitron'; font-size: 2.5rem; color: #fff; margin: 0; letter-spacing: 4px; }}
        .subtitle {{ color: var(--gold); letter-spacing: 2px; font-size: 0.9rem; text-transform: uppercase; }}
        .table-container {{ max-width: 1100px; margin: 0 auto; background: var(--card); border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #0b0e14; padding: 15px; color: #8b949e; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--border); }}
        td {{ padding: 10px 15px; border-bottom: 1px solid var(--border); }}
        tr:hover {{ background: #1c2128; }}
        .nick-link {{ color: #fff; font-weight: 700; text-decoration: none; }}
        .nick-link:hover {{ color: var(--accent); }}
        .nav-links {{ text-align: center; margin-bottom: 20px; }}
        .nav-links a {{ color: var(--accent); text-decoration: none; margin: 0 15px; font-size: 0.9rem; }}
    </style></head><body>
    <header><h1>MY ARENA PROWESS</h1><div class="subtitle">Личная эффективность против Топ-50</div></header>
    <div class="nav-links"><a href="dashboard.html">← Общий дашборд Арены</a></div>
    <div class="table-container"><table><thead><tr>
        <th style="width:40px">Место</th><th>Противник</th><th>Клан</th><th>Рейтинг</th><th>Мощь</th><th>Winrate</th><th>Счет (W/L)</th><th>Боёв</th><th>Последний (МСК)</th>
    </tr></thead><tbody>{rows}</tbody></table></div>
    </body></html>"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    print("[*] Агрегация личной статистики боёв...")
    players = get_latest_arena_players()
    stats = analyze_battles()
    generate_summary_pages(stats)
    generate_main_dashboard(players, stats)
    print(f"[*] Готово! Отчет: {OUTPUT_FILE}")
