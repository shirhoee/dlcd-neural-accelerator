import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

EPOCHS = 50
BATCH_SIZE = 128
LR = 0.002

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

    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(self.relu(x))
        x = self.conv2(x)
        x = self.pool2(self.relu(x))
        x = self.flatten(x)
        x = self.fc(x)
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
    
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = ConvMLP_V2().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    print("Training model...")
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
    
    print("Exporting weights to Q7.8...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Conv1 Weights
    # Shape: [4, 1, 3, 3] -> 4 channels, 9 taps each
    with open(os.path.join(base_dir, "weights_q7_8.txt"), "w") as f:
        w1 = model.conv1.weight.detach().numpy()
        for oc in range(4):
            # HW tap order: exactly flattened 3x3
            for r in range(3):
                for c in range(3):
                    val = w1[oc, 0, r, c]
                    f.write(f"{hex16(to_q7_8(val))}\n")
                    
    # 2. Conv2 Weights
    # Shape: [8, 4, 3, 3] -> 8 out_channels, 4 in_channels, 9 taps each
    with open(os.path.join(base_dir, "conv2_weights_q7_8.txt"), "w") as f:
        w2 = model.conv2.weight.detach().numpy()
        for oc in range(8):
            for ic in range(4):
                for r in range(3):
                    for c in range(3):
                        val = w2[oc, ic, r, c]
                        f.write(f"{hex16(to_q7_8(val))}\n")
                        
    # 3. Dense Weights (The Flatten Trap Fix)
    # Shape in PyTorch: [10, 200]
    # We must explicitly view it as [10, 8, 5, 5], permute to [10, 5, 5, 8], and flatten to match HW output order
    with open(os.path.join(base_dir, "dense_weights_q7_8.txt"), "w") as f:
        w3 = model.fc.weight.detach()
        # [10, 8, 5, 5] -> [out_classes, channels, height, width]
        w3 = w3.view(10, 8, 5, 5)
        # HW output order is spatial first (H, W), then channels (8 channels arrive simultaneously, but dot product flattens them)
        # Wait, how does dense_pe.v read the weights?
        # N7 analysis: maxpool2 outputs [8] channels for 25 spatial cycles.
        # So the flattened data is grouped by spatial cycle, with 8 channels per cycle.
        # PyTorch flatten is [Channel, H, W]. We need [H, W, Channel].
        w3 = w3.permute(0, 2, 3, 1).reshape(10, 200).numpy()
        for i in range(200):
            # Dense pe receives 8 weights per cycle. Actually, dense_array.v uses readmemh.
            # Let's write them such that the ROM is populated with exactly the right order.
            # dense_array.v reads into dense_weights[0:1999].
            # Index is digit * 200 + i.
            pass
            
        for digit in range(10):
            for i in range(200):
                val = w3[digit, i]
                f.write(f"{hex16(to_q7_8(val))}\n")

    print("All weights exported successfully!")

if __name__ == '__main__':
    main()
