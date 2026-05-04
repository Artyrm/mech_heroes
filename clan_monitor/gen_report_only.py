"""
Запуск только генерации отчетов из существующих снэпшотов,
без обращения к API и без проверки активной сессии.
Использует clan_data_full.json для структуры иерархии.
"""
import sys, json, os
sys.path.insert(0, '.')

# Патчим is_user_active чтобы не блокировал
import clan_accountant as ca

# Загружаем последние живые данные
with open('clan_data_full.json', encoding='utf-8') as f:
    raw = json.load(f)

# clan_data_full может хранить разные структуры - ищем нужную
hier = raw.get('hier') or raw.get('hierarchy')
users = raw.get('users') or raw.get('Users') or []
rating = raw.get('clanRating') or raw.get('rating') or 0

print(f"Ключи в clan_data_full.json: {list(raw.keys())}")
if hier:
    print(f"Ключи в hier: {list(hier.keys())[:10]}")
print(f"Рейтинг: {rating}, Пользователей: {len(users)}")
