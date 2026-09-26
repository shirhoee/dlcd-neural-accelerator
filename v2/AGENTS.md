# V2 Architecture Rules & Guidelines

## Inherited from V1 (Reused Components)
To ensure a stable upgrade path and demonstrate clear architectural progression, the following verified, parameterized modules are being reused **as-is** from the V1 architecture:
- `systolic_array.v`
- `mac_q7_8.v`
- `relu_q7_8.v`
- `layer_relu.v`

## New for V2 (Built Fresh)
To support the transition from a simple MLP to a Convolutional Neural Network (CNN), the following components will be built entirely fresh for V2:
- Convolutional layer logic
- Pooling layer logic
- Line buffers (for 2D sliding-window convolutions)
- Wider systolic array dimensions (to support the expanded MLP classification head)
