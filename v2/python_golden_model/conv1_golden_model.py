import sys
import os

# Import fixed_point_math locally
from fixed_point_math import to_q7_8, from_q7_8, mul_q7_8, add_q7_8

def conv_pe_mac_sequence(pixels_float, weights_float):
    """
    Simulates a 9-tap sequential MAC for a single output pixel in Q7.8.
    Input lists must be 9 elements long.
    """
    assert len(pixels_float) == 9
    assert len(weights_float) == 9
    
    acc_q7_8 = 0
    
    print(f"{'Tap':<4} | {'Pix(F)':<8} | {'Pix(Q)':<8} | {'Wt(F)':<8} | {'Wt(Q)':<8} | {'MAC(Q)':<8} | {'Acc(Q)':<8}")
    print("-" * 70)
    
    for i in range(9):
        p_q = to_q7_8(pixels_float[i])
        w_q = to_q7_8(weights_float[i])
        
        # MAC
        prod = mul_q7_8(p_q, w_q)
        acc_q7_8 = add_q7_8(acc_q7_8, prod)
        
        print(f"{i:<4} | {pixels_float[i]:<8.4f} | {p_q:<8} | {weights_float[i]:<8.4f} | {w_q:<8} | {prod:<8} | {acc_q7_8:<8}")
        
    print("-" * 70)
    print(f"Final Accumulator (Q7.8): {acc_q7_8}")
    print(f"Final Accumulator (Float): {from_q7_8(acc_q7_8):.4f}\n")
    return acc_q7_8

if __name__ == "__main__":
    # 9 weights for a 3x3 kernel
    # Example weights: [-0.5, 0.1, 0.8, -0.2, 0.9, -0.1, 0.3, 0.4, -0.7]
    weights = [-0.5, 0.1, 0.8, -0.2, 0.9, -0.1, 0.3, 0.4, -0.7]
    
    print("=== TEST CASE 1: Interior Window (No Padding) ===")
    # 9 interior pixels
    pixels_interior = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    conv_pe_mac_sequence(pixels_interior, weights)
    
    print("=== TEST CASE 2: Edge Window (Top-Left Padding) ===")
    # Padding on top row and left column (taps 0, 1, 2, 3, 6 are padded? Wait)
    # If 3x3 window is at top-left corner of the image, the padded elements are:
    # row 0: all padded (taps 0, 1, 2 = 0)
    # row 1: left element padded (tap 3 = 0, tap 4, 5 are image)
    # row 2: left element padded (tap 6 = 0, tap 7, 8 are image)
    pixels_edge = [0.0, 0.0, 0.0, 0.0, 0.5, 0.6, 0.0, 0.8, 0.9]
    conv_pe_mac_sequence(pixels_edge, weights)
