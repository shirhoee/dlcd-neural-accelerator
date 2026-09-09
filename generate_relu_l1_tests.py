import sys
sys.path.append('python_golden_model')

from fixed_point_math import relu_q4_12

def main():
    # Read pre-ReLU outputs from M3
    with open('verilog_src/array_expected_outs.hex', 'r') as f:
        pre_relu = [int(line.strip(), 16) for line in f]

    print(f"Read {len(pre_relu)} pre-ReLU values")

    # Apply ReLU
    post_relu = [relu_q4_12(val) for val in pre_relu]

    # Export
    with open('verilog_src/relu_l1_expected_outs.hex', 'w') as f:
        for val in post_relu:
            f.write(f'{val:04x}\n')

    print("Generated relu_l1_expected_outs.hex")
    print("\nPost-ReLU values (16 neurons):")
    for i, (pre, post) in enumerate(zip(pre_relu, post_relu)):
        print(f"  Neuron {i:2d}: pre={pre:04x} -> post={post:04x}")

if __name__ == '__main__':
    main()