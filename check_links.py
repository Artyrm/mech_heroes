with open('battle_analytics/ksotar/summary.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'window\.location="(.*?)"', text)
print("Sample links:", matches[:5])
for l in matches[:3]:
    full = os.path.normpath(os.path.join('battle_analytics/ksotar', l))
    print(f"Link: {l} -> Full: {full} -> Exists: {os.path.exists(full)}")
