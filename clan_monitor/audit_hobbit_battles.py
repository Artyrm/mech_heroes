import os, json, logging
from datetime import datetime, timedelta

# Конфигурация
USER_ID = "113012"  # Хоббит
BATTLES_DIR = r'G:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\battle_analytics\Хоббит'

print(f'Аудит файлов в папке {BATTLES_DIR}...')

count = 0
found_defense = 0
for f_name in os.listdir(BATTLES_DIR):
    if f_name.startswith("battle_") and f_name.endswith(".html"):
        count += 1
        file_path = os.path.join(BATTLES_DIR, f_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "ЗАЩИТА" in content:
                    found_defense += 1
                    if found_defense <= 5: # Выведем первые 5 найденных
                        print(f'Найдена ЗАЩИТА в: {f_name}')
        except Exception as e:
            print(f'Ошибка чтения {f_name}: {e}')

print(f'Всего файлов боев: {count}')
print(f'Боев с меткой "ЗАЩИТА": {found_defense}')
