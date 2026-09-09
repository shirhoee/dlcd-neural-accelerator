# Project Overview: DLCD Neural Accelerator
A Verilog-based systolic array neural network accelerator designed to classify 10x10 pixel hand-drawn digits (0-9).
- **Architecture:** 3-Layer Multilayer Perceptron (100 -> 16 -> 6 -> 10).
- **Math:** Q4.12 Fixed-Point (2's complement).
- **Dataflow:** Weight-stationary systolic arrays with sequential staggered evaluation.
- **End Goal:** PC-in-the-loop hardware integration where an Arduino Uno captures drawn digits on a touchscreen, streams them to the PC via USB Serial, and the Verilog simulation returns the classification.

# PROGRESS.md — Living Changelog for DLCD Neural Accelerator

## M0 — Python Golden Model (Complete)
- Implemented Q4.12 fixed-point arithmetic in `python_golden_model/fixed_point_math.py`
- Functions: to_q4_12, from_q4_12, mul_q4_12, add_q4_12, relu_q4_12
- Sequential MAC with truncation at each step matches hardware behavior
- Verified against hand-calculated examples

## M1 — MAC & ReLU Hardware (Complete)
- Built `mac_q4_12.v` (combinational multiply-accumulate with Q4.12 truncation)
- Built `relu_q4_12.v` (combinational ReLU)
- Self-checking testbench `tb_mac_relu.v` with 100 random vectors
- All 100 tests pass against Python golden model
- Tagged `M1`

## M2 — Systolic Processing Element (Complete)
- Built `systolic_pe.v` with weight-stationary dataflow and register-passing
- Fixed load/compute race: made `load_weight` and compute branches mutually exclusive in same clock edge
- Cycle-accurate testbench `tb_systolic_pe.v` with 3-cycle protocol (load → compute → check)
- 100/100 vectors pass, timing verified
- Built `systolic_array_l1.v` — 16×100 grid (1,600 PEs) elaborates clean
- Tagged `M2`

## M3 — Array Golden Model + Array Testbench (Complete)
- Built `tb_systolic_array_l1.v` with 100-cycle weight load phase, instrumented watch window, and staggered per-row check using formula `wait_cycles = r + COLS + 1`
- Found and fixed a weight-loading order bug: shift-register loading means the last-presented column ends up leftmost, so the golden model's column-0-first ordering must be fed in reverse (99 down to 0) during the hardware load phase
- Verified output stability: `acc_out_right` holds steady across multiple cycles once weights and inputs are held constant, confirming weight-stationary behavior with no strobe/valid signal needed at this stage
- All 16 rows pass, tagged `M3`

## M4 — ReLU Integration on Layer 1 Output (Complete)
- Built `layer1_relu.v` wrapping 16 instances of the verified `relu_q4_12.v`
- Confirmed port names (`in_val`/`out_val`) against actual source before wiring
- Generated `generate_relu_l1_tests.py`, chaining M3's verified `array_expected_outs.hex` directly as input (not new random data)
- All 16 post-ReLU values match golden model exactly — negative values zeroed, positive values passed through unchanged
- Tagged `M4`

## M5 — Layer 2 Array (16 -> 6) (Complete)
- Built `tb_systolic_array_l2.v` for 6×16 array (96 PEs), reusing `systolic_array.v`, weight-loading reversal fix, and analytical wait-cycle formula (`r + COLS + 1` with elapsed tracking)
- Generated `layer2_golden_model.py` chaining L1 ReLU output (`relu_l1_expected_outs.hex`) as input (no new random data)
- All 6 rows pass perfectly against golden model
- Tagged `M5`

## M6 — Layer 2 ReLU (Complete)
- Refactored `layer1_relu.v` into parameterized `layer_relu.v` (parameter ROWS)
- Syntax clean, `ROWS=6` elaboration verified
- Generated `generate_relu_l2_tests.py`, chaining M5's verified `layer2_expected_outs.hex` as input
- All 6 post-ReLU values match golden model exactly — 3 negative values zeroed, 3 positive values passed through
- Tagged `M6`

## M7 — Layer 3 Array (6 -> 10) (Complete)
- Built `tb_systolic_array_l3.v` for 10×6 array (60 PEs), reusing `systolic_array.v`, weight-loading reversal fix, and analytical wait-cycle formula (`r + COLS + 1` with elapsed tracking)
- Generated `layer3_golden_model.py` chaining L2 ReLU output (`relu_l2_expected_outs.hex`) as input (no new random data)
- All 10 rows pass perfectly against golden model — 10 logits produced
- Tagged `M7`

## M8 — Argmax Logic (In Progress)
- Combinational logic to find the highest value among the 10 logits to determine the predicted digit
- Explicit signed comparison to avoid 2's complement signed/unsigned trap
- Must correctly select digit 1 from M7's output (only positive logits: 1=174f, 4=0d7a, 7=0fcc)

## Future Milestones (Roadmap)
* **M8 — Argmax Logic:** Combinational logic to find the highest value among the 10 outputs to determine the predicted digit.
* **M9 — Top-Level Integration:** Wiring L1, L1_ReLU, L2, L2_ReLU, L3, and Argmax into a single wrapper (`accelerator_top.v`).
* **M10 — End-to-End Verification:** Python script to take a full image, pass it through the Verilog top-module, and verify the final digit prediction.
* **M11 — Hardware Integration:** Arduino C++ code and Python Serial bridge to allow live drawing classification.