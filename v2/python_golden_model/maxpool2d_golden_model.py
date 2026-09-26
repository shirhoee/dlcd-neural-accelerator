import sys

# Import fixed_point_math locally
from fixed_point_math import to_q7_8, from_q7_8

def maxpool_2x2_q7_8(window_float):
    """
    Simulates 2x2 max pooling in Q7.8.
    window_float: list of 4 float values [in0, in1, in2, in3]
    """
    assert len(window_float) == 4
    
    # Convert all inputs to Q7.8 (Signed 16-bit integers)
    q7_8_vals = [to_q7_8(val) for val in window_float]
    
    # IMPORTANT: The Q7.8 values returned by to_q7_8 are 16-bit integers natively 
    # handled by Python as arbitrary precision signed integers. 
    # However, to explicitly model standard Verilog 2's complement comparisons:
    # A signed comparison in Verilog evaluates the MSB as the sign bit.
    # We must treat the 16-bit integer as a signed 2's complement number.
    # Python's `to_q7_8` already handles `if i & (1 << 15): i -= 65536` logic inside 
    # conversions, so the integer values we get from `to_q7_8` might be standard Python 
    # integers (Wait, `to_q7_8` in fixed_point_math actually returns the bitwise representation
    # using `& MASK` which means it returns an UNSIGNED 16-bit value from 0 to 65535!).
    # Let's fix that for the golden model comparison.
    
    def sign_extend_16(val):
        if val & 0x8000:
            return val - 0x10000
        return val

    # Sign extend them so Python uses true signed comparison
    signed_vals = [sign_extend_16(val) for val in q7_8_vals]
    
    # Find max
    max_val = max(signed_vals)
    
    # Convert back to bit representation (0 to 65535) for Q7.8 output
    max_q7_8 = max_val & 0xFFFF
    
    print(f"Inputs (F): {window_float}")
    print(f"Inputs (Q): {q7_8_vals}")
    print(f"Inputs (S): {signed_vals}")
    print(f"Max (S): {max_val} -> Max (Q): {max_q7_8}")
    print(f"Max (F): {from_q7_8(max_q7_8):.4f}\n")
    
    return max_q7_8

if __name__ == "__main__":
    print("=== TEST CASE 1: All Positive ===")
    maxpool_2x2_q7_8([0.1, 0.5, 0.2, 0.9])
    
    print("=== TEST CASE 2: All Negative ===")
    # Crucial test: naive unsigned max of Q7.8 would incorrectly treat -0.1 (0xFF..) as larger than positive numbers.
    # Wait, -0.1 is 65510, -0.9 is 65305. 
    # Naive unsigned max would pick 65510 (-0.1). Wait, that IS the max!
    # Let's pick -0.5, -0.1, -0.9, -0.2. Max is -0.1.
    # If unsigned, 65510 (-0.1) is max.
    # Wait, what if it's mixed? Mixed is where unsigned fails!
    # Let's just have an all negative test case anyway.
    maxpool_2x2_q7_8([-0.5, -0.1, -0.9, -0.2])
    
    print("=== TEST CASE 3: Mixed Positive/Negative ===")
    # Positive: 0.1 (26). Negative: -0.9 (65305).
    # Unsigned max would pick -0.9 (65305).
    # Signed max should pick 0.1 (26).
    maxpool_2x2_q7_8([-0.9, 0.1, -0.5, 0.05])
    
    print("=== TEST CASE 4: Tie ===")
    maxpool_2x2_q7_8([0.4, 0.4, 0.1, -0.5])
