import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
import numpy as np

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

digits = load_digits()
X = digits.images
y = digits.target
X_padded = np.pad(X, ((0,0), (1,1), (1,1)), mode='constant', constant_values=0)
X_flat = X_padded.reshape(len(X), 100)
X_flat = (X_flat > 8).astype(np.float32)
X_tensor = torch.tensor(X_flat)
y_tensor = torch.tensor(y, dtype=torch.long)
X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=SEED)

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
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)

for epoch in range(150):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

model.eval()
sample_img = X_test[0]
sample_img_q = (sample_img * 256).round().to(torch.int32)

w1_q = torch.round(model.fc1.weight * 256).to(torch.int32)
w2_q = torch.round(model.fc2.weight * 256).to(torch.int32)
w3_q = torch.round(model.fc3.weight * 256).to(torch.int32)

def mac_step(acc, x_val, w_val):
    prod = ((x_val * w_val) >> 8) & 0xFFFF
    return (acc + prod) & 0xFFFF

# L1
acc1 = torch.zeros(16, dtype=torch.int32)
for i in range(16):
    acc = 0
    for j in range(100):
        acc = mac_step(acc, sample_img_q[j].item(), w1_q[i, j].item())
    acc1[i] = acc & 0xFFFF
acc1 = torch.where((acc1 & 0x8000).bool(), torch.zeros_like(acc1), acc1)
print("L1:", [f"{v:04x}" for v in acc1.tolist()])

# L2
acc2 = torch.zeros(6, dtype=torch.int32)
for i in range(6):
    acc = 0
    for j in range(16):
        acc = mac_step(acc, acc1[j].item(), w2_q[i, j].item())
    acc2[i] = acc & 0xFFFF
acc2 = torch.where((acc2 & 0x8000).bool(), torch.zeros_like(acc2), acc2)
print("L2:", [f"{v:04x}" for v in acc2.tolist()])

# L3
acc3 = torch.zeros(10, dtype=torch.int32)
for i in range(10):
    acc = 0
    for j in range(6):
        acc = mac_step(acc, acc2[j].item(), w3_q[i, j].item())
    acc3[i] = acc & 0xFFFF
print("L3:", [f"{v:04x}" for v in acc3.tolist()])

# Convert to signed for argmax
def to_signed(v):
    return v - 65536 if (v & 0x8000) else v

signed_logits = [to_signed(v) for v in acc3.tolist()]
print("Signed L3:", signed_logits)
pred = torch.argmax(torch.tensor(signed_logits)).item()
print(f"PyTorch Quantized Prediction: Digit {pred}")