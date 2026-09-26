import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import numpy as np

# 0. Reproducibility
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# 1. Load and Normalize Dataset (GRAYSCALE 0.0 to 1.0)
transform = transforms.Compose([
    transforms.Resize((10, 10)),
    transforms.ToTensor()
])

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

print("Pre-processing datasets into memory...", flush=True)
X_train_list, y_train_list = [], []
for images, labels in DataLoader(train_dataset, batch_size=1024):
    X_train_list.append(images)
    y_train_list.append(labels)
X_train = torch.cat(X_train_list)
y_train = torch.cat(y_train_list)

X_test_list, y_test_list = [], []
for images, labels in DataLoader(test_dataset, batch_size=1024):
    X_test_list.append(images)
    y_test_list.append(labels)
X_test = torch.cat(X_test_list)
y_test = torch.cat(y_test_list)

train_loader = DataLoader(torch.utils.data.TensorDataset(X_train, y_train), batch_size=1024, shuffle=True)
test_loader = DataLoader(torch.utils.data.TensorDataset(X_test, y_test), batch_size=1024, shuffle=False)

# 2. Define Pure VerilogNet (100 -> 16 -> 6 -> 10, No Bias, No Dropout)
class VerilogNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(100, 16, bias=False)
        self.fc2 = nn.Linear(16, 6, bias=False)
        self.fc3 = nn.Linear(6, 10, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = VerilogNet()

# 3. Train Model (300 Epochs, Cosine Annealing)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-5)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=300)

print("Training MNIST model...")
for epoch in range(300):
    model.train()
    for images, labels in train_loader:
        images = images.view(-1, 100)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    scheduler.step()

    if (epoch+1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in test_loader:
                images = images.view(-1, 100)
                test_out = model(images)
                _, predicted = torch.max(test_out, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            acc = correct / total * 100
            print(f"Epoch {epoch+1}/300 - Loss: {loss.item():.4f} - Test Acc: {acc:.2f}%")

X_test = []
y_test = []
for images, labels in test_loader:
    X_test.append(images.view(-1, 100))
    y_test.append(labels)
X_test = torch.cat(X_test)
y_test = torch.cat(y_test)

# Check max logit headroom for Q7.8 (+/- 127.99)
model.eval()
with torch.no_grad():
    all_logits = model(X_test)
max_abs = all_logits.abs().max().item()
print(f"\nMax absolute logit across test set: {max_abs:.4f} (Q7.8 allows up to 127.99)")

# 4. STRICT Q7.8 EXPORT (Multiplier = 256)
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

print("Exporting Q7.8 weights to verilog_src/...")
export_weights(model.fc1.weight, 'verilog_src/e2e_w1.hex')
export_weights(model.fc2.weight, 'verilog_src/e2e_w2.hex')
export_weights(model.fc3.weight, 'verilog_src/e2e_w3.hex')

# 5. Export Test Image (Q7.8)
sample_img = X_test[0]
sample_label = y_test[0].item()

with torch.no_grad():
    golden_logits = model(sample_img.unsqueeze(0))
    golden_pred = torch.argmax(golden_logits, dim=1).item()

with open('verilog_src/e2e_input.hex', 'w') as f:
    for val in sample_img.numpy():
        v_int = int(val * 256)
        f.write(f"{v_int & 0xFFFF:04x}\n")

with open('verilog_src/e2e_true_label.txt', 'w') as f:
    f.write(str(golden_pred))

print(f"Exported test image. Dataset Ground Truth: DIGIT {sample_label} | PyTorch Float Prediction: DIGIT {golden_pred}")