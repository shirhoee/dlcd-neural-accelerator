import math
from fixed_point_math import (
    to_q4_12, from_q4_12, add_q4_12, mul_q4_12, relu_q4_12,
    TOTAL_BITS, FRAC_BITS, SCALE, MASK
)


INPUT_SIZE = 100
HIDDEN_SIZE = 16
OUTPUT_SIZE = 10


def mac_q4_12(acc, weight, input_val):
    return add_q4_12(acc, mul_q4_12(weight, input_val))


def layer_forward(inputs, weights, biases):
    outputs = []
    for i in range(len(weights)):
        acc = biases[i]
        for j in range(len(inputs)):
            acc = mac_q4_12(acc, weights[i][j], inputs[j])
        outputs.append(acc)
    return outputs


def relu_layer(outputs):
    return [relu_q4_12(x) for x in outputs]


def argmax_with_confidence(outputs):
    max_idx = 0
    max_val = outputs[0]
    for i, val in enumerate(outputs):
        val_signed = val if not (val & (1 << (TOTAL_BITS - 1))) else val - (1 << TOTAL_BITS)
        max_signed = max_val if not (max_val & (1 << (TOTAL_BITS - 1))) else max_val - (1 << TOTAL_BITS)
        if val_signed > max_signed:
            max_val = val
            max_idx = i

    second_max = -32768
    for i, val in enumerate(outputs):
        if i == max_idx:
            continue
        val_signed = val if not (val & (1 << (TOTAL_BITS - 1))) else val - (1 << TOTAL_BITS)
        if val_signed > second_max:
            second_max = val_signed

    max_signed = max_val if not (max_val & (1 << (TOTAL_BITS - 1))) else max_val - (1 << TOTAL_BITS)
    confidence = max_signed - second_max
    return max_idx, to_q4_12(confidence)


def forward_pass(input_bits, l1_weights, l1_biases, l2_weights, l2_biases):
    inputs_q = [to_q4_12(bit * SCALE) for bit in input_bits]

    l1_out = layer_forward(inputs_q, l1_weights, l1_biases)
    l1_relu = relu_layer(l1_out)

    l2_out = layer_forward(l1_relu, l2_weights, l2_biases)

    class_idx, confidence = argmax_with_confidence(l2_out)
    return class_idx, confidence