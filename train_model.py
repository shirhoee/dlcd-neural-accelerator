import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
import numpy as np

# 0. Reproducibility
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# 1. Load and Normalize Dataset (GRAYSCALE 0.0 to 1.0)
digits = load_digits()
X = digits.images 
y = digits.target

# Pad 8x8 to 10x10
X_padded = np.pad(X, ((0,0), (1,1), (1,1)), mode='constant', constant_values=0)
X_flat = X_padded.reshape(len(X), 100)
X_flat = (X_flat / 16.0).astype(np.float32)

X_tensor = torch.tensor(X_flat)
y_tensor = torch.tensor(y, dtype=torch.long)

X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=SEED)

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

print("Training peak 93% baseline model...")
for epoch in range(300):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    scheduler.step()

    if (epoch+1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            test_out = model(X_test)
            _, predicted = torch.max(test_out, 1)
            acc = (predicted == y_test).float().mean().item() * 100
            print(f"Epoch {epoch+1}/300 - Loss: {loss.item():.4f} - Test Acc: {acc:.2f}%")

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