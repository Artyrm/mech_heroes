# -*- coding: utf-8 -*-
import json
import os
import glob
import sys
from datetime import datetime, timedelta

# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arena.registry_manager as rm

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ANALYTICS_DIR = os.path.join(ROOT_DIR, 'battle_analytics')
ARENA_SNAPSHOTS = os.path.join(ROOT_DIR, 'arena', 'snapshots')
OUTPUT_FILE = os.path.join(ANALYTICS_DIR, 'personal.html')
CACHE_FILE = os.path.join(ROOT_DIR, 'arena', 'stats_cache.json')

def load_json(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def parse_fight_time(ft_str):
    try: return datetime.strptime(ft_str.split('.')[0], "%d/%m/%Y_%H:%M:%S")
    except: return datetime.min

def get_snapshot_dt(fname):
    ts_str = os.path.basename(fname).replace('arena_', '').replace('.json', '')
    try: return datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
    except: return datetime.now()


def abbrev_units(units_list):
    if not units_list: return '-'
    res = []
    for u in units_list:
        clean_u = u.replace('_', '').replace('-', '')
        abbr = clean_u[:2].upper()
        res.append(abbr)
    return ', '.join(res)

def get_player_battles_timeline():
    timeline = {}
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    for nick in player_keys:
        player_dir = os.path.join(ANALYTICS_DIR, nick)
        battles = []
        for bf in glob.glob(os.path.join(player_dir, "battle_*.json")):
            b = load_json(bf)
            dt = parse_fight_time(b.get('fightTime'))
            delta = int(b.get('ourRatingDelta', 0))
            sd = b.get('statistics', {})
            p_u_data = sd.get('player', {}).get('units', {})
            e_u_data = sd.get('enemy', {}).get('units', {})
            
            player_units = []
            for slot in p_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
            e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
            
            p_name = sd.get('player', {}).get('name', nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            
            p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
            e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
            
            p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
            e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
            
            is_attack = p_min < e_min
            opponent = e_name if is_attack else p_name
            if opponent == nick:
                opponent = e_name if p_name == nick else p_name
                
            opponent_clan = e_clan if is_attack else p_clan
            if not opponent_clan or opponent_clan == '-':
                opponent_clan = e_clan if opponent == e_name else p_clan

            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()

            battles.append({
                'dt': dt, 
                'is_win': delta > 0, 
                'is_attack': is_attack, 
                'delta': delta, 
                'file_html': os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'opponent_clan': opponent_clan or '-',
                'p_nick': nick
            })
        battles.sort(key=lambda x: x['dt'])
        timeline[nick] = battles
    return timeline

def get_state_at_optimized(arena_snap_path, player_timelines):
    snap_dt = get_snapshot_dt(arena_snap_path)
    arena_data = load_json(arena_snap_path)
    
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    
    current_uids = {int(p.get('userID', p.get('userId'))) for p in arena_data.get('players', []) if p.get('userID') or p.get('userId')}
    all_known_uids = {int(uid) for uid in known_users.keys()}
    
    # Также соберем uid для всех ников из player_timelines или папок battle_analytics
    nick_to_uid = {n: u for u, n in known_users.items()}
    
    missing_uids = all_known_uids - current_uids
    
    for uid in missing_uids:
        profile_file = os.path.join(ROOT_DIR, 'arena', 'squads', str(uid), 'profile_history.json')
        pe = None
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as pf:
                    ph = json.load(pf)
                    if ph: pe = ph[-1]
            except: pass
        
        arena_data['players'].append({
            'userID': uid,
            'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else 0,
            'power': pe.get('power', 0) if pe else 0,
            'profileState': {
                'nickname': (pe.get('nickname') if pe else None) or known_users.get(str(uid), str(uid)),
            },
            'clanProfile': {
                'clanName': pe.get('clanProfile', {}).get('clanName', '-') if pe else '-',
                'clanTag': pe.get('clanProfile', {}).get('clanTag', '') if pe else ''
            }
        })

    # Добавим игроков из player_timelines, если их нет
    existing_nicks = {p.get('profileState', {}).get('nickname', '').strip() for p in arena_data.get('players', [])}
    for nick in player_timelines.keys():
        if nick not in existing_nicks and nick != 'ksotar':
            # Попробуем найти профиль по нику
            pe = None
            uid_str = nick_to_uid.get(nick)
            if uid_str:
                profile_file = os.path.join(ROOT_DIR, 'arena', 'squads', uid_str, 'profile_history.json')
                if os.path.exists(profile_file):
                    try:
                        with open(profile_file, 'r', encoding='utf-8') as pf:
                            ph = json.load(pf)
                            if ph: pe = ph[-1]
                    except: pass
            
            arena_data['players'].append({
                'rating': pe.get('arenaRating', pe.get('rating', 0)) if pe else 0,
                'power': pe.get('power', 0) if pe else 0,
                'profileState': { 'nickname': nick },
                'clanProfile': { 
                    'clanName': pe.get('clanProfile', {}).get('clanName', '-') if pe else '-', 
                    'clanTag': pe.get('clanProfile', {}).get('clanTag', '') if pe else '' 
                }
            })

    players = []
    for i, p in enumerate(arena_data.get('players', []), 1):
        players.append({
            'rank': i, 
            'nick': p.get('profileState', {}).get('nickname', '').strip(), 
            'clan': p.get('clanProfile', {}).get('clanName', '-'), 
            'clan_tag': p.get('clanProfile', {}).get('clanTag', ''), 
            'power': p.get('power', 0), 
            'rating': p.get('rating', 0)
        })

    players.sort(key=lambda x: int(x.get('rating', 0) or 0), reverse=True)
    for idx, p in enumerate(players, 1):
        p['rank'] = idx

    battle_stats, global_sum = {}, {'a_wins': 0, 'a_losses': 0, 'd_wins': 0, 'd_losses': 0}
    for nick, battles in player_timelines.items():
        wins, losses, a_total, d_total, last_battle = 0, 0, 0, 0, datetime.min
        for b in battles:
            if b['dt'] > snap_dt: break
            if b['is_win']: wins += 1
            else: losses += 1
            if b['is_attack']:
                a_total += 1
                if b['is_win']: global_sum['a_wins'] += 1
                else: global_sum['a_losses'] += 1
            else:
                d_total += 1
                if b['is_win']: global_sum['d_wins'] += 1
                else: global_sum['d_losses'] += 1
            last_battle = b['dt']
        if wins + losses > 0:
            battle_stats[nick] = {'wins': wins, 'losses': losses, 'a_total': a_total, 'd_total': d_total, 'winrate': round(wins/(wins+losses)*100, 1), 'last_battle_utc': last_battle.isoformat() if last_battle != datetime.min else None}
    return {'timestamp_utc': snap_dt.strftime('%Y-%m-%dT%H-%M-%S'), 'players': players, 'battle_stats': battle_stats, 'summary': global_sum}

def generate_dossiers(player_timelines):
    reg = rm.load_registry()
    known_users = reg.get('known_users', {})
    
    # Собираем все бои против ksotar со всех папок противников
    all_ksotar_battles = []
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    for p_nick in player_keys:
        p_dir = os.path.join(ANALYTICS_DIR, p_nick)
        for bf in glob.glob(os.path.join(p_dir, "battle_*.json")):
            b_data = load_json(bf)
            dt = parse_fight_time(b_data.get('fightTime'))
            delta = int(b_data.get('ourRatingDelta', 0))
            sd = b_data.get('statistics', {})
            
            p_u_data = sd.get('player', {}).get('units', {})
            e_u_data = sd.get('enemy', {}).get('units', {})
            
            p_min = min([int(s) for s in p_u_data.keys()]) if p_u_data else 99
            e_min = min([int(s) for s in e_u_data.keys()]) if e_u_data else 99
            
            p_name = sd.get('player', {}).get('name', p_nick)
            e_name = sd.get('enemy', {}).get('name', 'Противник')
            
            p_clan_data = sd.get('player', {}).get('clanProfile', sd.get('player', {}).get('clan', {}))
            e_clan_data = sd.get('enemy', {}).get('clanProfile', sd.get('enemy', {}).get('clan', {}))
            
            p_clan = p_clan_data.get('clanTag', p_clan_data.get('clanName', '-')) if isinstance(p_clan_data, dict) else '-'
            e_clan = e_clan_data.get('clanTag', e_clan_data.get('clanName', '-')) if isinstance(e_clan_data, dict) else '-'
            
            is_attack = p_min < e_min
            opponent = e_name if is_attack else p_name
            opponent_clan = e_clan if is_attack else p_clan
            
            # Инвертируем для ksotar: если противник выиграл (delta > 0), для ksotar это поражение
            ksotar_is_win = delta < 0
            ksotar_is_attack = not is_attack
            ksotar_delta = -delta
            
            player_units = []
            for slot in p_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: player_units.append(u_def)
            player_units.sort()
            
            enemy_units = []
            for slot in e_u_data.values():
                u_def = slot.get('state', {}).get('defId')
                if u_def: enemy_units.append(u_def)
            enemy_units.sort()
            
            all_ksotar_battles.append({
                'dt': dt,
                'is_win': ksotar_is_win,
                'is_attack': ksotar_is_attack,
                'delta': ksotar_delta,
                'file_html': f"../{p_nick}/" + os.path.basename(bf).replace('.json', '.html'),
                'units': tuple(player_units),
                'enemy_units': tuple(enemy_units),
                'opponent': opponent,
                'opponent_clan': opponent_clan or '-'
            })
    all_ksotar_battles.sort(key=lambda x: x['dt'])

    all_nicks = set(player_timelines.keys())
    for uid_str, nick in known_users.items():
        all_nicks.add(nick)
    all_nicks.add('ksotar')
        
    for nick in all_nicks:
        if nick.strip() == 'ksotar':
            battles = all_ksotar_battles
        else:
            battles = player_timelines.get(nick, [])
            
        compositions = {}
        for b in battles:
            u = b.get('units')
            if not u: continue
            if u not in compositions:
                compositions[u] = {'wins': 0, 'losses': 0}
            if b['is_win']: compositions[u]['wins'] += 1
            else: compositions[u]['losses'] += 1
            
        sorted_comps = sorted(compositions.items(), key=lambda x: (x[1]['wins'] + x[1]['losses']), reverse=True)
        
        tactical_html = ''
        if nick.strip() != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'
            if not sorted_comps:
                tactical_html += '<div style="color:#8b949e;padding:10px">Нет данных о составах</div>'
            for units, res in sorted_comps:
                total = res['wins'] + res['losses']
                wr = (res['wins'] / total) * 100
                color = '#3fb950' if wr >= 60 else ('#f85149' if wr <= 40 else '#f2cc60')
                units_str = ", ".join(units)
                tactical_html += f'''
                <div class="comp-box">
                    <div class="comp-units">{units_str}</div>
                    <div class="comp-stats">Боёв: <b>{total}</b> | Винрейт: <span style="color:{color};font-weight:bold">{wr:.1f}%</span> ({res['wins']}В / {res['losses']}П)</div>
                </div>'''
            tactical_html += '</div>'

        if nick.strip() == 'ksotar':
            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Противник</th><th>Клан</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th></tr>"
        else:
            table_headers = "<tr><th>Дата и время (МСК)</th><th>Тип</th><th>Свой отряд</th><th>Отряд противника</th><th>Результат</th><th style=\"text-align:right\">Δ Рейтинг</th></tr>"
        
        rows = ""
        if battles:
            for b in reversed(battles):
                dt_str = (b['dt'] + timedelta(hours=3)).strftime('%d.%m %H:%M')
                type_str = 'АТАКА' if b['is_attack'] else 'ЗАЩИТА'
                type_class = 'type-attack' if b['is_attack'] else 'type-defense'
                res_str = 'ПОБЕДА' if b['is_win'] else 'ПОРАЖЕНИЕ'
                res_class = 'res-win' if b['is_win'] else 'res-loss'
                delta_val = b['delta']
                delta_str = f"+{delta_val}" if delta_val > 0 else str(delta_val)
                delta_color = '#3fb950' if delta_val > 0 else ('#f85149' if delta_val < 0 else '#8b949e')
                my_units_abbr = abbrev_units(b.get('units', []))
                enemy_units_abbr = abbrev_units(b.get('enemy_units', []))
                
                if nick.strip() == 'ksotar':
                    opponent = b.get('opponent', '-')
                    opp_clan = b.get('opponent_clan', '-')
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\"window.location='{file_html}'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\"color:#58a6ff;font-family:'Inter',sans-serif;font-weight:600\">{opponent}</td><td style=\"color:#8b949e;font-family:'Inter',sans-serif;font-size:0.75rem\">{opp_clan}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\">{my_units_abbr}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>"
                else:
                    file_html = b.get('file_html', '#')
                    rows += f"<tr onclick=\"window.location='{file_html}'\" style=\"cursor:pointer\" title=\"Нажмите, чтобы открыть подробную карточку боя\"><td>{dt_str}</td><td><span class='{type_class}'>{type_str}</span></td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#58a6ff\" title=\"{ ', '.join(b.get('units', [])) }\">{my_units_abbr}</td><td style=\"font-family:'Roboto Mono';font-size:0.75rem;color:#8b949e\" title=\"{ ', '.join(b.get('enemy_units', [])) }\">{enemy_units_abbr}</td><td><span class='{res_class}'>{res_str}</span></td><td style=\"text-align:right;font-family:'Roboto Mono';color:{delta_color};font-weight:bold\">{delta_str}</td></tr>"
        else:
            col_span = 8 if nick.strip() == 'ksotar' else 6
            rows = f"<tr><td colspan=\"{col_span}\" style=\"text-align:center;color:#8b949e;padding:20px\">Бои не найдены</td></tr>"
            
        target_dir = os.path.join(ANALYTICS_DIR, nick.strip())
        os.makedirs(target_dir, exist_ok=True)
        
        html = f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>История: {nick}</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet">
        <style>
            body{{background:#0d1117;color:#c9d1d9;font-family:'Inter',sans-serif;margin:20px;font-size:0.9rem}}
            .container{{max-width:1000px;margin:0 auto}}
            h1{{font-family:'Orbitron';color:#fff;text-align:center;font-size:1.8rem;margin-bottom:10px}}
            h2{{font-family:'Orbitron';font-size:1.1rem;color:#8b949e;border-bottom:1px solid #30363d;padding-bottom:5px;margin-top:20px}}
            .back-link{{color:#58a6ff;text-decoration:none;display:inline-block;margin-bottom:20px;font-size:0.85rem}}
            table{{width:100%;border-collapse:collapse;background:#161b22;border-radius:8px;overflow:hidden;margin-top:20px}}
            th{{background:#21262d;padding:12px;text-align:left;font-size:0.7rem;text-transform:uppercase;color:#888;letter-spacing:1px}}
            td{{padding:12px;border-bottom:1px solid #30363d}}
            tr:hover{{background:#1c2128}}
            .comp-box {{ border-bottom: 1px solid #30363d; padding: 8px 0; }}
            .comp-box:last-child {{ border-bottom: none; }}
            .comp-units {{ color: #58a6ff; font-family: 'Roboto Mono'; font-size: 0.8rem; font-weight: bold; }}
            .comp-stats {{ font-size: 0.75rem; color: #8b949e; margin-top: 3px; }}
            .type-attack {{ color: #f2cc60; font-weight: bold; }}
            .type-defense {{ color: #58a6ff; font-weight: bold; }}
            .res-win {{ color: #3fb950; font-weight: bold; }}
            .res-loss {{ color: #f85149; font-weight: bold; }}
        </style></head>
        <body><div class="container"><a href="../personal.html" class="back-link">← К списку игроков</a>
        <h1>ДОСЬЕ: {nick}</h1>
        {tactical_html}
        <table><thead>{table_headers}</thead><tbody>{rows}</tbody></table>
        </div></body></html>'''
        
        with open(os.path.join(target_dir, 'summary.html'), 'w', encoding='utf-8') as f: f.write(html)
