# V2 Architecture Rules & Guidelines

## Project Summary
Hardware neural network accelerator, V2. Adds a convolutional frontend (2x Conv+ReLU+MaxPool) ahead of an MLP head, targeting 20x20 input resolution, digits 0-9 only (MNIST). Q7.8 fixed-point arithmetic, bias-free throughout, reusing V1's verified systolic_array.v / mac_q7_8.v / relu_q7_8.v / layer_relu.v for the MLP portion.

## Inherited from V1 (reused as-is)
- systolic_array.v (parameterized ROWS/COLS systolic MAC array)
- mac_q7_8.v (Q7.8 sequential MAC with truncation)
- 
elu_q7_8.v / layer_relu.v (parameterized ReLU)

**Do not modify without strong reason — these are already verified.**

## New for V2
- Conv2D hardware module(s) + line buffers / sliding window logic
- MaxPool hardware module
- Wider/reconfigured systolic array dimensions for the new MLP head (200->64->32->10)

## Process Rules (Lessons from V1 — non-negotiable)
1. Every training run must pass a mandatory Q7.8 headroom check (max|logit| per layer, with realistic margin, not just theoretical worst-case) before hex export is allowed. No exceptions.
2. The regression harness must validate against BOTH the Q7.8 integer emulator AND true Float32 logits from its very first version, flagging any divergence — not retrofitted after a bug is found.
3. Any live/interactive Tkinter UI testing must be preceded by a synthetic/headless test using the identical preprocessing code path, and that headless test must be verified to actually exercise the preprocessing logic being tested (no silent no-ops that give false confidence).
4. A milestone is not marked complete based on synthetic/simulated results alone if live/interactive testing is part of its definition. Real testing required before tagging.
5. After every milestone, check git status and unpushed commit/tag count as a standing step; push before moving to the next milestone. Do not let commits sit local-only for multiple milestones.
6. The core architecture spec (input resolution: 20x20, layer dimensions, dataset: MNIST digits only, fixed-point format: Q7.8) is locked once N0 is validated, and is not changed without an explicit, justified proposal — not casual mid-project scope changes.
7. Any agent decision involving a real tradeoff (parameter choice, file move/rename, preprocessing method, which layer to rescale) must be reported along with the alternative not taken, before proceeding to the next step.
8. File and directory names, once established for V2, are not renamed mid-project.
9. Milestones are tagged in Git (N0, N1, N2...) representing verified working states — never tag with a known bug present (same discipline as V1's M-series).

## Directory / File Map
- 2/verilog_src/
- 2/python_golden_model/
- 2/AGENTS.md
- 2/PROGRESS.md

## Milestone Plan (Current Status)
- **N0 [COMPLETED]**: PyTorch golden model - Conv+MLP architecture, MNIST digits, float32 validation only
- **N1 [COMPLETED]**: Conv1 Processing Element (conv_pe.v) + testbench
- **N2 [COMPLETED]**: Pooling PE (maxpool_pe.v) + testbench
- **N3a [COMPLETED]**: Sliding-Window Generator (window_gen.v) for 3x3 convolutions + testbench
- **N3b [COMPLETED]**: Full Conv1 array hardware (conv1_array.v) + Master FSM + testbench
- **N4a [COMPLETED]**: MaxPool sliding-window memory router (pool_window_gen.v) + testbench
- **N4b [COMPLETED]**: Full MaxPool array integration
- **N5 [TODO]**: Conv2 Array implementation
- **N6 [TODO]**: Post-conv MLP head systolic arrays & Full pipeline integration + regression harness
- **N7 [TODO]**: Train on MNIST-with-augmentation, headroom sweep, hex export
- **N8 [TODO]**: Live Tkinter/Pygame demo — the real final-stage test

## Known Tradeoffs
- **Duplicated Base Modules**: mac_q7_8.v, relu_q7_8.v, and ixed_point_math.py have been physically copied from 1/ into 2/ to ensure absolute standalone compilation of V2. If V1's originals are ever modified, the V2 copies will NOT automatically stay in sync. This is a deliberate tradeoff to prevent V2 iterations from silently breaking the frozen V1 architecture.

## Interface Contracts
- **Sliding-Window Generator (window_gen.v) Memory Contract**: The window_gen.v module outputs pixel_addr (0-399) and expects the upstream image-storage source to return the corresponding pixel value on pixel_in **COMBINATIONALLY** (same cycle, zero latency). There must be no clocked or registered read delay in the RAM/storage providing this data. This is a locked contract. If a 1-cycle read latency block (like a standard BRAM) is used in the future, a combinational bypass or explicit pre-fetch wrapper must be added, otherwise the pipeline's timing and padding logic will break silently.
- **Address Generation Timing**: window_gen.v drives pixel_addr continuously based on its internal state. The address updates immediately on the clock edge following any cycle where the dvance signal is asserted. It sweeps linearly across the 22x22 virtual padded grid without pausing for specific 'windowing phases'. If dvance is held low, pixel_addr is held perfectly stable. If the current virtual coordinate falls in the zero-padding boundary, the module ignores pixel_in and handles padding internally, but pixel_addr will default to 0 during these cycles.

- **MaxPool Array Latency Contract**: maxpool_array.v processes pixels with completely zero latency relative to valid_in. The pool_window_gen buffers lines perfectly and computes maxpool outputs combinationally in the exact cycle that the bottom-right pixel of the 2x2 stride-2 window arrives (which happens when valid_in pulses on odd row/col). There is no pipelined delay in maxpool_pe or relu_q7_8; they are purely combinational. Downstream modules must consume out_ch0..3 immediately in the cycle valid_out goes high.

- **Conv2 Unpipelined Architecture**: conv2_pe.v instantiates 4 multipliers and a 4-input adder tree sequentially without pipelining before the accumulation register. This heavily cascades the logic depth (multipliers -> adder stage 1 -> adder stage 2 -> accumulator). This design choice was made for simulation simplicity and state-machine compactness, at the expense of a severely degraded physical synthesis Fmax.
- **MaxPool2 Array Gated Shift Contract**: pool2_window_gen.v utilizes valid_in as a strict clock-enable. Its internal 11-stage shift register and window logic are mathematically derived from a pure 10x10 stream. Because downstream Conv2 outputs valid tokens with an 8-cycle idle gap, pool2_window_gen strictly freezes all state when valid_in is low.
- **Dense Array Accumulation**: dense_array.v processes spatial maps perfectly in sync with the MaxPool array output. No internal pipelining exists between the 8 multipliers and the final stage accumulator. The array inherently assumes exactly 25 valid input pulses per frame.
