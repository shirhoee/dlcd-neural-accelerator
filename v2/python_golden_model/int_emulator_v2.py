import torch
import torch.nn.functional as F
import numpy as np
from fixed_point_math import to_signed_16, mul_q7_8, add_q7_8, relu_q7_8, MASK

def sign_ext(x):
    return to_signed_16(x)

def load_hex(path):
    with open(path, 'r') as f:
        return [int(line.strip(), 16) for line in f if line.strip()]

class IntEmulatorV2:
    def __init__(self, conv1_hex, conv2_hex, dense_hex=None, dense1_hex=None, dense2_hex=None, dense3_hex=None, head_type="200->10"):
        self.conv1_w = load_hex(conv1_hex)
        self.conv2_w = load_hex(conv2_hex)
        self.head_type = head_type
        if head_type == "200->10":
            self.dense_w = load_hex(dense_hex)
        else:
            self.dense1_w = load_hex(dense1_hex)
            self.dense2_w = load_hex(dense2_hex)
            self.dense3_w = load_hex(dense3_hex)
        
    def conv2d_q7_8(self, in_map, weight, in_ch, out_ch, h, w):
        # in_map: [in_ch, h, w]
        # weight: [out_ch, in_ch, 3, 3] flat
        out_map = np.zeros((out_ch, h, w), dtype=int)
        for oc in range(out_ch):
            for i in range(h):
                for j in range(w):
                    acc = 0
                    for ic in range(in_ch):
                        for ky in range(3):
                            for kx in range(3):
                                # Padding=1
                                y = i + ky - 1
                                x = j + kx - 1
                                if 0 <= y < h and 0 <= x < w:
                                    val = in_map[ic, y, x]
                                else:
                                    val = 0
                                w_idx = oc * (in_ch * 9) + ic * 9 + ky * 3 + kx
                                wt = self.conv2_w[w_idx] if in_ch > 1 else self.conv1_w[w_idx]
                                m = mul_q7_8(wt, val)
                                acc = add_q7_8(acc, m)
                    out_map[oc, i, j] = acc
        return out_map

    def relu_map(self, in_map):
        out_map = np.zeros_like(in_map)
        for c in range(in_map.shape[0]):
            for i in range(in_map.shape[1]):
                for j in range(in_map.shape[2]):
                    out_map[c, i, j] = relu_q7_8(in_map[c, i, j])
        return out_map
        
    def maxpool2d(self, in_map):
        out_map = np.zeros((in_map.shape[0], in_map.shape[1]//2, in_map.shape[2]//2), dtype=int)
        for c in range(in_map.shape[0]):
            for i in range(out_map.shape[1]):
                for j in range(out_map.shape[2]):
                    vals = [
                        sign_ext(in_map[c, i*2, j*2]),
                        sign_ext(in_map[c, i*2, j*2+1]),
                        sign_ext(in_map[c, i*2+1, j*2]),
                        sign_ext(in_map[c, i*2+1, j*2+1])
                    ]
                    out_map[c, i, j] = max(vals) & MASK
        return out_map

    def dense_q7_8(self, in_flat, weight, in_features, out_features):
        out = np.zeros(out_features, dtype=int)
        for of in range(out_features):
            acc = 0
            for inf in range(in_features):
                w_idx = of * in_features + inf
                wt = weight[w_idx]
                val = in_flat[inf]
                m = mul_q7_8(wt, val)
                acc = add_q7_8(acc, m)
            out[of] = acc
        return out

    def forward(self, img_q7_8_flat):
        # input: 20x20
        img = np.array(img_q7_8_flat).reshape(1, 20, 20)
        c1 = self.conv2d_q7_8(img, self.conv1_w, 1, 4, 20, 20)
        p1 = self.maxpool2d(c1)
        # N4b: relu applied after pooling
        r1 = self.relu_map(p1)
        
        c2 = self.conv2d_q7_8(r1, self.conv2_w, 4, 8, 10, 10)
        p2 = self.maxpool2d(c2)
        r2 = self.relu_map(p2) # N6: relu after pool2
        
        flat = r2.transpose(1, 2, 0).flatten()
        if self.head_type == "200->10":
            logits = self.dense_q7_8(flat, self.dense_w, 200, 10)
        else:
            # 200 -> 64 -> 32 -> 10
            # Note: PyTorch linear weights were flattened in [out, in] order
            # The dense_q7_8 expects weights such that w_idx = of * in_features + inf
            # This perfectly matches standard flattening of shape [out, in]!
            d1 = self.dense_q7_8(flat, self.dense1_w, 200, 64)
            d1_relu = np.array([relu_q7_8(v) for v in d1])
            d2 = self.dense_q7_8(d1_relu, self.dense2_w, 64, 32)
            d2_relu = np.array([relu_q7_8(v) for v in d2])
            logits = self.dense_q7_8(d2_relu, self.dense3_w, 32, 10)
            
        pred = 0
        max_val = sign_ext(logits[0])
        for i in range(1, 10):
            v = sign_ext(logits[i])
            # Tie breaker: lower index wins (so strictly >)
            if v > max_val:
                max_val = v
                pred = i
        return pred, logits
