
import requests
sid = "227408_F6E6A170D4EB52B09EBA656F03755405"
payload = {"data":{"userId":227408,"sessionID":sid,"commands":[{"commandNumber":260039,"hash":0,"id":"UnequipGeneralItemCommand","paramsStr":"{\"ID\":\"eva\",\"Item\":\"Tracker\"}","time":"20/05/2026_18:39:49.7530"}],"clanVersion":352488},"locale":"ru","platform":"YandexGamesDesktop","requestId":942114983,"version":"1.24.1"}
resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/commands?userid=227408", json=payload)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text}")
