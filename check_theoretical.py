import torch
import numpy as np
from test_headless_drawing import get_model

def check_max_possible_headroom():
    model = get_model()
    
    # Layer 1 max possible activation
    w1 = model.fc1.weight.data
    # input is [0, 1]. Max activation for each neuron is sum of positive weights.
    max_act1 = torch.clamp(w1, min=0).sum(dim=1)
    print(f"Max possible L1 activations: {max_act1}")
    print(f"Absolute max possible L1: {max_act1.max().item():.2f}")
    
    # Layer 2 max possible
    # We can just feed max_act1 into Layer 2? No, because input to L2 is relu(L1)
    # The max possible input to L2 is max_act1.
    w2 = model.fc2.weight.data
    max_input_l2 = max_act1.unsqueeze(0) # Not exactly, because L1 activations are correlated, but let's upper bound
    # To get upper bound, we assume we can independently maximize each L1 neuron, which is impossible, but it's a bound.
    # Actually, the maximum possible L2 output is when L1 is maxed out for positive L2 weights.
    max_act2 = torch.matmul(max_input_l2, torch.clamp(w2.t(), min=0)).squeeze()
    print(f"Absolute max possible L2: {max_act2.max().item():.2f}")
    
    # Layer 3
    w3 = model.fc3.weight.data
    max_input_l3 = max_act2.unsqueeze(0)
    max_act3 = torch.matmul(max_input_l3, torch.clamp(w3.t(), min=0)).squeeze()
    print(f"Absolute max possible L3: {max_act3.max().item():.2f}")

    # Let's also check actual max in training set
    from torchvision import datasets, transforms
    transform = transforms.Compose([transforms.Resize((10, 10)), transforms.ToTensor()])
    dataset = datasets.MNIST(root='./data', train=True, download=False, transform=transform)
    from torch.utils.data import DataLoader
    loader = DataLoader(dataset, batch_size=1024)
    
    max_l3_observed = 0
    for images, _ in loader:
        images = images.view(-1, 100)
        logits = model(images)
        max_l3_observed = max(max_l3_observed, logits.abs().max().item())
        
    print(f"Max observed L3 logit in MNIST train set: {max_l3_observed:.2f}")

if __name__ == "__main__":
    check_max_possible_headroom()
