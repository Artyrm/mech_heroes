import json

def analyze_relationships():
    with open('clan_data_full.json', 'r', encoding='utf-8') as f:
        clan_data = json.load(f)
    
    hier = clan_data.get('clanState', {}).get('hierarchy', {})
    slots = hier.get('slots', [])
    leader = hier.get('leader', {})
    
    # Собираем всех в карту: SlotID -> {UID, Nick, Role, ParentID}
    nodes = {}
    
    def add_node(slot):
        sid = slot.get('slotId')
        uid = str(slot.get('member', {}).get('userId'))
        nick = slot.get('member', {}).get('nickname', 'Unknown')
        parent = slot.get('parentId')
        nodes[sid] = {"uid": uid, "nick": nick, "role": slot.get('role'), "parent": parent}

    if leader: add_node(leader)
    for s in slots: add_node(s)
    
    # Ищем Александра и Димарика
    alex_uid = "361914"
    dim_uid = "371651"
    
    alex_nodes = [sid for sid, n in nodes.items() if n['uid'] == alex_uid]
    dim_nodes = [sid for sid, n in nodes.items() if n['uid'] == dim_uid]
    
    print(f"Александр (ID: {alex_uid}) найден в слотах: {alex_nodes}")
    print(f"Димарик (ID: {dim_uid}) найден в слотах: {dim_nodes}")
    
    for d_sid in dim_nodes:
        parent_sid = nodes[d_sid]['parent']
        if parent_sid:
            p = nodes.get(parent_sid)
            if p:
                print(f"Димарик (слот {d_sid}) подчиняется: {p['nick']} (ID: {p['uid']}, Роль: {p['role']})")
            else:
                print(f"Димарик (слот {d_sid}) подчиняется слоту {parent_sid}, но он не найден в данных.")
        else:
            print(f"Димарик (слот {d_sid}) не имеет родительского слота (возможно, он Лидер или баг).")

    # Проверяем, кто подчиняется Александру
    for a_sid in alex_nodes:
        print(f"\nПодчиненные Александра (слот {a_sid}):")
        found_any = False
        for sid, n in nodes.items():
            if n['parent'] == a_sid:
                print(f"  - {n['nick']} (ID: {n['uid']}, Роль: {n['role']})")
                found_any = True
        if not found_any:
            print("  (Прямых подчиненных не найдено)")

if __name__ == "__main__":
    analyze_relationships()
