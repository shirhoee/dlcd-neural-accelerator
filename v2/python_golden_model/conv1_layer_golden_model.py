import sys
from fixed_point_math import to_q7_8, from_q7_8, mul_q7_8, add_q7_8

def conv2d_q7_8(image_20x20, weights_4x9):
    """
    Simulates Conv1: 1 input channel -> 4 output channels, 3x3 kernel, stride 1, padding 1.
    image_20x20: 2D list (20x20) of floats.
    weights_4x9: 2D list (4x9) of floats. Each row is a channel's 9 weights in tap order.
    Returns: 4x20x20 tensor in Q7.8 (integer format).
    """
    assert len(image_20x20) == 20
    assert len(weights_4x9) == 4
    for w in weights_4x9:
        assert len(w) == 9

    # Convert weights to Q7.8
    weights_q = [[to_q7_8(val) for val in chan] for chan in weights_4x9]
    
    # Pre-convert image to Q7.8
    image_q = [[to_q7_8(val) for val in row] for row in image_20x20]

    out_4x20x20 = []
    
    for ch in range(4):
        out_channel = []
        for r in range(20):
            out_row = []
            for c in range(20):
                acc_q7_8 = 0
                tap_idx = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        in_r = r + dr
                        in_c = c + dc
                        
                        # Apply Padding
                        if 0 <= in_r < 20 and 0 <= in_c < 20:
                            pixel_q = image_q[in_r][in_c]
                        else:
                            pixel_q = 0
                            
                        # MAC operation (matches N1)
                        prod = mul_q7_8(pixel_q, weights_q[ch][tap_idx])
                        acc_q7_8 = add_q7_8(acc_q7_8, prod)
                        
                        tap_idx += 1
                        
                out_row.append(acc_q7_8)
            out_channel.append(out_row)
        out_4x20x20.append(out_channel)
        
    return out_4x20x20

if __name__ == "__main__":
    # Generate test image: value = (r*20 + c + 1) * 0.001
    test_image = []
    for r in range(20):
        row = []
        for c in range(20):
            row.append((r * 20 + c + 1) * 0.001)
        test_image.append(row)
        
    # Generate test weights
    # Ch0: all 0.1
    # Ch1: all -0.1
    # Ch2: 0.1 to 0.9
    # Ch3: -0.1 to -0.9
    weights = [
        [0.1] * 9,
        [-0.1] * 9,
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]
    ]

    out = conv2d_q7_8(test_image, weights)
    
    # Write image to hex file for testbench
    with open("test_image_q7_8.txt", "w") as f:
        image_q = [[to_q7_8(val) for val in row] for row in test_image]
        for row in image_q:
            for val in row:
                f.write(f"{(val & 0xFFFF):04X}\n")

    # Dump weights
    with open("weights_q7_8.txt", "w") as f:
        weights_q = [[to_q7_8(val) for val in chan] for chan in weights]
        for chan in weights_q:
            for val in chan:
                f.write(f"{(val & 0xFFFF):04X}\n")

    # Write to hex file for testbench
    with open("expected_conv1_out.txt", "w") as f:
        # Output order: For each of the 400 window positions, write 4 values (Ch0, Ch1, Ch2, Ch3)
        # This matches the parallel streaming output format
        for r in range(20):
            for c in range(20):
                vals = [out[ch][r][c] for ch in range(4)]
                f.write(" ".join(f"{(val & 0xFFFF):04X}" for val in vals) + "\n")
                
    print("Generated 1600 output values to expected_conv1_out.txt")
