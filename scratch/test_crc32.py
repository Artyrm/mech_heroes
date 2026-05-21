
import zlib
import json

def to_int32(n):
    n = n & 0xFFFFFFFF
    if n > 0x7FFFFFFF:
        n -= 0x100000000
    return n

# Real data
data = [
    {
        "commandNumber": 260037,
        "id": "EquipGeneralItemCommand",
        "paramsStr": '{"OwnerID":"eva","ItemID":1288}',
        "hash": -1080719895
    }
]

authKey = "2B8ADCBE7A00EE8AF838139813C3ABBB"

print("Testing CRC32 theories...")

for d in data:
    variants = [
        f"{authKey}{d['paramsStr']}{d['commandNumber']}",
        f"{d['paramsStr']}{d['commandNumber']}{authKey}",
        f"{d['commandNumber']}{d['paramsStr']}{authKey}",
        f"{authKey}{d['commandNumber']}{d['paramsStr']}",
        d['paramsStr'],
        str(d['commandNumber'])
    ]
    
    for v in variants:
        c = zlib.crc32(v.encode())
        if to_int32(c) == d['hash']:
            print(f"MATCH! Variant: {v}")
            exit()
            
print("No match found for CRC32.")
