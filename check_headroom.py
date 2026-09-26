import torch
import numpy as np
from test_headless_drawing import get_model, draw_digit, preprocess

def check_headroom():
    model = get_model()
    for digit in range(10):
        img = draw_digit(digit)
        # Without erosion (as is the case now)
        proc_img = preprocess(img, False)
        inp = torch.tensor(proc_img.flatten(), dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            x = inp
            out_fc1 = model.fc1(x)
            out_relu1 = model.relu(out_fc1)
            out_fc2 = model.fc2(out_relu1)
            out_relu2 = model.relu(out_fc2)
            out_fc3 = model.fc3(out_relu2)
            
            max_l1 = out_fc1.abs().max().item()
            max_l2 = out_fc2.abs().max().item()
            max_l3 = out_fc3.abs().max().item()
            
            print(f"Digit {digit}: Max L1={max_l1:.2f}, Max L2={max_l2:.2f}, Max L3={max_l3:.2f}")

if __name__ == "__main__":
    check_headroom()
