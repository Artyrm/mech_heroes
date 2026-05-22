
offset = 0x9C51CFC
with open(r'G:\Video\!Медведи\Mech Heroes\Приложение\Reverse\desktop.wasm', 'rb') as f:
    f.seek(offset)
    data = f.read(64)
    print(data.hex(' '))
