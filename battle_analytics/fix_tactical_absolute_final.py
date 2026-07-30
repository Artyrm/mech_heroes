path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Перепишем генерацию tactical_html безупречно:
# Если nick == 'ksotar', то tactical_html = '' и точка. Никаких циклов и +=.

old_target = '''        tactical_html = ''
        tactical_html = ''
        if nick != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'
        if not sorted_comps:
            tactical_html += '<div style="color:#8b949e;padding:10px">Нет данных о составах</div>'
        for units, res in sorted_comps:
            total = res['wins'] + res['losses']
            wr = (res['wins'] / total) * 100
            color = '#3fb950' if wr >= 60 else ('#f85149' if wr <= 40 else '#f2cc60')
            units_str = ", ".join(units)
            tactical_html += f\'\'\'
            <div class="comp-box">
                <div class="comp-units">{units_str}</div>
                <div class="comp-stats">Боёв: <b>{total}</b> | Винрейт: <span style="color:{color};font-weight:bold">{wr:.1f}%</span> ({res['wins']}В / {res['losses']}П)</div>
            </div>\'\'\'
        tactical_html += '</div>\''''

new_target = '''        tactical_html = ''
        if nick != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'
            if not sorted_comps:
                tactical_html += '<div style="color:#8b949e;padding:10px">Нет данных о составах</div>'
            for units, res in sorted_comps:
                total = res['wins'] + res['losses']
                wr = (res['wins'] / total) * 100
                color = '#3fb950' if wr >= 60 else ('#f85149' if wr <= 40 else '#f2cc60')
                units_str = ", ".join(units)
                tactical_html += f\'\'\'
                <div class="comp-box">
                    <div class="comp-units">{units_str}</div>
                    <div class="comp-stats">Боёв: <b>{total}</b> | Винрейт: <span style="color:{color};font-weight:bold">{wr:.1f}%</span> ({res['wins']}В / {res['losses']}П)</div>
                </div>\'\'\'
            tactical_html += '</div>\''''

# Найдем точное место по уникальной строке sorted_comps и заменим всё до rows = ""
start_idx = text.find('sorted_comps = sorted(compositions.items()')
if start_idx != -1:
    end_idx = text.find('rows = ""', start_idx)
    if end_idx != -1:
        replacement = '''sorted_comps = sorted(compositions.items(), key=lambda x: (x[1]['wins'] + x[1]['losses']), reverse=True)
        
        tactical_html = ''
        if nick != 'ksotar':
            tactical_html = '<div class="tactical-summary"><h2>Тактический анализ (по составам)</h2>'
            if not sorted_comps:
                tactical_html += '<div style="color:#8b949e;padding:10px">Нет данных о составах</div>'
            for units, res in sorted_comps:
                total = res['wins'] + res['losses']
                wr = (res['wins'] / total) * 100
                color = '#3fb950' if wr >= 60 else ('#f85149' if wr <= 40 else '#f2cc60')
                units_str = ", ".join(units)
                tactical_html += f\'\'\'
                <div class="comp-box">
                    <div class="comp-units">{units_str}</div>
                    <div class="comp-stats">Боёв: <b>{total}</b> | Винрейт: <span style="color:{color};font-weight:bold">{wr:.1f}%</span> ({res['wins']}В / {res['losses']}П)</div>
                </div>\'\'\'
            tactical_html += '</div>'
        
        '''
        text = text[:start_idx] + replacement + text[end_idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print('Absolute final tactical fix applied successfully!')
else:
    print('Could not find sorted_comps')
