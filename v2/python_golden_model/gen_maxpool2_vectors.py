import os

def hex16(val): return f"{(val & 0xFFFF):04x}"

def hex_to_signed_16(h):
    val = int(h, 16)
    return val if val < 32768 else val - 65536
    
def main():
    with open('v2/python_golden_model/expected_conv2_out.txt', 'r') as f:
        lines = [l.strip().split() for l in f if l.strip()]
        
    in_grid = [[[] for _ in range(10)] for _ in range(8)]
    for i, parts in enumerate(lines):
        r = i // 10
        c = i % 10
        for ch in range(8):
            in_grid[ch][r].append(hex_to_signed_16(parts[ch]))
            
    out_lines = []
    for r in range(5):
        for c in range(5):
            out_vals = []
            for ch in range(8):
                v0 = in_grid[ch][r*2][c*2]
                v1 = in_grid[ch][r*2][c*2+1]
                v2 = in_grid[ch][r*2+1][c*2]
                v3 = in_grid[ch][r*2+1][c*2+1]
                max_val = max(v0, v1, v2, v3)
                relu_val = max_val if max_val > 0 else 0
                out_vals.append(hex16(relu_val))
            out_lines.append(" ".join(out_vals))
            
    with open('v2/python_golden_model/expected_maxpool2_out.txt', 'w') as f:
        f.write("\n".join(out_lines) + "\n")
        
    print(f"Generated {len(out_lines)} MaxPool2 output vectors.")

if __name__ == '__main__':
    main()
