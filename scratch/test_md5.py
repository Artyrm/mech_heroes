
import hashlib
import json

def to_int32(n):
    # Convert to signed 32-bit integer
    n = n & 0xFFFFFFFF
    if n > 0x7FFFFFFF:
        n -= 0x100000000
    return n

authKey = "2B8ADCBE7A00EE8AF838139813C3ABBB"

# Real data from 'eva -- надеть око.txt'
data = [
    {
        "commandNumber": 260037,
        "id": "EquipGeneralItemCommand",
        "paramsStr": '{"OwnerID":"eva","ItemID":1288}',
        "hash": -1080719895
    },
    {
        "commandNumber": 260038,
        "id": "EquipGeneralItemCommand",
        "paramsStr": '{"OwnerID":"eva","ItemID":1468}',
        "hash": 738173835
    },
    {
        "commandNumber": 260039,
        "id": "TrackUsageTimeCommand",
        "paramsStr": 'null',
        "hash": 1406055994
    }
]

print("Testing MD5 theories...")

for d in data:
    # Try different combinations
    variants = [
        f"{authKey}{d['paramsStr']}{d['commandNumber']}",
        f"{authKey}{d['commandNumber']}{d['paramsStr']}",
        f"{d['commandNumber']}{authKey}{d['paramsStr']}",
        f"{d['paramsStr']}{d['commandNumber']}{authKey}",
        f"{authKey}{d['id']}{d['paramsStr']}{d['commandNumber']}",
        f"{d['commandNumber']}{d['id']}{d['paramsStr']}{authKey}"
    ]
    
    found = False
    for v in variants:
        m = hashlib.md5(v.encode()).hexdigest()
        # Take first 8 chars (4 bytes) and convert to int32
        h_val = int(m[:8], 16)
        if to_int32(h_val) == d['hash']:
            print(f"MATCH! Variant: {v}")
            found = True
            break
        
        # Try last 8 chars
        h_val = int(m[-8:], 16)
        if to_int32(h_val) == d['hash']:
            print(f"MATCH (last 8)! Variant: {v}")
            found = True
            break

    if not found:
        print(f"No match for Cmd {d['commandNumber']}")
