path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Найдем начало и конец блока формирования tactical_html в generate_dossiers
# И заменим его целиком на корректный блок с проверкой if nick != 'ksotar':

target_snippet = '''        tactical_html = ''
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

correct_snippet = '''        tactical_html = ''
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

# Заменим через простую замену подстроки (если есть дубликаты tactical_html = '' почистим)
text = text.replace("tactical_html = ''\n        tactical_html = ''", "tactical_html = ''")

# Сделаем замену с помощью замены по кускам
start_idx = text.find('sorted_comps = sorted(compositions.items()')
if start_idx != -1:
    end_idx = text.find('rows = \'\'', start_idx)
    if end_idx != -1:
        new_tactical_section = '''sorted_comps = sorted(compositions.items(), key=lambda x: (x[1]['wins'] + x[1]['losses']), reverse=True)
        
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
        text = text[:start_idx] + new_tactical_section + text[end_idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print('Successfully replaced tactical section in generate_personal_stats.py!')
else:
    print('Could not find sorted_comps')
