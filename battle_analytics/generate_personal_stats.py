import json
import os
import glob
import sys
from datetime import datetime, timedelta

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ANALYTICS_DIR = os.path.join(ROOT_DIR, 'battle_analytics')
ARENA_SNAPSHOTS = os.path.join(ROOT_DIR, 'arena', 'snapshots')
OUTPUT_FILE = os.path.join(ANALYTICS_DIR, 'personal_stats.html')

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def fmt_num(val):
    try:
        v = float(str(val).replace(',', '.'))
        return f"{int(v // 1000):,}k".replace(',', ' ') if v >= 1000000 else f"{int(v):,}".replace(',', ' ')
    except: return str(val)

def parse_fight_time(ft_str):
    try: return datetime.strptime(ft_str.split('.')[0], "%d/%m/%Y_%H:%M:%S")
    except: return datetime.min

def get_state_at(arena_snap_path):
    ts_str = os.path.basename(arena_snap_path).replace('arena_', '').replace('.json', '')
    try: snap_dt = datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
    except: snap_dt = datetime.now()
    arena_data = load_json(arena_snap_path)
    players = []
    for i, p in enumerate(arena_data.get('players', []), 1):
        nick_raw = p.get('profileState', {}).get('nickname', '')
        clan_info = p.get('clanProfile', {})
        players.append({'rank': i, 'nick': nick_raw.strip(), 'clan': clan_info.get('clanName', '-'), 'clan_tag': clan_info.get('clanTag', ''), 'power': p.get('power'), 'rating': p.get('rating')})

    battle_stats, global_sum = {}, {"a_wins": 0, "a_losses": 0, "d_wins": 0, "d_losses": 0}
    player_keys = [d for d in os.listdir(ANALYTICS_DIR) if os.path.isdir(os.path.join(ANALYTICS_DIR, d)) and not d.startswith('__') and d != 'snapshots']
    if glob.glob(os.path.join(ANALYTICS_DIR, "battle_*.json")):
        if "" not in player_keys: player_keys.append("")

    for nick_key in player_keys:
        player_dir = os.path.join(ANALYTICS_DIR, nick_key) if nick_key else ANALYTICS_DIR
        wins, losses, a_total, d_total, last_battle = 0, 0, 0, 0, datetime.min
        for bf in glob.glob(os.path.join(player_dir, "battle_*.json")):
            b = load_json(bf)
            b_dt = parse_fight_time(b.get('fightTime'))
            
            # Для построения таблицы с дельтами нам нужны бои строго до даты снимка
            if b_dt <= snap_dt:
                delta = int(b.get('ourRatingDelta', 0))
                is_win = delta > 0
                sd = b.get('statistics', {})
                p_u, e_u = sd.get('player', {}).get('units', {}), sd.get('enemy', {}).get('units', {})
                p_min, e_min = (min([int(s) for s in p_u.keys()]) if p_u else 99), (min([int(s) for s in e_u.keys()]) if e_u else 99)
                is_attack = p_min < e_min
                if is_win: wins += 1
                else: losses += 1
                if is_attack:
                    a_total += 1
                    if is_win: global_sum["a_wins"] += 1
                    else: global_sum["a_losses"] += 1
                else:
                    d_total += 1
                    if is_win: global_sum["d_wins"] += 1
                    else: global_sum["d_losses"] += 1
                if b_dt > last_battle: last_battle = b_dt
        if wins + losses > 0:
            battle_stats[nick_key] = {'wins': wins, 'losses': losses, 'a_total': a_total, 'd_total': d_total, 'winrate': round(wins/(wins+losses)*100, 1), 'last_battle_utc': last_battle.isoformat() if last_battle != datetime.min else None}
    return {"timestamp_utc": ts_str, "players": players, "battle_stats": battle_stats, "summary": global_sum}

def generate_html_template():
    return """<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>My Arena Prowess</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;700&family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --gold: #f2cc60; --green: #3fb950; --error: #f85149; --border: #30363d; }
        body { background: var(--bg); color: #c9d1d9; font-family: 'Inter', sans-serif; margin: 10px; font-size: 0.8rem; line-height: 1.2; }
        header { text-align: center; margin-bottom: 10px; }
        h1 { font-family: 'Orbitron'; font-size: 1.4rem; color: #fff; margin: 0; letter-spacing: 2px; }
        .summary-box { display: flex; justify-content: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
        .stat-card { background: var(--card); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border); text-align: center; min-width: 100px; }
        .stat-val { display: block; font-size: 1rem; font-family: 'Roboto Mono'; font-weight: 700; color: #fff; }
        .stat-label { font-size: 0.5rem; text-transform: uppercase; color: #8b949e; margin-top: 2px; display: block; }
        .controls { background: var(--card); padding: 8px 15px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 10px; display: flex; gap: 15px; align-items: center; justify-content: center; flex-wrap: wrap; }
        select { background: #0b0e14; color: #fff; border: 1px solid var(--border); padding: 3px 6px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; }
        .checkbox-container { display: flex; align-items: center; gap: 4px; color: #8b949e; font-size: 0.7rem; cursor: pointer; }
        .table-container { width: 100%; max-width: 100%; margin: 0 auto; background: var(--card); border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; }
        table { width: auto; margin: 0 auto; border-collapse: collapse; table-layout: auto; }
        th { background: #0b0e14; padding: 6px 8px; color: #8b949e; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); white-space: nowrap; }
        .text-right { text-align: right !important; }
        .text-left { text-align: left !important; }
        .text-center { text-align: center !important; }
        td { padding: 4px 8px; border-bottom: 1px solid var(--border); vertical-align: middle; white-space: nowrap; font-family: 'Roboto Mono', monospace; }
        .col-nick { font-family: 'Inter', sans-serif !important; font-weight: 700; color: #58a6ff !important; text-align: left !important; min-width: 100px; }
        .col-clan { font-family: 'Inter', sans-serif !important; font-weight: 400; color: #8b949e !important; text-align: left !important; }
        .col-delta { text-align: left !important; padding-left: 2px !important; font-size: 0.65rem; font-weight: bold; width: 35px; }
        .col-last { text-align: right !important; color: #8b949e; font-size: 0.7rem; }
        .delta-pos { color: #3fb950; }
        .delta-neg { color: #f85149; }
        .nick-link { color: #58a6ff; text-decoration: none; }
        .nick-link:hover { text-decoration: underline; }
        .elo-ref { margin-top: 20px; font-size: 0.7rem; color: #8b949e; text-align: center; }
    </style></head><body>
    <header><h1>MY ARENA PROWESS</h1></header>
    <div class="nav-links" style="text-align:center;margin-bottom:10px"><a href="dashboard.html" style="color:#58a6ff;text-decoration:none;font-size:0.7rem">← К дашборду Арены</a></div>
    <div class="summary-box" id="summary-container"></div>
    <div class="controls">
        <div><label>T1: </label><select id="t1-select" onchange="updateTable()"></select></div>
        <div><label>T2: </label><select id="t2-select" onchange="updateTable()"></select></div>
        <label class="checkbox-container"><input type="checkbox" id="show-changes" onchange="updateTable()" checked> Изменения</label>
    </div>
    <div class="table-container"><table><thead><tr>
        <th class="text-center">#</th><th class="text-left">Противник</th><th class="text-left">Клан</th><th class="text-right">Рейтинг</th>
        <th class="text-right">Мощь</th><th class="text-center" colspan="2">Winrate</th>
        <th class="text-center" colspan="2">ELO (W/L)</th>
        <th class="text-right">Побед</th><th class="col-delta"></th><th class="text-right">Поражений</th><th class="col-delta"></th>
        <th class="text-right">Атак</th><th class="col-delta"></th><th class="text-right">Защит</th><th class="col-delta"></th>
        <th class="text-right">Боёв</th><th class="col-delta"></th><th class="text-right">Последний</th>
    </tr></thead><tbody id="table-body"></tbody></table></div>
    <div class="elo-ref">Формула рейтинга: Win = 10 + round(diff/20), Loss = -10 + round(diff/20). База K=20.</div>
    <script>
        const snapshots = SNAPSHOTS_DATA;
        const ourCurrentRating = OUR_CURRENT_RATING;
        const t1Select = document.getElementById('t1-select'), t2Select = document.getElementById('t2-select');
        const showChanges = document.getElementById('show-changes'), tableBody = document.getElementById('table-body'), summaryBox = document.getElementById('summary-container');
        
        function calcElo(ourR, oppR) {
            const diff = oppR - ourR;
            let w = Math.max(1, 10 + Math.trunc(diff / 20));
            let l = Math.min(-1, -10 + Math.trunc(diff / 20));
            return {w: '+' + w, l: l};
        }
        function fmtNum(val) {
            if (!val) return "0"; let v = parseFloat(val.toString().replace(',', '.'));
            return (v >= 1000000) ? (Math.floor(v/1000)).toLocaleString('ru-RU') + 'k' : Math.floor(v).toLocaleString('ru-RU');
        }
        function parseTS(ts) { 
            const p = ts.split(/[-T]/); 
            return new Date(Date.UTC(p[0], p[1]-1, p[2], p[3], p[4], p[5])); 
        }
        function formatDateMSK(ts) {
            const dt = parseTS(ts);
            const msk = new Date(dt.getTime() + 3 * 3600 * 1000);
            return msk.getUTCDate().toString().padStart(2, '0') + '.' + (msk.getUTCMonth()+1).toString().padStart(2, '0') + ' ' + msk.getUTCHours().toString().padStart(2, '0') + ':' + msk.getUTCMinutes().toString().padStart(2, '0');
        }
        const dates = Object.keys(snapshots).sort();
        dates.forEach(d => { const label = formatDateMSK(d); t1Select.add(new Option(label, d)); t2Select.add(new Option(label, d)); });
        t2Select.selectedIndex = dates.length - 1;
        
        const latestDate = parseTS(dates[dates.length-1]);
        const latestMSK = new Date(latestDate.getTime() + 3 * 3600 * 1000);
        const startOfTodayMSK = new Date(Date.UTC(latestMSK.getUTCFullYear(), latestMSK.getUTCMonth(), latestMSK.getUTCDate())).getTime();
        let t1Idx = 0;
        for (let i = 0; i < dates.length; i++) { 
            if (parseTS(dates[i]).getTime() + 3*3600*1000 >= startOfTodayMSK) { t1Idx = i; break; } 
        }
        t1Select.selectedIndex = (t1Idx === dates.length-1 && dates.length > 1) ? dates.length-2 : t1Idx;

        function renderDelta(val, isInverse=false, isPercent=false) {
            if (!showChanges.checked || t1Select.value === t2Select.value) return "";
            const n = parseFloat(val); if (isNaN(n) || n === 0) return "";
            const cls = (n > 0) ? (isInverse ? "delta-neg" : "delta-pos") : (isInverse ? "delta-pos" : "delta-neg");
            const sign = n > 0 ? "+" : "-";
            const formatted = isPercent ? Math.abs(n).toFixed(0) + '%' : Math.floor(Math.abs(n));
            return `<span class="${cls}">${sign}${formatted}</span>`;
        }

        function updateTable() {
            const d1 = t1Select.value, d2 = t2Select.value, s1 = snapshots[d1], s2 = snapshots[d2], isSame = (d1 === d2);
            const sum2 = s2.summary, sum1 = s1.summary;
            const ds = { a_w: sum2.a_wins - (isSame?0:sum1.a_wins), a_l: sum2.a_losses - (isSame?0:sum1.a_losses), d_w: sum2.d_wins - (isSame?0:sum1.d_wins), d_l: sum2.d_losses - (isSame?0:sum1.d_losses) };
            summaryBox.innerHTML = `<div class="stat-card" style="border-bottom:3px solid #f2cc60"><span class="stat-val" style="color:#f2cc60">${ds.a_w} / ${ds.a_l}</span><span class="stat-label">Атаки</span></div>
                <div class="stat-card" style="border-bottom:3px solid #58a6ff"><span class="stat-val" style="color:#58a6ff">${ds.d_w} / ${ds.d_l}</span><span class="stat-label">Защиты</span></div>
                <div class="stat-card"><span class="stat-val" style="color:#fff">${ds.a_w + ds.d_w}</span><span class="stat-label">Побед всего</span></div>`;
            tableBody.innerHTML = "";
            s2.players.forEach((p2, idx) => {
                const nick_key = p2.nick;
                const display_nick = p2.nick || '<без имени>';
                const st1 = s1.battle_stats[nick_key], st2 = s2.battle_stats[nick_key];
                let wr = '-', wr_d = '', w = '-', w_d = '', l = '-', l_d = '', a = '-', a_d = '', d = '-', d_d = '', cnt = '-', cnt_d = '', last = '-';
                if (st2) {
                    const wrColor = st2.winrate>=49.5?'#3fb950':(st2.winrate>=29.5?'#f2cc60':'#f85149');
                    wr = `<span style="font-weight:700;color:${wrColor}">${st2.winrate}%</span>`;
                    wr_d = st1 ? renderDelta(st2.winrate - st1.winrate, false, true) : "";
                    w = st2.wins; w_d = st1 ? renderDelta(st2.wins - st1.wins) : "";
                    l = st2.losses; l_d = st1 ? renderDelta(st2.losses - st1.losses, true) : "";
                    a = st2.a_total; a_d = st1 ? renderDelta(st2.a_total - st1.a_total) : "";
                    d = st2.d_total; d_d = st1 ? renderDelta(st2.d_total - st1.d_total) : "";
                    cnt = st2.wins + st2.losses; cnt_d = st1 ? renderDelta(st2.wins + st2.losses - (st1.wins + st1.losses)) : "";
                    if (st2.last_battle_utc) {
                        const dt = new Date(new Date(st2.last_battle_utc).getTime() + 3 * 3600 * 1000);
                        last = dt.getUTCDate().toString().padStart(2, '0') + '.' + (dt.getUTCMonth()+1).toString().padStart(2, '0') + ' ' + dt.getUTCHours().toString().padStart(2, '0') + ':' + dt.getUTCMinutes().toString().padStart(2, '0');
                    }
                }
                const elo = calcElo(ourCurrentRating, parseInt(p2.rating));
                const tr = document.createElement('tr');
                tr.innerHTML = `<td class="text-center">${idx+1}</td><td class="col-nick"><a href="${nick_key || '_EMPTY_'}/summary.html" class="nick-link">${display_nick}</a></td>
                    <td class="col-clan">${p2.clan_tag || p2.clan}</td><td class="text-right">${fmtNum(p2.rating)}</td><td class="text-right">${fmtNum(p2.power)}</td>
                    <td class="text-right" style="border-right:none">${wr}</td><td class="col-delta" style="border-left:none">${wr_d}</td>
                    <td class="text-right" style="border-right:none">${elo.w}</td><td class="col-delta" style="border-left:none">${elo.l}</td>
                    <td class="text-right" style="border-right:none">${w}</td><td class="col-delta" style="border-left:none">${w_d}</td>
                    <td class="text-right" style="border-right:none">${l}</td><td class="col-delta" style="border-left:none">${l_d}</td>
                    <td class="text-right" style="border-right:none">${a}</td><td class="col-delta" style="border-left:none">${a_d}</td>
                    <td class="text-right" style="border-right:none">${d}</td><td class="col-delta" style="border-left:none">${d_d}</td>
                    <td class="text-right" style="border-right:none">${cnt}</td><td class="col-delta" style="border-left:none">${cnt_d}</td>
                    <td class="col-last">${last}</td>`;
                tableBody.appendChild(tr);
            });
        }
        updateTable();
    </script></body></html>"""

def generate_dossiers():
    for item in os.listdir(ANALYTICS_DIR):
        p_dir = os.path.join(ANALYTICS_DIR, item)
        is_root = False
        if not os.path.isdir(p_dir):
            if item.startswith("battle_") and item.endswith(".json"):
                is_root = True
                p_dir = ANALYTICS_DIR
                item = "_EMPTY_"
            else: continue
        
        if item.startswith('__') or item == 'snapshots': continue
        if is_root and os.path.exists(os.path.join(ANALYTICS_DIR, "_EMPTY_", "summary.html")): continue

        p_battles = []
        pattern = os.path.join(p_dir, "battle_*.json") if not is_root else os.path.join(ANALYTICS_DIR, "battle_*.json")
        for bf in glob.glob(pattern):
            if is_root and os.path.dirname(bf) != ANALYTICS_DIR: continue
            b = load_json(bf); sd = b.get('statistics', {}); p_u, e_u = sd.get('player', {}).get('units', {}), sd.get('enemy', {}).get('units', {})
            p_min, e_min = (min([int(s) for s in p_u.keys()]) if p_u else 99), (min([int(s) for s in e_u.keys()]) if e_u else 99)
            p_battles.append({'dt_msk': parse_fight_time(b.get('fightTime')) + timedelta(hours=3), 'delta': int(b.get('ourRatingDelta', 0)), 'is_win': int(b.get('ourRatingDelta', 0)) > 0, 'is_attack': p_min < e_min, 'file_html': os.path.basename(bf).replace('.json', '.html')})
        
        if p_battles:
            p_battles.sort(key=lambda x: x['dt_msk'], reverse=True)
            rows = ""
            for b in p_battles:
                rows += f"<tr onclick=\"window.location='{b['file_html']}'\" style=\"cursor:pointer\"><td>{b['dt_msk'].strftime('%d.%m %H:%M')}</td><td>{'АТАКА' if b['is_attack'] else 'ЗАЩИТА'}</td><td>{'ПОБЕДА' if b['is_win'] else 'ПОРАЖЕНИЕ'}</td><td style=\"text-align:right;font-family:'Roboto Mono';color:{'#3fb950' if b['delta']>0 else ('#f85149' if b['delta']<0 else '#8b949e')}\">{'+' if b['delta']>0 else ''}{b['delta']}</td></tr>"
            
            target_dir = os.path.join(ANALYTICS_DIR, item)
            os.makedirs(target_dir, exist_ok=True)
            display_name = item if item != "_EMPTY_" else "<без имени>"
            html = f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>История: {display_name}</title><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;700&family=Roboto+Mono&display=swap" rel="stylesheet"><style>body{{background:#0d1117;color:#c9d1d9;font-family:'Inter',sans-serif;margin:20px;font-size:0.9rem}}.container{{max-width:800px;margin:0 auto}}h1{{font-family:'Orbitron';color:#fff;text-align:center;font-size:1.8rem}}.back-link{{color:#58a6ff;text-decoration:none;display:inline-block;margin-bottom:20px;font-size:0.85rem}}table{{width:100%;border-collapse:collapse;background:#161b22;border-radius:8px;overflow:hidden}}th{{background:#21262d;padding:12px;text-align:left;font-size:0.7rem;text-transform:uppercase;color:#888;letter-spacing:1px}}td{{padding:12px;border-bottom:1px solid #30363d}}tr:hover{{background:#1c2128}}</style></head><body><div class="container"><a href="../personal.html" class="back-link">← К списку игроков</a><h1>ДОСЬЕ: {display_name}</h1><table><thead><tr><th>Дата и время (МСК)</th><th>Тип</th><th>Результат</th><th style="text-align:right">Δ Рейтинг</th></tr></thead><tbody>{rows}</tbody></table></div></body></html>'''
            with open(os.path.join(target_dir, 'summary.html'), 'w', encoding='utf-8') as f: f.write(html)

if __name__ == "__main__":
    arena_snaps = sorted(glob.glob(os.path.join(ARENA_SNAPSHOTS, "arena_*.json")))
    if not arena_snaps: sys.exit(1)
    prowess_data = {s["timestamp_utc"]: s for s in [get_state_at(p) for p in arena_snaps]}
    # Get latest our rating for ELO prediction
    our_current_rating = 0
    if arena_snaps:
        with open(arena_snaps[-1], 'r', encoding='utf-8') as f:
            snap_data = json.load(f)
            for p in snap_data.get('players', []):
                if p.get('profileState', {}).get('nickname') == "ksotar":
                    our_current_rating = int(p.get('rating', 0))
                    break

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: 
        html = generate_html_template().replace('SNAPSHOTS_DATA', json.dumps(prowess_data, ensure_ascii=False))
        html = html.replace('OUR_CURRENT_RATING', str(our_current_rating))
        f.write(html)
    generate_dossiers()
