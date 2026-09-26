import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageDraw
import os

CANVAS_SIZE = 400
STROKE_WIDTH = 24

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

def get_model():
    model = VerilogNet()
    w1_flat = np.array([int(line.strip(), 16) for line in open("verilog_src/e2e_w1.hex")])
    w2_flat = np.array([int(line.strip(), 16) for line in open("verilog_src/e2e_w2.hex")])
    w3_flat = np.array([int(line.strip(), 16) for line in open("verilog_src/e2e_w3.hex")])
    def to_signed(v): return v - 65536 if (v & 0x8000) else v
    w1 = np.array([to_signed(v) for v in w1_flat]).reshape(16, 100).astype(np.float32) / 256.0
    w2 = np.array([to_signed(v) for v in w2_flat]).reshape(6, 16).astype(np.float32) / 256.0
    w3 = np.array([to_signed(v) for v in w3_flat]).reshape(10, 6).astype(np.float32) / 256.0
    with torch.no_grad():
        model.fc1.weight.copy_(torch.from_numpy(w1))
        model.fc2.weight.copy_(torch.from_numpy(w2))
        model.fc3.weight.copy_(torch.from_numpy(w3))
    model.eval()
    return model

def draw_digit(digit):
    img = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d = ImageDraw.Draw(img)
    w = STROKE_WIDTH
    
    if digit == 0:
        d.ellipse([100, 50, 300, 350], outline='black', width=w)
    elif digit == 1:
        d.line([200, 50, 200, 350], fill='black', width=w)
    elif digit == 2:
        d.arc([100, 50, 300, 200], start=180, end=0, fill='black', width=w)
        d.line([300, 125, 100, 350], fill='black', width=w)
        d.line([100, 350, 300, 350], fill='black', width=w)
    elif digit == 3:
        d.arc([100, 50, 300, 200], start=270, end=90, fill='black', width=w)
        d.arc([100, 200, 300, 350], start=270, end=90, fill='black', width=w)
    elif digit == 4:
        d.line([300, 250, 100, 250], fill='black', width=w)
        d.line([100, 250, 250, 50], fill='black', width=w)
        d.line([250, 50, 250, 350], fill='black', width=w)
    elif digit == 5:
        d.line([300, 50, 100, 50], fill='black', width=w)
        d.line([100, 50, 100, 200], fill='black', width=w)
        d.arc([100, 150, 300, 350], start=270, end=135, fill='black', width=w)
    elif digit == 6:
        d.arc([100, 50, 300, 350], start=90, end=270, fill='black', width=w)
        d.ellipse([100, 200, 300, 350], outline='black', width=w)
    elif digit == 7:
        d.line([100, 50, 300, 50], fill='black', width=w)
        d.line([300, 50, 150, 350], fill='black', width=w)
    elif digit == 8:
        d.ellipse([120, 50, 280, 200], outline='black', width=w)
        d.ellipse([100, 200, 300, 350], outline='black', width=w)
    elif digit == 9:
        d.ellipse([100, 50, 300, 200], outline='black', width=w)
        d.line([300, 125, 300, 350], fill='black', width=w)
    return img

def preprocess(pil_img, use_erosion):
    gray = np.array(pil_img.convert('L'), dtype=np.float32)
    gray = 255.0 - gray
    rows = np.any(gray > 10, axis=1)
    cols = np.any(gray > 10, axis=0)
    if not np.any(rows) or not np.any(cols): return np.zeros((10, 10))
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    if use_erosion:
        import scipy.ndimage as ndimage
        gray = ndimage.binary_erosion(gray > 10, iterations=10).astype(np.float32) * 255.0
        gray = ndimage.gaussian_filter(gray, sigma=1.0)
        
    h = rmax - rmin + 1
    w = cmax - cmin + 1
    size = max(h, w)
    r_center = (rmin + rmax) // 2
    c_center = (cmin + cmax) // 2
    half = size // 2
    rmin_sq = max(0, r_center - half)
    rmax_sq = min(gray.shape[0] - 1, r_center + half)
    cmin_sq = max(0, c_center - half)
    cmax_sq = min(gray.shape[1] - 1, c_center + half)
    if rmax_sq - rmin_sq + 1 < size:
        if rmin_sq == 0: rmax_sq = min(gray.shape[0] - 1, rmin_sq + size - 1)
        elif rmax_sq == gray.shape[0] - 1: rmin_sq = max(0, rmax_sq - size + 1)
    if cmax_sq - cmin_sq + 1 < size:
        if cmin_sq == 0: cmax_sq = min(gray.shape[1] - 1, cmin_sq + size - 1)
        elif cmax_sq == gray.shape[1] - 1: cmin_sq = max(0, cmax_sq - size + 1)
        
    cropped = gray[rmin_sq:rmax_sq+1, cmin_sq:cmax_sq+1]
    
    h, w = cropped.shape
    out_h, out_w = 8, 8
    resized = np.zeros((out_h, out_w), dtype=np.float32)
    for i in range(out_h):
        for j in range(out_w):
            r_start = int(i * h / out_h)
            r_end = int((i + 1) * h / out_h)
            c_start = int(j * w / out_w)
            c_end = int((j + 1) * w / out_w)
            block = cropped[r_start:r_end, c_start:c_end]
            if block.size > 0:
                resized[i, j] = block.mean()
                
    padded = np.pad(resized, ((1, 1), (1, 1)), mode='constant', constant_values=0)
    return padded / 255.0

def run_tests():
    model = get_model()
    
    for state, use_erosion in [("WITHOUT EROSION (Commented Out)", False), ("WITH EROSION (Fix A Active)", True)]:
        print(f"\n--- TESTING {state} ---")
        correct = 0
        for digit in range(10):
            img = draw_digit(digit)
            proc_img = preprocess(img, use_erosion)
            
            inp = torch.tensor(proc_img.flatten(), dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                logits = model(inp)
                pred = torch.argmax(logits, dim=1).item()
                max_logit = logits.abs().max().item()
                
            match = "PASS" if pred == digit else "FAIL"
            print(f"Digit {digit}: Predicted {pred} {match} (Max logit: {max_logit:.2f})")
            if pred == digit: correct += 1
            
        print(f"Total Accuracy {state}: {correct}/10 ({correct*10}%)")

if __name__ == "__main__":
    run_tests()
