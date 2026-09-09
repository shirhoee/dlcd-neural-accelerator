import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
import numpy as np

# 0. Reproducibility — fix all seeds so this run can be reproduced later
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# 1. Load and Pad Dataset (8x8 -> 10x10)
digits = load_digits()
X = digits.images # (1797, 8, 8)
y = digits.target

# Pad with 1 pixel on all sides to make it 10x10 (100 pixels)
X_padded = np.pad(X, ((0,0), (1,1), (1,1)), mode='constant', constant_values=0)
X_flat = X_padded.reshape(len(X), 100)

# Binarize inputs: > 8 intensity (out of 16) becomes 1.0, else 0.0
X_flat = (X_flat > 8).astype(np.float32)

X_tensor = torch.tensor(X_flat)
y_tensor = torch.tensor(y, dtype=torch.long)

X_train, X_test, y_train, y_test = train_test_split(
    X_tensor, y_tensor, test_size=0.2, random_state=SEED
)

# 2. Define the Model (NO BIASES to match Verilog hardware)
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

# 3. Train the Model (with weight decay to suppress large weights)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)

print("Training 100 -> 16 -> 6 -> 10 Verilog Model...")
for epoch in range(150):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

    if (epoch+1) % 50 == 0:
        with torch.no_grad():
            test_out = model(X_test)
            _, predicted = torch.max(test_out, 1)
            acc = (predicted == y_test).float().mean().item() * 100
            print(f"Epoch {epoch+1}/150 - Loss: {loss.item():.4f} - Test Acc: {acc:.2f}%")

# 4. Quantize and Export Weights (Q4.12)
def export_weights(tensor, filename):
    weights = tensor.detach().numpy()
    weights_q = np.round(weights * 4096).astype(int)

    # Check for silent clipping (overflowing Q4.12 range)
    clipped = np.sum((weights_q < -32768) | (weights_q > 32767))
    if clipped > 0:
        print(f"  WARNING: {clipped} weights clipped in {filename} — consider stronger weight decay")

    weights_q = np.clip(weights_q, -32768, 32767)

    with open(filename, 'w') as f:
        for row in weights_q:
            for val in row:
                f.write(f"{val & 0xFFFF:04x}\n")

print("\nExporting Q4.12 weights to verilog_src/...")
export_weights(model.fc1.weight, 'verilog_src/e2e_w1.hex')
export_weights(model.fc2.weight, 'verilog_src/e2e_w2.hex')
export_weights(model.fc3.weight, 'verilog_src/e2e_w3.hex')

# 5. Export one test image to verify hardware
sample_img = X_test[0]
sample_label = y_test[0].item()

# Quantize input to Q4.12 (0 or 4096) — this is what hardware sees
sample_img_q = (sample_img * 4096).round().to(torch.int32)

# Get PyTorch's prediction using QUANTIZED input with EXACT hardware MAC behavior
# Q4.12 MAC: at each step, multiply -> >> 12 -> truncate to 16 bits -> add -> truncate to 16 bits
def quantized_forward(x_q, model):
    # x_q: (100,) int32 in Q4.12 (0 or 4096)
    # Convert weights to Q4.12 int
    w1_q = torch.round(model.fc1.weight * 4096).to(torch.int32)  # (16, 100)
    w2_q = torch.round(model.fc2.weight * 4096).to(torch.int32)  # (6, 16)
    w3_q = torch.round(model.fc3.weight * 4096).to(torch.int32)  # (10, 6)

    def mac_step(acc, x_val, w_val):
        # x_val, w_val are Q4.12 signed
        # Product: (x * w) >> 12, truncated to 16 bits
        prod = ((x_val * w_val) >> 12) & 0xFFFF
        # Add with truncation
        return (acc + prod) & 0xFFFF

    # L1: x_q (100,) @ w1_q.T (100, 16) -> (16,)
    acc1 = torch.zeros(16, dtype=torch.int32)
    for i in range(16):
        acc = 0
        for j in range(100):
            acc = mac_step(acc, x_q[j].item(), w1_q[i, j].item())
        acc1[i] = acc & 0xFFFF
    # ReLU: if MSB set (negative), zero it
    acc1 = torch.where((acc1 & 0x8000).bool(), torch.zeros_like(acc1), acc1)

    # L2: acc1 (16,) @ w2_q.T (16, 6) -> (6,)
    acc2 = torch.zeros(6, dtype=torch.int32)
    for i in range(6):
        acc = 0
        for j in range(16):
            acc = mac_step(acc, acc1[j].item(), w2_q[i, j].item())
        acc2[i] = acc & 0xFFFF
    # ReLU
    acc2 = torch.where((acc2 & 0x8000).bool(), torch.zeros_like(acc2), acc2)

    # L3: acc2 (6,) @ w3_q.T (6, 10) -> (10,)
    acc3 = torch.zeros(10, dtype=torch.int32)
    for i in range(10):
        acc = 0
        for j in range(6):
            acc = mac_step(acc, acc2[j].item(), w3_q[i, j].item())
        acc3[i] = acc & 0xFFFF

    return acc3

model.eval()
with torch.no_grad():
    golden_logits_q = quantized_forward(sample_img_q, model)
    # Debug: print logits
    def to_signed(v): return v - 65536 if (v & 0x8000) else v
    print("Debug PyTorch Quantized L3:", [f"{v:04x}({to_signed(v)})" for v in golden_logits_q.tolist()])
    # Convert to signed for argmax (torch.argmax treats int32 as unsigned!)
    golden_logits_signed = torch.tensor([to_signed(v) for v in golden_logits_q.tolist()], dtype=torch.int32)
    golden_pred = torch.argmax(golden_logits_signed).item()

with open('verilog_src/e2e_input.hex', 'w') as f:
    for val in sample_img_q.numpy():
        f.write(f"{int(val) & 0xFFFF:04x}\n")

# Write PyTorch's quantized prediction — this is the target Verilog is graded against
with open('verilog_src/e2e_true_label.txt', 'w') as f:
    f.write(str(golden_pred))

print(f"Exported test image. Dataset Ground Truth: DIGIT {sample_label} | PyTorch Quantized Prediction (Verilog must match this): DIGIT {golden_pred}")
print(f"(Seed={SEED} — rerun this script anytime to reproduce this exact model and test image)")