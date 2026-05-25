import json
import os

def extract_cooldowns(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        f.readline()
        data = json.load(f)
    
    generals_data = data.get("generals", {})
    gen_list = generals_data.get("generals", {})
    abilities = generals_data.get("abilities", {})
    
    results = []
    
    for gen_id, gen_data in gen_list.items():
        ab_name = gen_data.get("ability")
        if ab_name and ab_name in abilities:
            ab_data = abilities[ab_name]
            cooldown_str = ab_data.get("cooldown", "0s")
            # Превращаем '24s' в int 24
            cooldown_val = int(cooldown_str.replace('s', ''))
            
            energy_str = ab_data.get("energyCost", "0")
            # Превращаем '120,000' в int 120
            energy_val = int(energy_str.replace(',', '').replace('000', ''))
            
            results.append({
                "gen": gen_id, 
                "ab": ab_name, 
                "cd": cooldown_val, 
                "en": energy_val
            })
    
    # Сортировка по кулдауну
    results.sort(key=lambda x: x['cd'])
    
    print(f"| Генерал | Абилка | Кулдаун | Стоимость (к) |")
    print(f"|---|---|---|---|")
    for r in results:
        print(f"| {r['gen']} | {r['ab']} | {r['cd']}s | {r['en']} |")

if __name__ == "__main__":
    target_file = 'defs.json' 
    if os.path.exists(target_file):
        extract_cooldowns(target_file)
    else:
        print(f"Файл {target_file} не найден.")
