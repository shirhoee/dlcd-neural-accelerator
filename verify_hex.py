# Verify golden model from the actual hex files
def read_hex(fn):
    with open(fn) as f:
        return [int(line.strip(), 16) for line in f]

def to_signed(v): return v - 65536 if (v & 0x8000) else v
def mul(a, b):
    a_s = to_signed(a); b_s = to_signed(b)
    return ((a_s * b_s) >> 8) & 0xFFFF
def add(a, b):
    a_s = to_signed(a); b_s = to_signed(b)
    return (a_s + b_s) & 0xFFFF
def relu(a): return 0 if (a & 0x8000) else a

inputs = read_hex('verilog_src/e2e_input.hex')
w1_flat = read_hex('verilog_src/e2e_w1.hex')
w2_flat = read_hex('verilog_src/e2e_w2.hex')
w3_flat = read_hex('verilog_src/e2e_w3.hex')

print(f"Inputs: {len(inputs)} (first 5: {[to_signed(x) for x in inputs[:5]]})")
print(f"W1: {len(w1_flat)} weights")
print(f"W2: {len(w2_flat)} weights")
print(f"W3: {len(w3_flat)} weights")

# Reshape W1: 16x100
w1 = [w1_flat[r*100:(r+1)*100] for r in range(16)]
# Reshape W2: 6x16
w2 = [w2_flat[r*16:(r+1)*16] for r in range(6)]
# Reshape W3: 10x6
w3 = [w3_flat[r*6:(r+1)*6] for r in range(10)]

def mac_1d(inp, w):
    acc = 0
    for i, wi in zip(inp, w):
        acc = add(acc, mul(i, wi))
    return acc

# L1
l1 = [relu(mac_1d(inputs, w1[r])) for r in range(16)]
print("\nL1 (post-ReLU):")
for r, v in enumerate(l1):
    print(f"  {r}: {v:04x} ({to_signed(v)})")

# L2
l2 = [relu(mac_1d(l1, w2[r])) for r in range(6)]
print("\nL2 (post-ReLU):")
for r, v in enumerate(l2):
    print(f"  {r}: {v:04x} ({to_signed(v)})")

# L3
l3 = [mac_1d(l2, w3[r]) for r in range(10)]
print("\nL3 (logits):")
for r, v in enumerate(l3):
    print(f"  {r}: {v:04x} ({to_signed(v)})")

pred = max(range(10), key=lambda i: to_signed(l3[i]))
print(f"\nGolden Prediction: Digit {pred}")