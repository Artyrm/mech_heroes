import json
import os

def list_nicks():
    path = 'current_init_dump.json'
    if not os.path.exists(path):
        print(f"File {path} not found")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return
            
    history = data.get("data", {}).get("userState", {}).get("arena", {}).get("battlesHistory", [])
    nicks = {b.get('nick') for b in history if b.get('nick')}
    
    print("Unique nicknames in history:")
    for n in sorted(list(nicks)):
        print(f"  - {n}")

if __name__ == "__main__":
    list_nicks()
