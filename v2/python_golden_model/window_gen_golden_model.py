import sys

def generate_windows(image_20x20):
    """
    Given a 20x20 image, generates 400 3x3 windows with padding=1, stride=1.
    Output is in row-major tap order.
    """
    assert len(image_20x20) == 20
    assert all(len(row) == 20 for row in image_20x20)
    
    windows = []
    
    # We are iterating over the 20x20 output grid.
    # Output (r, c) corresponds to center of the 3x3 window in the padded image.
    for r in range(20):
        for c in range(20):
            window = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    in_r = r + dr
                    in_c = c + dc
                    
                    if 0 <= in_r < 20 and 0 <= in_c < 20:
                        window.append(image_20x20[in_r][in_c])
                    else:
                        window.append(0) # Padding
            windows.append(window)
            
    return windows

if __name__ == "__main__":
    # Create a small 20x20 test pattern where each pixel has a distinct, recognizable value.
    # value = row * 20 + col + 1 (so from 1 to 400)
    test_image = []
    for r in range(20):
        row = []
        for c in range(20):
            row.append(r * 20 + c + 1)
        test_image.append(row)
        
    windows = generate_windows(test_image)
    
    print("=== Python Golden Model: Window Generator ===")
    print(f"Total windows generated: {len(windows)}")
    
    print("\n[Spot Check] Top-Left Corner (r=0, c=0):")
    print(f"Expected 2 padding sides (top, left): {windows[0]}")
    
    print("\n[Spot Check] Top-Edge Non-Corner (r=0, c=1):")
    print(f"Expected 1 padding side (top): {windows[1]}")
    
    print("\n[Spot Check] Fully Interior (r=1, c=1):")
    print(f"Expected 0 padding: {windows[21]}")

    # Write all 400 windows to a text file for the Verilog testbench to verify against
    with open("expected_windows.txt", "w") as f:
        for w in windows:
            # Write 9 values separated by space as hex strings
            # Handle signed values safely (though in this test, all pixels are >= 0)
            f.write(" ".join(f"{(val & 0xFFFF):04X}" for val in w) + "\n")
    print("\nWrote all 400 windows to expected_windows.txt")
