
def to_unsigned(n):
    return n & 0xFFFFFFFF

# Данные из 'eva -- надеть око.txt'
# commandNumbers: 260037, 260038, 260039, 260040, 260041, 260042, 260043
hashes_raw = [-1080719895, 738173835, 1406055994, -519333633, -380244254, -1523492169, 1557594399]
hashes = [to_unsigned(h) for h in hashes_raw]
cmds = [260037 + i for i in range(len(hashes))]

print("--- Анализ последовательности хешей ---")
for i in range(len(hashes)):
    print(f"Cmd: {cmds[i]}, Hash: {hashes[i]} (raw: {hashes_raw[i]})")

print("\n--- Проверка разностей (H_n - H_{n-1}) ---")
for i in range(1, len(hashes)):
    diff = to_unsigned(hashes[i] - hashes[i-1])
    print(f"Diff {i}->{i+1}: {diff} ({'Четное' if diff % 2 == 0 else 'Нечетное'})")

print("\n--- Проверка LCG (H_n = A*H_{n-1} + B mod 2^32) ---")
# Если A нечетное, то (H2-H1) и (H3-H2) должны иметь одинаковую четность.
# Diff 1->2: 1818893730 (Четное)
# Diff 2->3: 667882159 (Нечетное)
# ВЫВОД: Это НЕ простой LCG с постоянными A и B.

print("\n--- Проверка зависимости от commandNumber ---")
# Может быть Hash = f(commandNumber, secret)?
for i in range(len(hashes)):
    # Попробуем XOR или остаток
    print(f"Hash ^ Cmd: {hashes[i] ^ cmds[i]}")

print("\n--- Гипотеза: Хеш зависит от контента команды ---")
# Команды 260037 и 260038 - EquipGeneralItemCommand
# Команда 260039 - TrackUsageTimeCommand (ID другой!)
# Команды 260040-260043 - EquipGeneralItemCommand
# Если хеш 260039 выбивается из логики, значит он зависит от ID команды.

diff_id = to_unsigned(hashes[2] - hashes[1]) # Между Equip и Track
diff_same = to_unsigned(hashes[1] - hashes[0]) # Между Equip и Equip
print(f"Diff (Same ID): {diff_same}")
print(f"Diff (Diff ID): {diff_id}")

print("\n--- Итог ---")
print("Простой математической связи между последовательными хешами нет.")
print("Вероятно, используется алгоритм типа MD5(authKey + commandNumber + paramsStr + secret_salt)")
print("Или более сложный PRNG, состояние которого обновляется после каждой команды.")
