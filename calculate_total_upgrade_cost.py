import json

def calculate_cumulative_costs():
    with open('defs.json', 'r', encoding='utf-8') as f:
        f.readline()
        data = json.load(f)
        
    coeffs = data['generals']['upgrade']['levelCostCoefficients']
    
    # Множители, определенные по данным пользователя (4 уровень, шаг 0)
    # Опыт: 126 / 36.008 ≈ 3.5
    # Биты: 252 / 36.008 ≈ 7.0
    EXP_MULT = 3.5
    MONEY_MULT = 7.0
    
    total_exp = 0
    total_money = 0
    
    # 476 шагов (коэффициентов) = 119 уровней (полных)
    # Каждый уровень - это 4 шага (0, 1, 2, 3)
    
    print(f"{'Уровень':<10} | {'Опыт (накоп)':<15} | {'Биты (накоп)':<15}")
    print("-" * 45)
    
    for i, c_str in enumerate(coeffs):
        c = float(c_str.replace(',', '.'))
        total_exp += round(c * EXP_MULT)
        total_money += round(c * MONEY_MULT)
        
        # Печатаем итог для каждого уровня (после завершения 4-го шага, т.е. когда i+1 делится на 4)
        if (i + 1) % 4 == 0:
            level = (i + 1) // 4
            print(f"{level:<10} | {total_exp:<15} | {total_money:<15}")
            
    print("-" * 45)
    print(f"Итого для 119 уровня: {total_exp} опыта, {total_money} битов")

if __name__ == "__main__":
    calculate_cumulative_costs()
