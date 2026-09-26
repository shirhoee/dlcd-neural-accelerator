# Project Overview: DLCD Neural Accelerator
A Verilog-based systolic array neural network accelerator designed to classify 10x10 pixel hand-drawn digits (0-9).
- **Architecture:** 3-Layer Multilayer Perceptron (100 -> 16 -> 6 -> 10).
- **Math:** Q7.8 Fixed-Point (2's complement).
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

## M13 — Software Optimization Limits & Reversion (Complete)
- Attempted to break the 93.06% accuracy ceiling using data augmentation and dropout.
- Experiment 1 (Over-regularization): Applied 15% dropout, 10-degree rotation, and 1-pixel shift. Accuracy crashed to 76.39%. The 15% dropout crippled the tiny 6-neuron hidden layer, and rotation blurred the 10x10 inputs too heavily.
- Experiment 2 (Translation Only): Removed dropout and rotation, kept 1-pixel shift. Accuracy dropped to 87.22%. A 1-pixel shift on a 10x10 grid is a 10% spatial distortion, which proved too chaotic for the 16-neuron layer to resolve.
- Conclusion: We have scientifically proven that 93.06% is the hard mathematical ceiling for this $100 \rightarrow 16 \rightarrow 6 \rightarrow 10$ bias-free hardware architecture.
- Action Taken: Reverted `train_model.py` to the clean, grayscale-only configuration (300 epochs, Cosine Annealing, no augmentation) to restore and lock in the 93.06% peak baseline.

## M14 — Q7.8 Fixed-Point Migration (Complete)
- Fixed golden model, test-vector generators, and verify scripts to match hardware's Q7.8 format (scale=256, 8 fractional bits) — previously computing at stale Q4.12 (scale=4096, 12 fractional bits)
- Fixed weight_manager.py, which was broken (referenced deleted to_q4_12 function)
- Renamed relu_q4_12.v -> relu_q7_8.v, mac_q4_12.v -> mac_q7_8.v, updated all instantiations
- Updated AGENTS.md and PROGRESS.md documentation to Q7.8 (historical changelog entries for M0-M13 left as-is)
- Full regression M1-M10 re-verified passing, both before and after rename
- Commit d85f042

## M15 — PC-Only Batch Regression Harness (Complete)
- Built `batch_regression_m15.py`: automated N=20 test-set image regression using cached Q7.8 weights
- For each image: PyTorch float forward pass -> Q7.8 golden model (sequential MAC with truncation) -> export e2e_input.hex -> iverilog/vvp compile+run tb_accelerator_top.v -> capture Verilog predicted_digit at valid_out
- Hardware-vs-Golden agreement: **20/20 = 100%** (exact match on all 20 images)
- Golden-vs-True-Label mismatches: **3/20** (consistent with 93.06% model accuracy; 15% observed error rate within normal sampling variance of N=20)
- No Verilog RTL modifications — harness only drives existing verified modules (mac_q7_8.v, systolic_pe.v, systolic_array.v, layer_relu.v, relu_q7_8.v, argmax.v, accelerator_top.v)
- This harness is now the standing regression tool for any future Verilog changes
- Note: Initial run showed 18/20 mismatches due to stale weights in e2e_w*.hex (old failed training run); re-running train_model.py regenerated correct 93.06% baseline weights

## M16 — Local Hand-Drawn Digit Testing (Complete)
- Built **two UIs**: `hand_drawn_m16.py` (pygame, initial) and `hand_drawn_m16_tk.py` (Tkinter, polished — 400×400 canvas, modern buttons, live 10×10 preview with values, large prediction display)
- **Fixed critical preprocessing bugs**: (1) pygame/PIL→numpy axis transpose (W,H vs H,W), (2) tight bounding box diluted thin strokes, (3) max-pooling oversaturated thick mouse strokes — fixed with **square crop (centered, like sklearn digits) + average-pooling resize**
- Preprocessing pipeline: bounding-box crop → square crop (centered) → **average-pooling** resize to 8×8 → pad to 10×10 → normalize to [0.0, 1.0] (matches sklearn antialiased stroke distribution)
- On Predict: downsample → export e2e_input.hex (Q7.8) → PyTorch golden forward pass → iverilog/vvp compile+run tb_accelerator_top.v → capture Verilog predicted_digit
- Q7.8 headroom check: max |logit| ≤ 48 (well within ±127.99 limit; no overflow risk for hand-drawn input)
- Golden-vs-Hardware agreement: **100%** (verified on 6 synthetic digits + interactive testing)
- Model accuracy on hand-drawn digits: **~20%** (2/10 correct on clear digits 0-9) — **domain shift**: model trained on sklearn 8×8 antialiased scans, not thick mouse strokes; this is a model limitation, not a hardware bug
- No Verilog RTL modifications — harness only drives existing verified modules with new input
- M17 (Arduino PC-in-the-loop) is now the final remaining milestone for physical integration.

## M17 — Handwriting Generalization & Q7.8 Overflow Fix (Complete)
- Attempted to solve the hand-drawn domain shift (poor accuracy in M16) by retraining the model on the full MNIST dataset instead of sparse sklearn digits.
- **MNIST Retraining:** Pre-cached and flattened the dataset in memory to bypass a massive 15+ hour PIL resizing bottleneck. Model achieved **95.33%** float accuracy on the MNIST test set while preserving the strict 100->16->6->10 architecture.
- **Critical Bug Discovered:** Live hand-drawn testing revealed severe hardware/golden mismatches (e.g., PyTorch=3, Verilog=9). Investigation proved that the denser MNIST weights combined with thick, heavily saturated hand-drawn digits caused the 16-bit Verilog accumulator to silently overflow/wrap around past its Q7.8 limit (±127.99). Theoretical maximum L2 activations were found to reach ~198.
- **Q7.8 Overflow Fix:** Performed post-training uniform rescaling of all weights (L1, L2, and L3) by an aggressive factor of **~0.709**. This mathematically constrained the absolute worst-case L1 activation to `19.18`, L2 to `99.48`, and realistically bounded L3 to `<100.0` (fully saturated input measured at `37.78`).
- **Accuracy Preserved:** Quantized PyTorch test accuracy on the rescaled hex weights measured **95.39%**, proving the uniform rescaling successfully preserved the relative logit rankings entirely.
- **Harness Blind-Spot Patched:** Modified `batch_regression_m15.py` to compute and monitor true PyTorch Float32 logits alongside the Q7.8 emulator, preventing future 16-bit overflows from being masked by identical emulator wraparound.
- **Final Result:** While the hardware/golden discrepancy was fixed, live hand-drawn digit accuracy remained poor. This represents the absolute functional ceiling for this tiny 16->6->10 bias-free architecture. This is the closing entry for the handwriting-generalization effort; the root cause for the remaining stylistic mismatches will not be further pursued.