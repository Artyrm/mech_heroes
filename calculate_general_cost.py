import json

# Данные из defs.json для upgrade.levelCostCoefficients
# (ограничимся для теста первыми 476 элементами, как в документации про уровень 1-120)
level_costs = [
    1.000, 2.500, 5.505, 8.515, 11.531, 14.553, 17.584, 20.624, 23.675, 26.737,
    # ... (здесь должна быть полная таблица)
]
# Я вижу в output, что массив очень длинный, порядка 476 элементов.
# Нам нужно прочитать его полностью.
# Я перепишу скрипт, чтобы он загрузил данные из файла defs.json

with open('defs.json', 'r', encoding='utf-8') as f:
    f.readline()
    data = json.load(f)
    coeffs = data['generals']['upgrade']['levelCostCoefficients']
    
# Преобразуем строковые значения с запятой в float
costs = [float(c.replace(',', '.')) for c in coeffs]

# Итоговая стоимость — это сумма всех коэффициентов
total_cost = sum(costs)

print(f"Количество коэффициентов: {len(costs)}")
print(f"Суммарная стоимость: {total_cost}")
