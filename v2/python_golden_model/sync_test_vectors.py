import os
import sys
import numpy as np

# Add local path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fixed_point_math import to_signed_16, mul_q7_8, add_q7_8, relu_q7_8, MASK
from int_emulator_v2 import IntEmulatorV2, load_hex

def sync_vectors():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    conv1_w_path = os.path.join(base_dir, "weights_q7_8.txt")
    conv2_w_path = os.path.join(base_dir, "conv2_weights_q7_8.txt")
    img_path = os.path.join(base_dir, "test_image_q7_8.txt")
    
    dense1_path = os.path.join(base_dir, "dense1_q7_8.txt")
    dense2_path = os.path.join(base_dir, "dense2_q7_8.txt")
    dense3_path = os.path.join(base_dir, "dense3_q7_8.txt")
    dense_old_path = os.path.join(base_dir, "dense_weights_q7_8.txt")

    img_q = load_hex(img_path)
    emu = IntEmulatorV2(
        conv1_w_path, conv2_w_path,
        dense1_hex=dense1_path, dense2_hex=dense2_path, dense3_hex=dense3_path,
        head_type="200->64->32->10"
    )

    img = np.array(img_q).reshape(1, 20, 20)
    
    # 1. Conv1 (4 channels, 20x20)
    c1 = emu.conv2d_q7_8(img, emu.conv1_w, 1, 4, 20, 20)
    conv1_out_path = os.path.join(base_dir, "expected_conv1_out.txt")
    with open(conv1_out_path, "w") as f:
        for r in range(20):
            for c in range(20):
                line = [f"{(c1[ch, r, c] & MASK):04x}" for ch in range(4)]
                f.write(" ".join(line) + "\n")
    print(f"Wrote {conv1_out_path}")

    # 2. MaxPool1 + ReLU (4 channels, 10x10)
    p1 = emu.maxpool2d(c1)
    r1 = emu.relu_map(p1)
    maxpool_out_path = os.path.join(base_dir, "expected_maxpool_out.txt")
    with open(maxpool_out_path, "w") as f:
        for r in range(10):
            for c in range(10):
                line = [f"{(r1[ch, r, c] & MASK):04x}" for ch in range(4)]
                f.write(" ".join(line) + "\n")
    print(f"Wrote {maxpool_out_path}")

    # 3. Conv2 (8 channels, 10x10)
    c2 = emu.conv2d_q7_8(r1, emu.conv2_w, 4, 8, 10, 10)
    conv2_out_path = os.path.join(base_dir, "expected_conv2_out.txt")
    with open(conv2_out_path, "w") as f:
        for r in range(10):
            for c in range(10):
                line = [f"{(c2[ch, r, c] & MASK):04x}" for ch in range(8)]
                f.write(" ".join(line) + "\n")
    print(f"Wrote {conv2_out_path}")

    # 4. MaxPool2 + ReLU (8 channels, 5x5)
    p2 = emu.maxpool2d(c2)
    r2 = emu.relu_map(p2)
    
    # 25 lines of 8 channels for tb_maxpool2_array.v / tb_dense_array.v
    maxpool2_out_path = os.path.join(base_dir, "expected_maxpool2_out.txt")
    with open(maxpool2_out_path, "w") as f:
        for r in range(5):
            for c in range(5):
                line = [f"{(r2[ch, r, c] & MASK):04x}" for ch in range(8)]
                f.write(" ".join(line) + "\n")
    print(f"Wrote {maxpool2_out_path}")

    # 5. Flat features for dense (200)
    flat = r2.transpose(1, 2, 0).flatten()
    dense_in_path = os.path.join(base_dir, "expected_mp2_relu_flat.txt")
    with open(dense_in_path, "w") as f:
        for val in flat:
            f.write(f"{(val & MASK):04x}\n")
    print(f"Wrote {dense_in_path}")

    # 6. Legacy 200->10 dense output for tb_dense_array.v (if dense_weights_q7_8 exists)
    if os.path.exists(dense_old_path):
        old_dense_w = load_hex(dense_old_path)
        old_logits = []
        for out_idx in range(10):
            acc = 0
            for in_idx in range(200):
                wt = old_dense_w[out_idx * 200 + in_idx]
                val = flat[in_idx]
                m = mul_q7_8(wt, val)
                acc = add_q7_8(acc, m)
            old_logits.append(acc)
        
        dense_out_path = os.path.join(base_dir, "expected_dense_out.txt")
        with open(dense_out_path, "w") as f:
            f.write(" ".join(f"{(val & MASK):04x}" for val in old_logits) + "\n")
        print(f"Wrote {dense_out_path}")

    # 7. Active 200->64->32->10 dense outputs for tb_mlp_head.v
    d1 = emu.dense_q7_8(flat, emu.dense1_w, 200, 64)
    d1_relu = np.array([relu_q7_8(v) for v in d1])
    d2 = emu.dense_q7_8(d1_relu, emu.dense2_w, 64, 32)
    d2_relu = np.array([relu_q7_8(v) for v in d2])
    logits = emu.dense_q7_8(d2_relu, emu.dense3_w, 32, 10)
    pred, _ = emu.forward(img_q)

    logits_path = os.path.join(base_dir, "expected_logits.txt")
    with open(logits_path, "w") as f:
        for val in logits:
            f.write(f"{(val & MASK):04x}\n")
    print(f"Wrote {logits_path} (Predicted Digit: {pred})")

if __name__ == "__main__":
    sync_vectors()
