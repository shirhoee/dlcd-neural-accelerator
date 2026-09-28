import os

def hex_to_signed_16(h):
    val = int(h, 16)
    return val if val < 32768 else val - 65536

def signed_16_to_hex(val):
    return f"{(val & 0xFFFF):04x}"

def relu(x):
    return x if x > 0 else 0

def maxpool_array_vectors():
    # Read conv1 output vectors
    # Format: CH0_HEX CH1_HEX CH2_HEX CH3_HEX
    conv_file = 'v2/python_golden_model/expected_conv1_out.txt'
    with open(conv_file, 'r') as f:
        lines = [l.strip().split() for l in f if l.strip()]
        
    assert len(lines) == 400, f"Expected 400 conv1 outputs, got {len(lines)}"
    
    # Restructure into 20x20 grids per channel
    grids = [[[] for _ in range(20)] for _ in range(4)]
    
    for i, parts in enumerate(lines):
        r = i // 20
        for ch in range(4):
            val = hex_to_signed_16(parts[ch])
            grids[ch][r].append(val)
            
    # Compute maxpool + relu
    # 10x10 output per channel
    out_lines = []
    
    neg_conv_count = 0
    neg_max_count = 0
    
    for r in range(0, 20, 2):
        for c in range(0, 20, 2):
            out_ch = []
            for ch in range(4):
                # 2x2 window
                w = [
                    grids[ch][r][c], grids[ch][r][c+1],
                    grids[ch][r+1][c], grids[ch][r+1][c+1]
                ]
                
                for v in w:
                    if v < 0: neg_conv_count += 1
                
                max_val = max(w)
                if max_val < 0: neg_max_count += 1
                
                # relu(max(x))
                res1 = relu(max_val)
                # max(relu(x))
                res2 = max([relu(v) for v in w])
                
                assert res1 == res2, f"Math mismatch at ch{ch} {r},{c}: relu(max)={res1}, max(relu)={res2}"
                
                out_ch.append(signed_16_to_hex(res1))
            out_lines.append(" ".join(out_ch))
            
    assert len(out_lines) == 100, f"Expected 100 maxpool outputs, got {len(out_lines)}"
    
    with open('v2/python_golden_model/expected_maxpool_out.txt', 'w') as f:
        f.write("\n".join(out_lines) + "\n")
        
    print(f"Generated 100 expected maxpool outputs.")
    print(f"Negative conv outputs: {neg_conv_count}")
    print(f"Negative max windows: {neg_max_count}")

if __name__ == '__main__':
    maxpool_array_vectors()
