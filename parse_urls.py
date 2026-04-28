import json

def get_urls():
    with open('заход на Арену, просмотр статистики.har', 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    urls = set()
    for e in d['log']['entries']:
        url = e['request']['url'].split('?')[0]
        if '.bundle' not in url and 'yandex.ru' not in url and 'games.s3' not in url:
            urls.add(url)
            
    for u in urls:
        print(u)

if __name__ == "__main__":
    get_urls()
