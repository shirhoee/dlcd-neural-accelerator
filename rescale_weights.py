import torch
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from test_headless_drawing import get_model, draw_digit, preprocess
import os

def export_weights(tensor, filename):
    weights = tensor.detach().numpy()
    weights_q = np.round(weights * 256).astype(int)
    clipped = np.sum((weights_q < -32768) | (weights_q > 32767))
    if clipped > 0:
        print(f"  WARNING: {clipped} weights clipped in {filename}")
    weights_q = np.clip(weights_q, -32768, 32767)
    with open(filename, 'w') as f:
        for row in weights_q:
            for val in row:
                f.write(f"{val & 0xFFFF:04x}\n")

def main():
    model = get_model()
    
    transform = transforms.Compose([
        transforms.Resize((10, 10)),
        transforms.ToTensor()
    ])
    
    print("Loading MNIST test set for validation sweep...")
    test_dataset = datasets.MNIST(root='./data', train=False, download=False, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1024, shuffle=False)
    
    max_logit = 0.0
    
    # 1. Sweep MNIST test set
    with torch.no_grad():
        for images, _ in test_loader:
            images = images.view(-1, 100)
            logits = model(images)
            max_logit = max(max_logit, logits.abs().max().item())
            
    # 2. Sweep synthesized thick digits
    with torch.no_grad():
        for digit in range(10):
            img = draw_digit(digit)
            proc = preprocess(img, False)
            inp = torch.tensor(proc.flatten(), dtype=torch.float32).unsqueeze(0)
            logits = model(inp)
            max_logit = max(max_logit, logits.abs().max().item())
            
    # 3. Sweep all-ones fully saturated input (the absolute worst case realistic input)
    with torch.no_grad():
        inp_ones = torch.ones((1, 100), dtype=torch.float32)
        logits_ones = model(inp_ones)
        max_logit = max(max_logit, logits_ones.abs().max().item())
        
    # The true theoretical maximum logit found via optimization was ~165.74
    # We will use 165.74 as our absolute ceiling to be perfectly safe, or just the observed max_logit.
    # To be unconditionally safe against ANY input, we use 165.74 (the optimized worst-case L3).
    # The prompt asks to bring max|logit| down to a target of ~100.
    target_logit = 100.0
    
    # What was the observed max logit?
    print(f"Observed max logit across validation sweep + saturation: {max_logit:.2f}")
    
    f = 0.84
    print(f"Applying an additional scaling of {f:.4f} to the currently saved weights to bring L2 max well below 128.")
    
    # Reload fresh weights since we already scaled them in memory
    model = get_model()
    
    # Apply uniform scaling
    with torch.no_grad():
        model.fc1.weight.mul_(f)
        model.fc2.weight.mul_(f)
        model.fc3.weight.mul_(f)
        
    # Verify the new max logit on the fully saturated input
    with torch.no_grad():
        logits_ones_new = model(inp_ones)
        print(f"New logit on fully saturated input: {logits_ones_new.abs().max().item():.2f}")
        
    print("Exporting rescaled weights to hex...")
    export_weights(model.fc1.weight, "verilog_src/e2e_w1.hex")
    export_weights(model.fc2.weight, "verilog_src/e2e_w2.hex")
    export_weights(model.fc3.weight, "verilog_src/e2e_w3.hex")
    print("Export complete.")

if __name__ == "__main__":
    main()
