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

## M8 — Argmax Logic (Complete)
- Built `argmax.v` with explicit `signed` comparison to avoid 2's complement trap
- Built `tb_argmax.v` loading Layer 3's 10 verified logits
- Correctly selected Digit 1 (logit 174f > 0fcc > 0d7a > all negatives)
- Tagged `M8`

## M9 — Top-Level Integration (Complete)
- Built `accelerator_top.v` with Master Cycle Controller (cycle counter + staggered capture)
- Pipeline registers `l1_buffer` (cycles 102-117), `l2_buffer` (135-140), `l3_buffer` (148-157)
- Argmax at cycle 158, `valid_out` pulse at 159
- Parallel weight loading for all 3 layers (100 cycles) prevents pre-compute zeros
- Tagged `M9`

## M10 — End-to-End Verification (Complete)
- Created `generate_e2e_test.py` generating fresh 100-pixel image + 3-layer weights
- Exported `e2e_input.hex`, `e2e_w1.hex`, `e2e_w2.hex`, `e2e_w3.hex`
- Built `tb_accelerator_top.v` with parallel weight loading, input apply, start pulse
- Hardware logits **identical** to golden model recomputed from hex files (Digit 8)
- Tagged `M10`

## M11 — Model Training (Complete)
- PyTorch script `train_model.py` trains 100->16->6->10 network (bias=False, weight_decay=1e-4)
- 150 epochs, 88.33% test accuracy on MNIST digits (8x8 padded to 10x10, binarized)
- Q4.12 weight export with strict overflow monitoring (0 weights clipped)
- Quantized forward pass replicates exact hardware MAC behavior (per-step 16-bit truncation)
- Exports `e2e_w1.hex`, `e2e_w2.hex`, `e2e_w3.hex`, `e2e_input.hex`, `e2e_true_label.txt`
- PyTorch quantized prediction: Digit 0 | Verilog prediction: Digit 0 → **MATCH**
- Fully reproducible with SEED=42
- Tagged `M11`

## M12 — Accuracy Improvement: Grayscale Input + Extended Training (Complete)
- Removed hard binarization; inputs now use normalized grayscale `[0.0, 1.0]` instead of binary `[0, 1]`.
- Extended training from 150 to 300 epochs, utilizing `CosineAnnealingLR` scheduler.
- New test accuracy achieved: **93.06%**.
- Max absolute logit across the test set: **32.47** (Safely within the Q7.8 headroom limit of ±127.99).
- Hardware re-verified end-to-end after input encoding change: **MATCH YES** (PyTorch Float Prediction: Digit 6, Verilog Prediction: Digit 6).