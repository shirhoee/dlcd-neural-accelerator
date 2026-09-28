import torch
import torch.nn as nn
from fixed_point_math import to_q7_8

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(200, 64, bias=False)
        self.fc2 = nn.Linear(64, 32, bias=False)
        self.fc3 = nn.Linear(32, 10, bias=False)
        self.relu = nn.ReLU()

def hex16(val): return f"{(val & 0xFFFF):04x}"

def hex_to_signed_16(h):
    if isinstance(h, int):
        val = h
    else:
        val = int(h, 16)
    return val if val < 32768 else val - 65536

def main():
    model = Net()
    model.load_state_dict(torch.load('v2/python_golden_model/v2_n0_model.pt', map_location='cpu'))
    
    conv2_w = model.conv2.weight.detach().numpy() # [8, 4, 3, 3]
    
    w_q = []
    for oc in range(8):
        oc_w = []
        for ic in range(4):
            ic_w = []
            for h in range(3):
                for w in range(3):
                    ic_w.append(to_q7_8(conv2_w[oc, ic, h, w]))
            oc_w.append(ic_w)
        w_q.append(oc_w)
        
    with open('v2/python_golden_model/conv2_weights_q7_8.txt', 'w') as f:
        for oc in range(8):
            for ic in range(4):
                for tap in range(9):
                    f.write(hex16(w_q[oc][ic][tap]) + "\n")
                    
    with open('v2/python_golden_model/expected_maxpool_out.txt', 'r') as f:
        lines = [l.strip().split() for l in f if l.strip()]
        
    in_grid = [[[] for _ in range(10)] for _ in range(4)]
    for i, parts in enumerate(lines):
        r = i // 10
        c = i % 10
        for ch in range(4):
            in_grid[ch][r].append(hex_to_signed_16(parts[ch]))
            
    out_lines = []
    for r in range(10):
        for c in range(10):
            out_vals = []
            for oc in range(8):
                acc = 0
                for ic in range(4):
                    for kr in range(3):
                        for kc in range(3):
                            in_r = r + kr - 1
                            in_c = c + kc - 1
                            if 0 <= in_r < 10 and 0 <= in_c < 10:
                                p_val = in_grid[ic][in_r][in_c]
                            else:
                                p_val = 0
                            
                            wt = hex_to_signed_16(w_q[oc][ic][kr * 3 + kc])
                            prod = wt * p_val
                            trunc = (prod >> 8) & 0xFFFF
                            if trunc >= 32768: trunc -= 65536
                            acc += trunc
                            
                acc_16 = acc & 0xFFFF
                if acc_16 >= 32768: acc_16 -= 65536
                out_vals.append(hex16(acc_16))
            out_lines.append(" ".join(out_vals))
            
    with open('v2/python_golden_model/expected_conv2_out.txt', 'w') as f:
        f.write("\n".join(out_lines) + "\n")
        
    print(f"Generated {len(out_lines)} Conv2 output vectors.")

if __name__ == '__main__':
    main()
