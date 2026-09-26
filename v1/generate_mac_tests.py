import sys
import random
import importlib

sys.path.insert(0, 'python_golden_model')
import fixed_point_math
importlib.reload(fixed_point_math)
from fixed_point_math import to_q7_8, mul_q7_8, add_q7_8, relu_q7_8


def generate_random_q7_8():
    return random.randint(-32768, 32767)


def main():
    random.seed(0xDEADBEEF)
    num_tests = 100

    weights = []
    in_vals = []
    acc_ins = []
    expected_mac = []
    expected_relu = []

    for _ in range(num_tests):
        w = generate_random_q7_8() & 0xFFFF
        i = generate_random_q7_8() & 0xFFFF
        a = generate_random_q7_8() & 0xFFFF

        mac_result = add_q7_8(a, mul_q7_8(w, i))
        relu_result = relu_q7_8(mac_result)

        weights.append(w)
        in_vals.append(i)
        acc_ins.append(a)
        expected_mac.append(mac_result)
        expected_relu.append(relu_result)

    def write_hex(filename, data):
        with open(filename, 'w') as f:
            for val in data:
                f.write(f"{val & 0xFFFF:04X}\n")

    write_hex('verilog_src/mac_weights.hex', weights)
    write_hex('verilog_src/mac_in_vals.hex', in_vals)
    write_hex('verilog_src/mac_acc_ins.hex', acc_ins)
    write_hex('verilog_src/mac_expected_mac.hex', expected_mac)
    write_hex('verilog_src/mac_expected_relu.hex', expected_relu)

    print(f"Generated {num_tests} MAC test vectors in verilog_src/")


if __name__ == '__main__':
    main()