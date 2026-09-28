import sys

def generate_pool_windows():
    # 20x20 image, values 0 to 399
    image = []
    val = 0
    for r in range(20):
        row = []
        for c in range(20):
            row.append(val)
            val += 1
        image.append(row)
        
    windows = []
    # Stride 2, 2x2 window
    # r and c iterate over the top-left corners of the windows
    for r in range(0, 20, 2):
        for c in range(0, 20, 2):
            w = [
                image[r][c],       # Top-left
                image[r][c+1],     # Top-right
                image[r+1][c],     # Bottom-left
                image[r+1][c+1]    # Bottom-right
            ]
            windows.append(w)
            
    with open("expected_pool_windows.hex", "w") as f:
        for w in windows:
            f.write(" ".join(f"{val:04X}" for val in w) + "\n")
            
    print(f"Generated {len(windows)} windows to expected_pool_windows.hex")

if __name__ == "__main__":
    generate_pool_windows()
