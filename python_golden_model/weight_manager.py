import random
import math
import os
from fixed_point_math import to_q7_8, MAX_VAL, MIN_VAL


XOR_KEY = 0xA5A5


def xavier_init(fan_in, fan_out):
    scale = math.sqrt(2.0 / (fan_in + fan_out))
    return [random.uniform(-scale, scale) for _ in range(fan_in * fan_out)]


def generate_weights():
    l1_w_floats = xavier_init(INPUT_SIZE, HIDDEN_SIZE)
    l1_b_floats = xavier_init(1, HIDDEN_SIZE)
    l2_w_floats = xavier_init(HIDDEN_SIZE, OUTPUT_SIZE)
    l2_b_floats = xavier_init(1, OUTPUT_SIZE)

    l1_weights = [[to_q7_8(l1_w_floats[i * INPUT_SIZE + j]) for j in range(INPUT_SIZE)] for i in range(HIDDEN_SIZE)]
    l1_biases = [to_q7_8(l1_b_floats[i]) for i in range(HIDDEN_SIZE)]
    l2_weights = [[to_q7_8(l2_w_floats[i * HIDDEN_SIZE + j]) for j in range(HIDDEN_SIZE)] for i in range(OUTPUT_SIZE)]
    l2_biases = [to_q7_8(l2_b_floats[i]) for i in range(OUTPUT_SIZE)]

    return l1_weights, l1_biases, l2_weights, l2_biases


def encrypt_weights(weights, biases):
    enc_weights = [[w ^ XOR_KEY for w in row] for row in weights]
    enc_biases = [b ^ XOR_KEY for b in biases]
    return enc_weights, enc_biases


def write_hex_file(filepath, data):
    with open(filepath, 'w') as f:
        if isinstance(data[0], list):
            for row in data:
                for val in row:
                    f.write(f"{val & 0xFFFF:04X}\n")
        else:
            for val in data:
                f.write(f"{val & 0xFFFF:04X}\n")


def export_all():
    os.makedirs('weights_hex', exist_ok=True)

    l1_w, l1_b, l2_w, l2_b = generate_weights()
    l1_w_enc, l1_b_enc = encrypt_weights(l1_w, l1_b)
    l2_w_enc, l2_b_enc = encrypt_weights(l2_w, l2_b)

    write_hex_file('weights_hex/l1_w_plain.hex', l1_w)
    write_hex_file('weights_hex/l1_w_enc.hex', l1_w_enc)
    write_hex_file('weights_hex/l1_b_plain.hex', l1_b)
    write_hex_file('weights_hex/l1_b_enc.hex', l1_b_enc)
    write_hex_file('weights_hex/l2_w_plain.hex', l2_w)
    write_hex_file('weights_hex/l2_w_enc.hex', l2_w_enc)
    write_hex_file('weights_hex/l2_b_plain.hex', l2_b)
    write_hex_file('weights_hex/l2_b_enc.hex', l2_b_enc)

    print("Exported all weight files to weights_hex/")
    return l1_w, l1_b, l2_w, l2_b


def load_plain_weights():
    def read_hex_2d(filepath, rows, cols):
        with open(filepath, 'r') as f:
            vals = [int(line.strip(), 16) for line in f if line.strip()]
        return [[vals[i * cols + j] for j in range(cols)] for i in range(rows)]

    def read_hex_1d(filepath, size):
        with open(filepath, 'r') as f:
            return [int(line.strip(), 16) for line in f if line.strip()][:size]

    l1_w = read_hex_2d('weights_hex/l1_w_plain.hex', HIDDEN_SIZE, INPUT_SIZE)
    l1_b = read_hex_1d('weights_hex/l1_b_plain.hex', HIDDEN_SIZE)
    l2_w = read_hex_2d('weights_hex/l2_w_plain.hex', OUTPUT_SIZE, HIDDEN_SIZE)
    l2_b = read_hex_1d('weights_hex/l2_b_plain.hex', OUTPUT_SIZE)
    return l1_w, l1_b, l2_w, l2_b


INPUT_SIZE = 100
HIDDEN_SIZE = 16
OUTPUT_SIZE = 10


if __name__ == '__main__':
    export_all()