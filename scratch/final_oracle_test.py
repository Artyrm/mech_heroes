
import requests
init_resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/init?userid=227408", json={"data":{"userID":227408,"authKey":"2B8ADCBE7A00EE8AF838139813C3ABBB"},"version":"1.24.1","requestId":1,"locale":"ru","platform":"YandexGamesDesktop"}).json()
sid = init_resp['data']['sessionID']
cmd = {"data":{"userId":227408,"sessionID":sid,"commands":[{"commandNumber":260003,"hash":999,"id":"UnequipGeneralItemCommand","paramsStr":"{\"ID\":\"eva\",\"Item\":\"Tracker\"}","time":"20/05/2026_18:39:49.7530"}],"clanVersion":352498},"locale":"ru","platform":"YandexGamesDesktop","requestId":2,"version":"1.24.1"}
resp = requests.post("https://tanks.ya.patternmasters.ru/1.24.1/commands?userid=227408", json=cmd)
print(resp.text)
