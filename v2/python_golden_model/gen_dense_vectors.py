import torch
import torch.nn as nn

SCALE = 256.0
MAX_VAL = 32767
MIN_VAL = -32768
MASK = 0xFFFF

def to_q7_8(f):
    val = int(round(f * SCALE))
    if val > MAX_VAL: val = MAX_VAL
    if val < MIN_VAL: val = MIN_VAL
    return val & MASK

def hex16(val): return f"{(val & 0xFFFF):04x}"

def hex_to_signed_16(h):
    val = int(h, 16)
    return val if val < 32768 else val - 65536

class ConvMLP_V2(nn.Module):
    def __init__(self):
        super(ConvMLP_V2, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(200, 10, bias=False)
        self.relu = nn.ReLU()

def main():
    model = ConvMLP_V2()
    model.load_state_dict(torch.load('v2/python_golden_model/v2_n0_model.pt', map_location='cpu'))
    
    # 1. Solve the Flatten Trap
    w = model.fc.weight.detach() # shape [10, 200]
    w = w.view(10, 8, 5, 5)
    w = w.permute(0, 2, 3, 1) # shape [10, 5, 5, 8]
    w = w.reshape(10, 200)
    
    w_np = w.numpy()
    
    # Quantize and export
    with open('v2/python_golden_model/dense_weights_q7_8.txt', 'w') as f:
        for out_idx in range(10):
            for in_idx in range(200):
                f.write(hex16(to_q7_8(w_np[out_idx, in_idx])) + "\n")
                
    # Read maxpool2 output
    with open('v2/python_golden_model/expected_maxpool2_out.txt', 'r') as f:
        lines = [l.strip().split() for l in f if l.strip()]
    
    # Flatten the 25 pulses (each with 8 channels) into a single 200-element array
    mp2_flat = []
    for line in lines:
        for val in line:
            mp2_flat.append(hex_to_signed_16(val))
            
    # Integer dot product
    dense_out = []
    for out_idx in range(10):
        acc = 0
        for in_idx in range(200):
            wt = hex_to_signed_16(hex16(to_q7_8(w_np[out_idx, in_idx])))
            px = mp2_flat[in_idx]
            prod = wt * px
            trunc = (prod >> 8) & 0xFFFF
            if trunc >= 32768: trunc -= 65536
            acc += trunc
        
        acc_16 = acc & 0xFFFF
        if acc_16 >= 32768: acc_16 -= 65536
        dense_out.append(hex16(acc_16))
        
    with open('v2/python_golden_model/expected_dense_out.txt', 'w') as f:
        f.write(" ".join(dense_out) + "\n")
        
    print(f"Generated dense weights and 10 expected output logits.")

if __name__ == '__main__':
    main()
