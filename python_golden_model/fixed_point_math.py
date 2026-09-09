TOTAL_BITS = 16
FRAC_BITS = 12
SCALE = 1 << FRAC_BITS
MAX_VAL = (1 << (TOTAL_BITS - 1)) - 1
MIN_VAL = -(1 << (TOTAL_BITS - 1))
MASK = (1 << TOTAL_BITS) - 1


def to_signed_16(x):
    return x - 65536 if x >= 32768 else x


def to_q4_12(f):
    val = int(round(f * SCALE))
    if val > MAX_VAL:
        return MAX_VAL
    if val < MIN_VAL:
        return MIN_VAL
    return val & MASK


def from_q4_12(i):
    if i & (1 << (TOTAL_BITS - 1)):
        i -= 1 << TOTAL_BITS
    return i / SCALE


def add_q4_12(a, b):
    a_signed = to_signed_16(a)
    b_signed = to_signed_16(b)
    return (a_signed + b_signed) & MASK


def mul_q4_12(a, b):
    a_signed = to_signed_16(a)
    b_signed = to_signed_16(b)
    product = a_signed * b_signed
    result = (product >> FRAC_BITS) & MASK
    return result


def relu_q4_12(x):
    x_signed = to_signed_16(x)
    if x_signed < 0:
        return 0
    return x