import sys
sys.path.append('python_golden_model')

import random
from fixed_point_math import to_q4_12, mul_q4_12

def main():
    random.seed(42)
    num_tests = 100

    weights = []
    in_vals = []
    expected_outs = []

    for _ in range(num_tests):
        w_float = random.uniform(-8.0, 8.0 - (1/4096))
        i_float = random.uniform(-8.0, 8.0 - (1/4096))

        w_q = to_q4_12(w_float)
        i_q = to_q4_12(i_float)

        weights.append(w_q)
        in_vals.append(i_q)

        mac_result = mul_q4_12(w_q, i_q)
        expected_outs.append(mac_result)

    with open('verilog_src/pe_weights.hex', 'w') as f:
        for w in weights:
            f.write(f'{w:04x}\n')

    with open('verilog_src/pe_in_vals.hex', 'w') as f:
        for i in in_vals:
            f.write(f'{i:04x}\n')

    with open('verilog_src/pe_expected_outs.hex', 'w') as f:
        for o in expected_outs:
            f.write(f'{o:04x}\n')

    print(f'Generated {num_tests} PE test vectors')
    print(f'  verilog_src/pe_weights.hex')
    print(f'  verilog_src/pe_in_vals.hex')
    print(f'  verilog_src/pe_expected_outs.hex')

if __name__ == '__main__':
    main()