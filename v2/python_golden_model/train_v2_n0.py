import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np

EPOCHS = 2
BATCH_SIZE = 128
LR = 0.001

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

    def forward(self, x, return_all_logits=False):
        out_c1 = self.conv1(x)
        act1 = self.pool1(self.relu(out_c1))
        out_c2 = self.conv2(act1)
        act2 = self.pool2(self.relu(out_c2))
        flat = self.flatten(act2)
        out_fc = self.fc(flat)
        
        if return_all_logits:
            return out_fc, out_c1, out_c2
        return out_fc

def train_and_export():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    model = ConvMLP_V2().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    
    print("--- Training V2 N7 Model (Short Run) ---")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.cross_entropy(output, target)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch} Complete.")

    torch.save(model.state_dict(), 'v2/python_golden_model/v2_n0_model.pt')
    print("Model saved to v2_n0_model.pt.")

if __name__ == '__main__':
    train_and_export()
