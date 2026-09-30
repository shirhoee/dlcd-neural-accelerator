import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

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

def parse_hex16(line):
    val = int(line.strip(), 16)
    return val if val < 32768 else val - 65536

def load_q7_8_weights(model, base_dir):
    with open(os.path.join(base_dir, "weights_q7_8.txt")) as f:
        lines = f.readlines()
    w1 = torch.zeros((4, 1, 3, 3))
    idx = 0
    for oc in range(4):
        for r in range(3):
            for c in range(3):
                w1[oc, 0, r, c] = parse_hex16(lines[idx]) / 256.0
                idx += 1
    model.conv1.weight.data = w1
    
    with open(os.path.join(base_dir, "conv2_weights_q7_8.txt")) as f:
        lines = f.readlines()
    w2 = torch.zeros((8, 4, 3, 3))
    idx = 0
    for oc in range(8):
        for ic in range(4):
            for r in range(3):
                for c in range(3):
                    w2[oc, ic, r, c] = parse_hex16(lines[idx]) / 256.0
                    idx += 1
    model.conv2.weight.data = w2
    
    with open(os.path.join(base_dir, "dense_weights_q7_8.txt")) as f:
        lines = f.readlines()
    w3_hw = torch.zeros((10, 200))
    idx = 0
    for digit in range(10):
        for i in range(200):
            w3_hw[digit, i] = parse_hex16(lines[idx]) / 256.0
            idx += 1
            
    w3_hw = w3_hw.view(10, 5, 5, 8)
    w3_pt = w3_hw.permute(0, 3, 1, 2)
    model.fc.weight.data = w3_pt.reshape(10, 200)

def main():
    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Load MNIST Test set
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)
    
    model = ConvMLP_V2()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Loading hardware Q7.8 weights back into PyTorch...")
    load_q7_8_weights(model, base_dir)
    model.eval()
    
    print("Evaluating over 10,000 test images...")
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += len(target)
            
    print(f"Hardware-Quantized Accuracy: {100. * correct / total:.2f}% ({correct}/{total})")

if __name__ == '__main__':
    main()
