from typing import List

# MNIST Normalization Parameters
MNIST_MEAN = 0.1307
MNIST_STD = 0.3081
Q7_8_SCALE = 256.0
Q7_8_MIN = -32768
Q7_8_MAX = 32767

def hex16(val: int) -> str:
    """Format signed 16-bit integer into 4-character hex string."""
    return f"{(val & 0xFFFF):04x}"

def parse_signed_str(s: str) -> int:
    """Safely parse signed integer string."""
    try:
        return int(s.strip())
    except ValueError:
        return 0

def downsample_28_to_20(grid_28: List[List[float]]) -> List[List[float]]:
    """Downsample a 28x28 normalized image to 20x20 using nearest-neighbor mapping."""
    grid_20: List[List[float]] = []
    for y in range(20):
        row: List[float] = []
        for x in range(20):
            orig_y = int(y * 28 / 20)
            orig_x = int(x * 28 / 20)
            row.append(grid_28[orig_y][orig_x])
        grid_20.append(row)
    return grid_20

def quantize_to_q7_8_lines(grid_20: List[List[float]]) -> List[str]:
    """Normalize and convert 20x20 grid to Q7.8 hex lines for Verilog readmemh."""
    lines: List[str] = []
    for row in grid_20:
        for val in row:
            norm_val = (val - MNIST_MEAN) / MNIST_STD
            q_val = int(round(norm_val * Q7_8_SCALE))
            if q_val > Q7_8_MAX:
                q_val = Q7_8_MAX
            if q_val < Q7_8_MIN:
                q_val = Q7_8_MIN
            lines.append(hex16(q_val))
    return lines
