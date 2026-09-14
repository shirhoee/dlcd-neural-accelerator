import sys
sys.path.append('python_golden_model')

import random
from fixed_point_math import to_q7_8, mul_q7_8, add_q7_8

def main():
    random.seed(42)
    ROWS = 16
    COLS = 100

    # Generate input vector (100 elements)
    input_vector = []
    for _ in range(COLS):
        val = random.uniform(-8.0, 8.0 - (1/256))
        input_vector.append(to_q7_8(val))

    # Generate weight matrix (16x100, row-major)
    weight_matrix = []
    for _ in range(ROWS):
        row = []
        for _ in range(COLS):
            val = random.uniform(-8.0, 8.0 - (1/256))
            row.append(to_q7_8(val))
        weight_matrix.append(row)

    # Compute expected outputs (16 neurons) using sequential MAC with truncation at each step
    expected_outputs = []
    for r in range(ROWS):
        acc = 0  # Start with zero accumulator
        for c in range(COLS):
            product = mul_q7_8(weight_matrix[r][c], input_vector[c])
            acc = add_q7_8(acc, product)
        expected_outputs.append(acc)

    # Export weights (row-major: 16 rows x 100 cols = 1600 values)
    with open('verilog_src/array_weights.hex', 'w') as f:
        for r in range(ROWS):
            for c in range(COLS):
                f.write(f'{weight_matrix[r][c]:04x}\n')

    # Export input vector
    with open('verilog_src/array_input.hex', 'w') as f:
        for val in input_vector:
            f.write(f'{val:04x}\n')

    # Export expected outputs (16 values)
    with open('verilog_src/array_expected_outs.hex', 'w') as f:
        for val in expected_outputs:
            f.write(f'{val:04x}\n')

    print("Generated array test vectors:")
    print(f"  verilog_src/array_weights.hex (1600 values)")
    print(f"  verilog_src/array_input.hex (100 values)")
    print(f"  verilog_src/array_expected_outs.hex (16 values)")
    print("\nExpected outputs (16 neurons):")
    for i, val in enumerate(expected_outputs):
        print(f"  Neuron {i:2d}: {val:04x} ({val})")

if __name__ == '__main__':
    main()