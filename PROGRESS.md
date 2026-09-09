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

## M5 — Layer 2 Array (16 -> 6) (In Progress)
- Refactoring `systolic_array_l1.v` into a reusable parameterized `systolic_array.v` (ROWS, COLS as parameters) so Layer 1, Layer 2, and the output layer all instantiate the same verified module instead of triplicating hand-written arrays
- Layer 2: ROWS=6, COLS=16
- Reusing the already-solved weight-loading order fix and `wait_cycles = r + COLS + 1` timing formula — no new derivation needed