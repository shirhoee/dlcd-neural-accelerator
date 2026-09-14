import sys
sys.path.append('python_golden_model')

from fixed_point_math import relu_q7_8

def main():
    # Read Layer 2's pre-ReLU outputs from M5
    with open('verilog_src/layer2_expected_outs.hex', 'r') as f:
        pre_relu = [int(line.strip(), 16) for line in f]

    print(f"Read {len(pre_relu)} pre-ReLU values from Layer 2")

    # Apply ReLU
    post_relu = [relu_q7_8(val) for val in pre_relu]

    # Export
    with open('verilog_src/relu_l2_expected_outs.hex', 'w') as f:
        for val in post_relu:
            f.write(f'{val:04x}\n')

    print("Generated relu_l2_expected_outs.hex")
    print("\nPost-ReLU values (6 neurons):")
    for i, (pre, post) in enumerate(zip(pre_relu, post_relu)):
        print(f"  Neuron {i:2d}: pre={pre:04x} -> post={post:04x}")

if __name__ == '__main__':
    main()