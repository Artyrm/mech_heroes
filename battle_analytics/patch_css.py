import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_css = """.comp-stats { font-size: 0.75rem; color: #8b949e; margin-top: 3px; }
        </style></head>"""

new_css = """.comp-stats { font-size: 0.75rem; color: #8b949e; margin-top: 3px; }
            .type-attack { color: #f2cc60; font-weight: bold; }
            .type-defense { color: #58a6ff; font-weight: bold; }
            .res-win { color: #3fb950; font-weight: bold; }
            .res-loss { color: #f85149; font-weight: bold; }
        </style></head>"""

if 'type-attack { color:' not in text:
    text = text.replace(old_css, new_css)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('CSS added')
else:
    print('CSS already exists')
