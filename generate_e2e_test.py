import random

def mul(a, b):
    a_s = a - 65536 if (a & 0x8000) else a
    b_s = b - 65536 if (b & 0x8000) else b
    return ((a_s * b_s) >> 12) & 0xFFFF

def add(a, b):
    a_s = a - 65536 if (a & 0x8000) else a
    b_s = b - 65536 if (b & 0x8000) else b
    return (a_s + b_s) & 0xFFFF

def relu(a):
    return 0 if (a & 0x8000) else a

def mac_1d(inputs, weights):
    acc = 0
    for i, w in zip(inputs, weights):
        acc = add(acc, mul(i, w))
    return acc

# 1. Generate 100 inputs (0 or 4096 representing 0.0 or 1.0)
inputs = [random.choice([0, 4096]) for _ in range(100)]

# 2. Generate random weights
w1 = [[random.randint(-2048, 2048) for _ in range(100)] for _ in range(16)]
w2 = [[random.randint(-2048, 2048) for _ in range(16)] for _ in range(6)]
w3 = [[random.randint(-2048, 2048) for _ in range(6)] for _ in range(10)]

# 3. Cycle-Accurate Forward Pass
l1_out = [relu(mac_1d(inputs, w1[r])) for r in range(16)]
l2_out = [relu(mac_1d(l1_out, w2[r])) for r in range(6)]
l3_out = [mac_1d(l2_out, w3[r]) for r in range(10)]

# 4. Argmax
def to_signed(val): return val - 65536 if (val & 0x8000) else val
pred = max(range(10), key=lambda i: to_signed(l3_out[i]))

# 5. Export Hex (Strict 16-bit 2's complement masking)
def write_hex(fn, data): 
    open(fn, 'w').write('\n'.join(f"{v & 0xFFFF:04x}" for v in data))
def write_hex_2d(fn, data): 
    open(fn, 'w').write('\n'.join(f"{v & 0xFFFF:04x}" for row in data for v in row))

write_hex('verilog_src/e2e_input.hex', inputs)
write_hex_2d('verilog_src/e2e_w1.hex', w1)
write_hex_2d('verilog_src/e2e_w2.hex', w2)
write_hex_2d('verilog_src/e2e_w3.hex', w3)

print(f"E2E Golden Model Expected Prediction: Digit {pred}")