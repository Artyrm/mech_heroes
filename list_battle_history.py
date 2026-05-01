import json

def list_history():
    with open('full_init_dump.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    history = data.get("data", {}).get("userState", {}).get("arena", {}).get("battlesHistory", [])
    
    print(f"{'#':<3} | {'Время':<25} | {'Оппонент':<15} | {'Дельта'}")
    print("-" * 55)
    for i, b in enumerate(history):
        print(f"{i+1:<3} | {b.get('fightTime'):<25} | {b.get('nick'):<15} | {b.get('ourRatingDelta')}")

if __name__ == "__main__":
    list_history()
