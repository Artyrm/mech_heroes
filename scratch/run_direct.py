
import re, requests
try:
    txt = open(r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\js_functions\sample_commands\eva -- надеть око.txt').read()
    match = re.search(r'sessionID\":\"([^\"]+)', txt)
    if not match:
        print("REGEX FAILED. File content snippet:")
        print(txt[:300])
        exit()
    sid = match.group(1)
    print(f"Found SID: {sid}")
    
    payload = {"data":{"userId":227408,"sessionID":sid,"commands":[{"commandNumber":260003,"hash":0,"id":"UnequipGeneralItemCommand","paramsStr":"{\"ID\":\"eva\",\"Item\":\"Tracker\"}","time":"20/05/2026_18:39:49.7530"}],"clanVersion":352488},"locale":"ru","platform":"YandexGamesDesktop","requestId":942114983,"version":"1.24.1"}
    resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/commands?userid=227408", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
