import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

EPOCHS = 50
BATCH_SIZE = 128
LR = 0.002

class ConvMLP_V2_TrueSpec(nn.Module):
    def __init__(self):
        super(ConvMLP_V2_TrueSpec, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()
        
        # 200 -> 64 -> 32 -> 10, all bias-free
        self.fc1 = nn.Linear(200, 64, bias=False)
        self.fc2 = nn.Linear(64, 32, bias=False)
        self.fc3 = nn.Linear(32, 10, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(self.relu(x))
        x = self.conv2(x)
        x = self.pool2(self.relu(x))
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def to_q7_8(val):
    q_val = int(round(val * 256.0))
    if q_val > 32767: q_val = 32767
    if q_val < -32768: q_val = -32768
    return q_val

def hex16(val):
    return f"{(val & 0xFFFF):04X}"

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST(root='../../data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = ConvMLP_V2_TrueSpec().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    print("Training 200->64->32->10 model...")
    model.train()
    for epoch in range(1, EPOCHS + 1):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.cross_entropy(output, target)
            loss.backward()
            optimizer.step()
        scheduler.step()
        print(f"Epoch {epoch} loss: {loss.item():.4f}, LR: {scheduler.get_last_lr()[0]:.6f}")
        
    model.cpu()
    
    # Headroom Gate Check
    # Simulate test data and find max logit amplitude to ensure it fits in Q7.8 range [-128, 127.99]
    test_dataset = datasets.MNIST(root='../../data', train=False, download=True, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    model.eval()
    max_logit_abs = 0.0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            out = model(data)
            max_logit_abs = max(max_logit_abs, out.abs().max().item())
            pred = out.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            
    print(f"\nFinal Test Accuracy: {100. * correct / len(test_dataset):.2f}%")
    print(f"HEADROOM GATE CHECK: Max absolute logit = {max_logit_abs:.2f}")
    if max_logit_abs > 127.99:
        print("WARNING: Max logit exceeds Q7.8 range [-128.0, 127.99]! Saturation clipping will degrade accuracy.")
    else:
        print("HEADROOM GATE PASSED: Logits fit well within Q7.8 range.")
        
    torch.save(model.state_dict(), "v2_n13_model.pt")
    
    print("\nExporting weights to Q7.8...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Conv1/Conv2 remain standard flattened format
    with open(os.path.join(base_dir, "weights_q7_8.txt"), "w") as f:
        w1 = model.conv1.weight.detach().numpy()
        for oc in range(4):
            for r in range(3):
                for c in range(3):
                    val = w1[oc, 0, r, c]
                    f.write(f"{hex16(to_q7_8(val))}\n")
                    
    with open(os.path.join(base_dir, "conv2_weights_q7_8.txt"), "w") as f:
        w2 = model.conv2.weight.detach().numpy()
        for oc in range(8):
            for ic in range(4):
                for r in range(3):
                    for c in range(3):
                        val = w2[oc, ic, r, c]
                        f.write(f"{hex16(to_q7_8(val))}\n")
                        
    # N14 Systolic Array tiling export format
    # In V1, the systolic array handles matrix multiplication by reading weights.
    # The V1 systolic array is tiled. But how did V1 export its weights?
    # Let's write them out raw and figure out the exact load order in N14.
    # For now, let's export them in standard PyTorch shape flattened.
    with open(os.path.join(base_dir, "dense1_q7_8.txt"), "w") as f:
        w = model.fc1.weight.detach().numpy() # [64, 200]
        for val in w.flatten():
            f.write(f"{hex16(to_q7_8(val))}\n")
            
    with open(os.path.join(base_dir, "dense2_q7_8.txt"), "w") as f:
        w = model.fc2.weight.detach().numpy() # [32, 64]
        for val in w.flatten():
            f.write(f"{hex16(to_q7_8(val))}\n")
            
    with open(os.path.join(base_dir, "dense3_q7_8.txt"), "w") as f:
        w = model.fc3.weight.detach().numpy() # [10, 32]
        for val in w.flatten():
            f.write(f"{hex16(to_q7_8(val))}\n")

    print("All weights exported successfully!")

if __name__ == '__main__':
    main()
