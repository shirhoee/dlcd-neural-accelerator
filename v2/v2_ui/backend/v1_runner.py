import os
from typing import List, Tuple
import numpy as np

# Path to V1 weights
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
V1_WEIGHTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../v1/verilog_src"))

def to_signed_16(val: int) -> int:
    return val if val < 32768 else val - 65536

def mul_q7_8(a: int, b: int) -> int:
    prod = a * b
    trunc = (prod >> 8) & 0xFFFF
    return to_signed_16(trunc)

def add_q7_8(a: int, b: int) -> int:
    sum_val = (a + b) & 0xFFFF
    return to_signed_16(sum_val)

def relu_q7_8(x: int) -> int:
    return x if x > 0 else 0

def load_hex_weights(path: str) -> List[int]:
    with open(path, "r") as f:
        return [to_signed_16(int(line.strip(), 16)) for line in f if line.strip()]

class V1Emulator:
    def __init__(self):
        w1_path = os.path.join(V1_WEIGHTS_DIR, "e2e_w1.hex")
        w2_path = os.path.join(V1_WEIGHTS_DIR, "e2e_w2.hex")
        w3_path = os.path.join(V1_WEIGHTS_DIR, "e2e_w3.hex")
        
        self.w1 = load_hex_weights(w1_path) # 16 x 100
        self.w2 = load_hex_weights(w2_path) # 6 x 16
        self.w3 = load_hex_weights(w3_path) # 10 x 6

    def downsample_28_to_10(self, grid_28: List[List[float]]) -> List[List[float]]:
        """Downsample 28x28 normalized canvas to 10x10 using block averaging."""
        grid_np = np.array(grid_28, dtype=np.float32)
        # 10x10 grid with block averaging
        out_10 = np.zeros((10, 10), dtype=np.float32)
        for r in range(10):
            for c in range(10):
                # Map 10x10 to 28x28 coordinates
                r_start = int(r * 2.8)
                r_end = min(28, int((r + 1) * 2.8))
                c_start = int(c * 2.8)
                c_end = min(28, int((c + 1) * 2.8))
                block = grid_np[r_start:r_end, c_start:c_end]
                out_10[r, c] = float(np.mean(block)) if block.size > 0 else 0.0
        return out_10.tolist()

    def forward(self, grid_10: List[List[float]]) -> Tuple[int, List[float], List[float], List[float]]:
        """
        Runs bit-exact Q7.8 forward pass for V1:
        Input: 10x10 floats in [0, 1]
        Returns: (prediction, logits, layer1_activations, layer2_activations)
        """
        # Quantize to Q7.8 (multiply by 256)
        in_flat = [int(round(val * 256.0)) for row in grid_10 for val in row]
        
        # Layer 1: 100 -> 16
        l1_out = []
        for i in range(16):
            acc = 0
            for j in range(100):
                w = self.w1[i * 100 + j]
                x = in_flat[j]
                acc = add_q7_8(acc, mul_q7_8(w, x))
            l1_out.append(relu_q7_8(acc))
            
        # Layer 2: 16 -> 6
        l2_out = []
        for i in range(6):
            acc = 0
            for j in range(16):
                w = self.w2[i * 16 + j]
                x = l1_out[j]
                acc = add_q7_8(acc, mul_q7_8(w, x))
            l2_out.append(relu_q7_8(acc))
            
        # Layer 3: 6 -> 10 (Logits)
        logits = []
        for i in range(10):
            acc = 0
            for j in range(6):
                w = self.w3[i * 6 + j]
                x = l2_out[j]
                acc = add_q7_8(acc, mul_q7_8(w, x))
            logits.append(float(acc))
            
        # Argmax
        pred = int(np.argmax(logits))
        
        # Return scaled values for UI
        l1_floats = [v / 256.0 for v in l1_out]
        l2_floats = [v / 256.0 for v in l2_out]
        logits_floats = [v / 256.0 for v in logits]
        
        return pred, logits_floats, l1_floats, l2_floats

# Singleton instance
_v1_instance = None
def get_v1_emulator() -> V1Emulator:
    global _v1_instance
    if _v1_instance is None:
        _v1_instance = V1Emulator()
    return _v1_instance
