import sys
sys.path.append('python_golden_model')

import random
from fixed_point_math import to_q4_12, mul_q4_12, add_q4_12

def main():
    random.seed(42)
    ROWS = 10
    COLS = 6

    # Read Layer 2's post-ReLU output as this layer's input (6 values)
    with open('verilog_src/relu_l2_expected_outs.hex', 'r') as f:
        input_vector = [int(line.strip(), 16) for line in f]

    print(f"Read {len(input_vector)} input values from L2 ReLU output")

    # Generate weight matrix (10x6, row-major)
    weight_matrix = []
    for _ in range(ROWS):
        row = []
        for _ in range(COLS):
            val = random.uniform(-8.0, 8.0 - (1/4096))
            row.append(to_q4_12(val))
        weight_matrix.append(row)

    # Compute expected outputs (10 neurons) using sequential MAC with truncation
    expected_outputs = []
    for r in range(ROWS):
        acc = 0
        for c in range(COLS):
            product = mul_q4_12(weight_matrix[r][c], input_vector[c])
            acc = add_q4_12(acc, product)
        expected_outputs.append(acc)

    # Export weights (row-major: 10 rows x 6 cols = 60 values)
    with open('verilog_src/layer3_weights.hex', 'w') as f:
        for r in range(ROWS):
            for c in range(COLS):
                f.write(f'{weight_matrix[r][c]:04x}\n')

    # Export input vector (copy of L2 ReLU output for traceability)
    with open('verilog_src/layer3_input.hex', 'w') as f:
        for val in input_vector:
            f.write(f'{val:04x}\n')

    # Export expected outputs (10 values)
    with open('verilog_src/layer3_expected_outs.hex', 'w') as f:
        for val in expected_outputs:
            f.write(f'{val:04x}\n')

    print("Generated Layer 3 test vectors:")
    print(f"  verilog_src/layer3_weights.hex (60 values)")
    print(f"  verilog_src/layer3_input.hex (6 values)")
    print(f"  verilog_src/layer3_expected_outs.hex (10 values)")
    print("\nExpected outputs (10 neurons):")
    for i, val in enumerate(expected_outputs):
        print(f"  Neuron {i:2d}: {val:04x} ({val})")

if __name__ == '__main__':
    main()