import torch
import numpy as np
from test_headless_drawing import get_model

def check_headroom():
    model = get_model()
    # Fully saturated image
    inp = torch.ones((1, 100), dtype=torch.float32)
    
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
        
        print(f"All-Ones Input: Max L1={max_l1:.2f}, Max L2={max_l2:.2f}, Max L3={max_l3:.2f}")

if __name__ == "__main__":
    check_headroom()
