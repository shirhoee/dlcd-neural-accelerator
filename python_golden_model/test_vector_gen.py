import os
from network_sim import forward_pass
from weight_manager import load_plain_weights


def generate_class_pattern(class_idx):
    pattern = [[0 for _ in range(10)] for _ in range(10)]

    bar_count = class_idx + 1
    for i in range(bar_count):
        row = i * 2
        if row < 10:
            for col in range(10):
                pattern[row][col] = 1

    if class_idx >= 5:
        for col in range(10):
            pattern[class_idx % 10][col] = 1

    flat = []
    for row in pattern:
        flat.extend(row)
    return flat


def generate_test_vectors():
    os.makedirs('test_vectors', exist_ok=True)

    l1_w, l1_b, l2_w, l2_b = load_plain_weights()

    for class_idx in range(10):
        for sample in range(10):
            idx = class_idx * 10 + sample
            input_bits = generate_class_pattern(class_idx)

            input_path = f'test_vectors/input_{idx:02d}.txt'
            with open(input_path, 'w') as f:
                for bit in input_bits:
                    f.write(f"{bit}\n")

            pred_class, confidence = forward_pass(input_bits, l1_w, l1_b, l2_w, l2_b)
            expected_path = f'test_vectors/expected_{idx:02d}.txt'
            with open(expected_path, 'w') as f:
                f.write(f"{pred_class} {confidence & 0xFFFF:04X}\n")

    print("Generated 100 test vectors in test_vectors/")


if __name__ == '__main__':
    generate_test_vectors()