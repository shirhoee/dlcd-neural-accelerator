import os
import torch
import math

def load_q7_8_txt(filename, rows, cols):
    with open(filename, 'r') as f:
        lines = f.read().split()
    matrix = torch.zeros((rows, cols), dtype=torch.int32)
    idx = 0
    for r in range(rows):
        for c in range(cols):
            val = int(lines[idx], 16)
            # Sign extend 16-bit to python int
            if val >= 32768:
                val -= 65536
            matrix[r, c] = val
            idx += 1
    return matrix

def pad_matrix(matrix, target_rows, target_cols):
    rows, cols = matrix.shape
    padded = torch.zeros((target_rows, target_cols), dtype=torch.int32)
    padded[:rows, :cols] = matrix
    return padded

def export_tiles(matrix, name, out_file):
    rows, cols = matrix.shape
    assert rows % 16 == 0 and cols % 16 == 0
    row_chunks = rows // 16
    col_chunks = cols // 16
    
    total_tiles = 0
    for r_idx in range(row_chunks):
        for c_idx in range(col_chunks):
            tile = matrix[r_idx*16:(r_idx+1)*16, c_idx*16:(c_idx+1)*16]
            # Write columns from 15 down to 0
            for c in range(15, -1, -1):
                word = 0
                for r in range(16):
                    val = int(tile[r, c].item())
                    # convert to 16-bit unsigned hex representation
                    val = val & 0xFFFF
                    word |= (val << (r * 16))
                # Write as 64-character hex string (256 bits)
                out_file.write(f"{word:064x}\n")
            total_tiles += 1
    print(f"Exported {total_tiles} tiles for {name}")

def main():
    w1 = load_q7_8_txt("dense1_q7_8.txt", 64, 200)
    w2 = load_q7_8_txt("dense2_q7_8.txt", 32, 64)
    w3 = load_q7_8_txt("dense3_q7_8.txt", 10, 32)
    
    w1_padded = pad_matrix(w1, 64, 208)
    w2_padded = pad_matrix(w2, 32, 64)
    w3_padded = pad_matrix(w3, 16, 32)
    
    with open("mlp_rom.txt", "w") as f:
        export_tiles(w1_padded, "Layer 1", f)
        export_tiles(w2_padded, "Layer 2", f)
        export_tiles(w3_padded, "Layer 3", f)

if __name__ == "__main__":
    main()
