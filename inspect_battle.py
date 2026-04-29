import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\Ответ на init от сервера.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

history = data['data']['userState']['arena']['battlesHistory']

# Полная структура первого боя
b = history[0]
print("=" * 60)
print(f"БОЙ #1 — '{b['nick']}' — полная структура")
print("=" * 60)

def print_deep(d, indent=0):
    prefix = "  " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                count = len(v)
                print(f"{prefix}{k}: ({type(v).__name__}, {count} эл.)")
                print_deep(v, indent + 1)
            else:
                print(f"{prefix}{k}: {v}")
    elif isinstance(d, list):
        for i, item in enumerate(d):
            print(f"{prefix}[{i}]:")
            print_deep(item, indent + 1)

print_deep(b)

print()
print("=" * 60)
print(f"БОЙ #2 — '{history[1]['nick']}' — только statistics")
print("=" * 60)
print_deep(history[1].get('statistics', {}))
