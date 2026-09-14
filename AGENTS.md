# AGENTS.md — Persistent Context for DLCD Neural Accelerator

## Project Summary

Hardware neural network accelerator implementing a 3-layer MLP (100→16→10) using Q7.8 fixed-point arithmetic. Systolic-array MAC architecture with weight-stationary dataflow. XOR-encrypted weight ROM for IP protection. UART interface for host communication. Built in Verilog, verified with Icarus Verilog and GTKWave.

## System Architecture

- **Topology:** 100 inputs (10x10 image) → 16 hidden neurons (L1) → 6 hidden neurons (L2) → 10 output neurons (L3).
- **Top-Level Goal:** Fully parameterized Verilog design capable of live hardware-in-the-loop inference with an Arduino Uno frontend.

## Architecture Rules (Must Not Be Violated)

1. **Python is pure math ground truth only** — Never a cycle-accurate simulator. Verilog testbenches prove their own timing analytically (compute expected wait cycles, then check), not by mirroring hardware state in Python.

2. **Q7.8 MAC must be sequential multiply-accumulate with truncation at each step**, matching hardware — never a single wide-accumulation matrix op (e.g. `numpy.dot`), since that drifts from real hardware rounding.

3. **Dataflow is weight-stationary**: Weights load once and stay in PE registers; inputs stream through.

4. **Milestones are tagged in Git (M0, M1, M2...)** and represent verified, working states — never tag a milestone with a known bug present.

5. **Load/compute must be mutually exclusive** in systolic_pe.v — the `load_weight` signal and compute logic cannot be active on the same clock edge, or garbage data corrupts the accumulator.

6. **Systolic arrays are built from one reusable parameterized module** (`systolic_array.v`, parameters ROWS/COLS) — never hand-write a new array module per layer. This avoids re-introducing the weight-loading-order bug found in M3. Layer 1 = (16,100), Layer 2 = (6,16), Output layer = (10,6).

7. **ReLU layers are built from one reusable parameterized module** (`layer_relu.v`, parameter ROWS). Layer 1 = 16, Layer 2 = 6.

8. **Global Pipeline Controller**: Data between arrays is captured in pipeline registers (`l1_buffer`, `l2_buffer`, `l3_buffer`) at mathematically precise cycle counts to prevent staggered output corruption.

## Directory / File Map

```
├── verilog_src/          # All Verilog + hex test vectors
│   ├── *.v               # RTL modules and testbenches (tb_*.v)
│   ├── *.hex             # Test vectors for $readmemh
├── python_golden_model/  # Pure math reference (fixed_point_math.py)
├── *.py                  # Test vector generators (generate_*.py, array_golden_model.py)
├── AGENTS.md             # This file — static rules & architecture
├── PROGRESS.md           # Living changelog
```

## Milestone Status Table

| Milestone | Description | Status |
|-----------|-------------|--------|
| **M0** | Python golden model (fixed_point_math.py) | ✅ Done |
| **M1** | MAC + ReLU hardware, self-checking testbench, 100% pass | ✅ Done |
| **M2** | systolic_pe.v cycle-accurate single-PE testbench 100/100 pass, systolic_array_l1.v 16×100 grid elaborates clean | ✅ Done |
| **M3** | Array golden model + tb_systolic_array_l1.v with analytical wait-cycle checking | ✅ Done |
| **M4** | ReLU wrapper on Layer 1 output | ✅ Done |
| **M5** | Refactor to parameterized systolic_array.v; Layer 2 (16->6) | ✅ Done |
| **M6** | Layer 2 ReLU wrapper (refactor layer_relu.v) | ✅ Done |
| **M7** | Layer 3 Array (6->10) | ✅ Done |
| **M8** | Argmax & Classification | ✅ Done |
| **M9** | Top-Level Integration (accelerator_top.v) | ✅ Done |
| **M10** | End-to-End Image Inference | ✅ Done |
| **M11** | Model Training: PyTorch 100->16->6->10 with Q4.12 export | ✅ Done |
| **M12** | Accuracy Improvement: Grayscale Input + Extended Training (93.06% test accuracy) | ✅ Done |
| **M13** | Software Optimization Limits & Reversion (proved 93.06% is the hard ceiling for this architecture; reverted to clean baseline) | ✅ Done |
| **M14** | Q7.8 fixed-point migration — golden model/test-gen scale fix, module renames | ✅ Done |
| **M15** | PC-only batch regression harness — N=20, hardware-vs-golden 100% agreement | ✅ Done |
| **M16** | Local hand-drawn digit testing — pygame canvas, preprocessing, 100% HW-golden agreement | ✅ Done |

## Known Bugs Already Fixed

- **systolic_pe.v load/compute race**: The `load_weight` and compute logic were not mutually exclusive, causing garbage data to corrupt the accumulator during load phase. Fixed by making load and compute branches mutually exclusive in the same `always @(posedge clk)` block.

- **Weight-loading order in systolic arrays**: Shift-register-style weight loading means the last-presented value ends up leftmost, not the first. Any testbench feeding a systolic array's weight columns must present them in reverse order (COLS-1 down to 0) to match the golden model's natural column ordering. Caught in M3; will resurface in any array built by hand rather than reusing `systolic_array_l1.v`.

- **Q-format headroom must be re-checked any time training data, input encoding, epoch count, or regularization changes** — logit magnitudes are not fixed properties of the architecture, they depend on what was actually learned. (Established in M11, re-confirmed in M12 after grayscale input change).

## Toolchain

- **Icarus Verilog**: `C:\iverilog\bin\`
- **Shell**: Windows PowerShell
- **Vector loading**: `$readmemh` for hex files
- **Waveforms**: `$dumpfile` / `$dumpvars` for GTKWave debugging

M16 complete: Local hand-drawn digit testing verified 100% hardware-vs-golden agreement on new/unseen input (pygame canvas, bounding-box crop + 8×8 resize + 10×10 pad preprocessing, Q7.8 headroom confirmed ≤48). Remaining plan:
1. **M17 — Arduino PC-in-the-loop integration**: Arduino Uno captures touchscreen digit, streams via USB Serial to PC, PC bridges to the Verilog sim, classification result returned — the original end-goal stated in PROGRESS.md's project overview.