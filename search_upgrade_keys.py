import json
with open('defs.json', 'r', encoding='utf-8') as f:
    f.readline()
    data = json.load(f)
    
# Проверяем, есть ли что-то похожее на уровни или прокачку генералов
potential_keys = [k for k in data.keys() if 'level' in k.lower() or 'upgrade' in k.lower() or 'exp' in k.lower()]
print(potential_keys)
