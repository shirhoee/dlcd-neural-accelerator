#!/usr/bin/env python3
"""
M15: PC-Only Batch Regression Harness
Tests hardware-vs-golden-model agreement across N=20 test-set images.
Does NOT retrain the model — uses cached weights from train_model.py.
"""

import torch
import torch.nn as nn
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
import subprocess
import os
import sys

SEED = 42
N_IMAGES = 20
IVERILOG_PATH = r"C:\iverilog\bin\iverilog.exe"
VVP_PATH = r"C:\iverilog\bin\vvp.exe"
VERILOG_SRC = "verilog_src"

torch.manual_seed(SEED)
np.random.seed(SEED)

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

def load_or_train_model():
    """Load cached weights or train once if not cached."""
    model = VerilogNet()
    
    w1_path = os.path.join(VERILOG_SRC, "e2e_w1.hex")
    w2_path = os.path.join(VERILOG_SRC, "e2e_w2.hex")
    w3_path = os.path.join(VERILOG_SRC, "e2e_w3.hex")
    
    if os.path.exists(w1_path) and os.path.exists(w2_path) and os.path.exists(w3_path):
        print("Loading cached Q7.8 weights...")
        w1_flat = np.array([int(line.strip(), 16) for line in open(w1_path)])
        w2_flat = np.array([int(line.strip(), 16) for line in open(w2_path)])
        w3_flat = np.array([int(line.strip(), 16) for line in open(w3_path)])
        
        def to_signed(v): return v - 65536 if (v & 0x8000) else v
        w1 = np.array([to_signed(v) for v in w1_flat]).reshape(16, 100).astype(np.float32) / 256.0
        w2 = np.array([to_signed(v) for v in w2_flat]).reshape(6, 16).astype(np.float32) / 256.0
        w3 = np.array([to_signed(v) for v in w3_flat]).reshape(10, 6).astype(np.float32) / 256.0
        
        with torch.no_grad():
            model.fc1.weight.copy_(torch.from_numpy(w1))
            model.fc2.weight.copy_(torch.from_numpy(w2))
            model.fc3.weight.copy_(torch.from_numpy(w3))
        print("Cached weights loaded.")
    else:
        print("No cached weights found. Training model...")
        train_model(model)
    
    return model

def train_model(model):
    """Train model and export Q7.8 weights (from train_model.py)."""
    digits = load_digits()
    X = digits.images
    y = digits.target
    X_padded = np.pad(X, ((0,0), (1,1), (1,1)), mode='constant', constant_values=0)
    X_flat = X_padded.reshape(len(X), 100)
    X_flat = (X_flat / 16.0).astype(np.float32)
    
    X_tensor = torch.tensor(X_flat)
    y_tensor = torch.tensor(y, dtype=torch.long)
    X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=SEED)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=300)
    
    for epoch in range(300):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        scheduler.step()
    
    # Export Q7.8 weights
    def export_weights(tensor, filename):
        weights = tensor.detach().numpy()
        weights_q = np.round(weights * 256).astype(int)
        weights_q = np.clip(weights_q, -32768, 32767)
        with open(filename, 'w') as f:
            for row in weights_q:
                for val in row:
                    f.write(f"{val & 0xFFFF:04x}\n")
    
    export_weights(model.fc1.weight, os.path.join(VERILOG_SRC, 'e2e_w1.hex'))
    export_weights(model.fc2.weight, os.path.join(VERILOG_SRC, 'e2e_w2.hex'))
    export_weights(model.fc3.weight, os.path.join(VERILOG_SRC, 'e2e_w3.hex'))
    print("Training complete and weights exported.")

def get_test_images():
    """Get N=20 test images from sklearn digits test set."""
    digits = load_digits()
    X = digits.images
    y = digits.target
    X_padded = np.pad(X, ((0,0), (1,1), (1,1)), mode='constant', constant_values=0)
    X_flat = X_padded.reshape(len(X), 100)
    X_flat = (X_flat / 16.0).astype(np.float32)
    
    X_tensor = torch.tensor(X_flat)
    y_tensor = torch.tensor(y, dtype=torch.long)
    _, X_test, _, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=SEED)
    
    indices = np.random.choice(len(X_test), N_IMAGES, replace=False)
    return X_test[indices], y_test[indices]

def to_q7_8_hex(val):
    """Convert float to Q7.8 hex string."""
    v_int = int(val * 256)
    return f"{v_int & 0xFFFF:04x}"

def write_input_hex(image, filename):
    """Write 100-pixel image as Q7.8 hex file."""
    with open(filename, 'w') as f:
        for val in image.numpy():
            f.write(to_q7_8_hex(val) + "\n")

def to_signed(v): return v - 65536 if (v & 0x8000) else v
def mul_q7_8(a, b):
    a_s = to_signed(a); b_s = to_signed(b)
    return ((a_s * b_s) >> 8) & 0xFFFF
def add_q7_8(a, b):
    a_s = to_signed(a); b_s = to_signed(b)
    return (a_s + b_s) & 0xFFFF
def relu_q7_8(a): return 0 if (a & 0x8000) else a

def mac_1d(inp, w):
    acc = 0
    for i, wi in zip(inp, w):
        acc = add_q7_8(acc, mul_q7_8(i, wi))
    return acc

def golden_predict_q7_8(image, w1, w2, w3):
    """Get Q7.8 fixed-point golden model prediction (matches hardware)."""
    inp = [int(val * 256) & 0xFFFF for val in image.numpy()]
    l1 = [relu_q7_8(mac_1d(inp, w1[r])) for r in range(16)]
    l2 = [relu_q7_8(mac_1d(l1, w2[r])) for r in range(6)]
    l3 = [mac_1d(l2, w3[r]) for r in range(10)]
    return max(range(10), key=lambda i: to_signed(l3[i]))

def load_q7_8_weights():
    """Load Q7.8 weights from hex files as integer arrays."""
    w1_flat = [int(line.strip(), 16) for line in open(os.path.join(VERILOG_SRC, "e2e_w1.hex"))]
    w2_flat = [int(line.strip(), 16) for line in open(os.path.join(VERILOG_SRC, "e2e_w2.hex"))]
    w3_flat = [int(line.strip(), 16) for line in open(os.path.join(VERILOG_SRC, "e2e_w3.hex"))]
    w1 = [w1_flat[r*100:(r+1)*100] for r in range(16)]
    w2 = [w2_flat[r*16:(r+1)*16] for r in range(6)]
    w3 = [w3_flat[r*6:(r+1)*6] for r in range(10)]
    return w1, w2, w3

def run_verilog_sim():
    """Compile and run tb_accelerator_top.v, return predicted digit or None on failure."""
    # Compile (run from verilog_src directory, include all dependent modules)
    cmd_compile = [
        IVERILOG_PATH, "-o", "tb_top.vvp",
        "mac_q7_8.v",
        "systolic_pe.v",
        "systolic_array.v",
        "relu_q7_8.v",
        "layer_relu.v",
        "argmax.v",
        "accelerator_top.v",
        "tb_accelerator_top.v"
    ]
    result = subprocess.run(cmd_compile, capture_output=True, text=True, cwd=VERILOG_SRC)
    if result.returncode != 0:
        print(f"  Compile FAILED: {result.stderr}")
        return None
    
    # Run
    cmd_run = [VVP_PATH, "tb_top.vvp"]
    result = subprocess.run(cmd_run, capture_output=True, text=True, cwd=VERILOG_SRC)
    if result.returncode != 0:
        print(f"  Simulation FAILED: {result.stderr}")
        return None
    
    # Parse output for "Verilog Prediction: Digit X"
    for line in result.stdout.split('\n'):
        if "Verilog Prediction: Digit" in line:
            try:
                digit = int(line.split("Digit")[-1].strip())
                return digit
            except:
                pass
    return None

def golden_predict(model, image):
    """Get PyTorch golden model prediction for an image."""
    model.eval()
    with torch.no_grad():
        logits = model(image.unsqueeze(0))
        pred = torch.argmax(logits, dim=1).item()
    return pred

def main():
    print(f"\n{'='*60}")
    print(f"M15: PC-Only Batch Regression Harness (N={N_IMAGES})")
    print(f"{'='*60}\n")
    
    # Load model (cached or train once)
    model = load_or_train_model()
    model.eval()
    
    # Load Q7.8 weights for golden model
    w1, w2, w3 = load_q7_8_weights()
    
    # Get test images
    X_test, y_test = get_test_images()
    
    hw_vs_golden_pass = 0
    hw_vs_golden_fail = 0
    golden_vs_true_mismatch = 0
    
    results = []
    
    for idx in range(N_IMAGES):
        img = X_test[idx]
        true_label = y_test[idx].item()
        
        # 1. Golden model prediction (Q7.8 fixed-point, matches hardware)
        golden_pred = golden_predict_q7_8(img, w1, w2, w3)
        
        # 2. Export input as Q7.8 hex
        write_input_hex(img, os.path.join(VERILOG_SRC, "e2e_input.hex"))
        
        # 3. Run Verilog simulation
        hw_pred = run_verilog_sim()
        
        if hw_pred is None:
            hw_vs_golden_fail += 1
            results.append({
                'idx': idx, 'true': true_label, 'golden': golden_pred,
                'hw': 'ERROR', 'match': False
            })
            print(f"Image {idx:2d}: True={true_label}, Golden={golden_pred}, HW=ERROR -> FAIL")
            continue
        
        # 4. Compare
        match = (hw_pred == golden_pred)
        if match:
            hw_vs_golden_pass += 1
        else:
            hw_vs_golden_fail += 1
        
        if golden_pred != true_label:
            golden_vs_true_mismatch += 1
        
        results.append({
            'idx': idx, 'true': true_label, 'golden': golden_pred,
            'hw': hw_pred, 'match': match
        })
        
        status = "PASS" if match else "FAIL"
        true_match = "OK" if golden_pred == true_label else "XX"
        print(f"Image {idx:2d}: True={true_label} ({true_match}), Golden={golden_pred}, HW={hw_pred} -> {status}")
    
    # Summary
    total = hw_vs_golden_pass + hw_vs_golden_fail
    agreement_rate = (hw_vs_golden_pass / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Hardware vs Golden Agreement: {hw_vs_golden_pass}/{total} = {agreement_rate:.1f}%")
    print(f"Golden vs True Label Mismatches: {golden_vs_true_mismatch}/{total} (training limitation)")
    print(f"{'='*60}")
    
    if agreement_rate < 100.0:
        print("\nFAILURES:")
        for r in results:
            if not r['match']:
                print(f"  Image {r['idx']}: True={r['true']}, Golden={r['golden']}, HW={r['hw']}")
        sys.exit(1)
    else:
        print("\nAll images PASSED hardware vs golden agreement check.")
        sys.exit(0)

if __name__ == "__main__":
    main()