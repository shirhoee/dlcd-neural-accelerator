# DLCD Neural Network Accelerator (Hardware V1 & V2)

**Course:** Digital Logic and Computer Design (UE25CS251A) — End Semester Assessment  
**Target Application:** Deterministic Edge AI Hardware for MNIST Handwritten Digit Classification  
**Target Hardware RTL:** Verilog-2001 (IEEE 1364-2001), Icarus Verilog (`iverilog`), GTKWave  
**Arithmetic Precision:** Signed 16-bit Q7.8 Fixed-Point (Multiplier = 256.0), Bias-Free, Sequential MAC with Per-Step Truncation `product[23:8]`  
**Verification Baseline:** 100% Bit-Exact Equivalence with Custom Python Q7.8 Integer Emulator  

---

## 1. Project Overview

The **DLCD Neural Accelerator** is a custom digital hardware design engineered in synthesizable Verilog-2001 for high-throughput, low-latency, and strictly deterministic classification of handwritten digits from the MNIST benchmark dataset.

The project encompasses two complete architectural generations:
1. **Version 1.0 (Baseline MLP):** A fully connected Multi-Layer Perceptron (100 $\rightarrow$ 16 $\rightarrow$ 6 $\rightarrow$ 10) that processes 10x10 downsampled inputs through an unrolled 16x16 systolic array in **159 clock cycles** (259 cycles from reset including 100-cycle feature preload).
2. **Version 2.0 (Proposed CNN Accelerator):** A hierarchical 2D Convolutional Neural Network with 20x20 input resolution, streaming line-buffer sliding window generators, fused 2x2 pooling/ReLU units, and a time-multiplexed 16x16 systolic array head (200 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 10) completing classification in **exactly 9,116 clock cycles** (91.16 μs at 100 MHz).

The accelerator operates with **zero host CPU intervention** during runtime and eliminates floating-point units (FPUs) through hardware-software co-designed Q7.8 fixed-point arithmetic.

---

## 2. Key Verified Performance Metrics

All metrics reported below are programmatically verified from the single source of truth (`docs/review/facts.json`) and empirically measured via cycle-accurate simulation and bit-exact software emulation:

| Specification Metric | Version 1.0 (Baseline MLP) | Version 2.0 (Proposed CNN) | Ground Truth Verification |
| :--- | :--- | :--- | :--- |
| **Network Architecture** | 100 $\rightarrow$ 16 $\rightarrow$ 6 $\rightarrow$ 10 (Dense MLP) | Conv1(4ch) $\rightarrow$ MP1 $\rightarrow$ Conv2(8ch) $\rightarrow$ MP2 $\rightarrow$ Systolic(200->64->32->10) | Exact RTL topology |
| **Spatial Input Size** | 10x10 pixels (100 words) | 20x20 pixels (400 words) | 4x higher spatial resolution |
| **Arithmetic Format** | Signed 16-bit Q7.8 | Signed 16-bit Q7.8 (`product[23:8]`) | Bit-exact per-step truncation |
| **Hardware Multipliers** | **256 multipliers** (16x16 array) | **292 multipliers** | 4 in Conv1 + 32 in Conv2 + 256 in Systolic |
| **Inference Latency** | **159 clock cycles** (1.59 μs @ 100 MHz) | **9,116 clock cycles** (91.16 μs @ 100 MHz) | Verified via `test_10.py` and `wave.vcd` |
| **Total Latency from Reset** | **259 clock cycles** (2.59 μs) | **9,117 clock cycles** (91.17 μs) | Cycle from `start` assertion to `done` |
| **Throughput (100 MHz)** | ~386,100 FPS (burst) | **10,969.7 FPS** (continuous) | Exceeds real-time vision rates (>10,000 FPS) |
| **On-Chip Memory** | Distributed Registers | **16,623 words (32.47 KB / 265,968 bits)** | Verified structural depth x width |
| **PyTorch Float32 Accuracy** | 95.39% (10x10 MNIST testset) | **98.83%** (9,883 / 10,000 on MNIST testset) | PyTorch 2.6.0 on full 10k test set |
| **Q7.8 Emulator Accuracy** | 93.06% (M15 test split) | **98.83%** (9,883 / 10,000 on MNIST testset) | Bit-exact integer emulator (`int_emulator_v2.py`) |
| **RTL vs Emulator Parity** | 100% Bit-Exact Match | **100% Bit-Exact Match (0 mismatches)** | **Full 10,000 images** verified in `harness.py` |
| **Testbench Suite Pass Rate** | 100% Pass Rate | **13/13 Passed (0 Failed)** | Canonical `run_all_tests.bat` |

---

## 3. Reconciled Pipeline Stage Latency Breakdown (9,116 Cycles)

The complete inference latency is strictly bounded at 9,116 clock cycles, apportioned across stages as follows:

```
Cycle 0                                                                        Cycle 9,116
|---|---------------------------|-------------------|-------------------|---|---|
  1            4,892                    1,244                 2,977        1   1
Latch      Conv1 + MaxPool1        Conv2 + MaxPool2     MLP Head (Systolic) Arg Align
```

1. **Front-End Latch / Input Sampling Overhead:** 1 cycle (Cycle 0 $\rightarrow$ 1, 35 ns $\rightarrow$ 45 ns)
2. **Conv1 + MaxPool1 Streaming Execution:** 4,892 cycles (Cycle 1 $\rightarrow$ 4893, 45 ns $\rightarrow$ 48,965 ns)
3. **Conv2 Buffering + Conv2 + MaxPool2 Execution:** 1,244 cycles (Cycle 4893 $\rightarrow$ 6137, 48,965 ns $\rightarrow$ 61,405 ns)
4. **MLP Head Systolic Matrix Multiplications:** 2,977 cycles (Cycle 6137 $\rightarrow$ 9114, 61,405 ns $\rightarrow$ 91,175 ns)
5. **Argmax Comparator Resolution:** 1 cycle (Cycle 9114 $\rightarrow$ 9115, 91,175 ns $\rightarrow$ 91,185 ns)
6. **Inter-Stage Pipeline Alignment Gap:** 1 cycle (Cycle 9115 $\rightarrow$ 9116, 91,185 ns $\rightarrow$ 91,195 ns)
- **Total Stage Cycles Sum:** $1 + 4892 + 1244 + 2977 + 1 + 1 = \mathbf{9,116\text{ cycles}}$ ($91.16\ \mu\text{s}$ at 100 MHz).

*Timing Note:* Cycle 0 is when `start` is asserted. At Cycle 1, `start` is sampled into `run_latch`. The testbench counting loop increments while `run_latch` is high until `done` rises at 91,175 ns (Cycle 9117), yielding 9,116 elapsed cycles.

---

## 4. Repository Structure

```
DLCD_Neural_Accelerator/
├── run_all_tests.bat                  # Canonical automated testbench runner (13 active testbenches)
├── run_v2_ui.bat                      # All-in-one launcher for FastAPI backend + React frontend
├── DLCD_Final_Project_Report_UE25CS251A.docx # Official End Semester Assessment Report (DOCX)
├── docs/
│   └── review/
│       ├── facts.json                 # Single source of truth for all verified project numbers
│       ├── DLCD_Final_Project_Report_UE25CS251A.docx # Synchronized final report (DOCX)
│       ├── DLCD_Final_Project_Report_UE25CS251A.pdf  # Synchronized final report (46 pages PDF)
│       ├── confusion_matrix.png       # 10x10 confusion matrix over 10,000 MNIST test images
│       ├── confusion_matrix.csv       # Confusion matrix raw numerical counts
│       ├── PHASE2_LOG.md              # Engineering change log and verification protocol
│       ├── build/
│       │   ├── measure_facts.py       # Facts generator script
│       │   ├── generate_final_report.py # Report generator with 2-pass TOC synchronization
│       │   ├── check_report.py        # Automated QA gate assertion script
│       │   ├── generate_figures.py    # 300 DPI architecture and FSM figure generator
│       │   └── check_gtkw.py          # GTKWave signal verification script
│       ├── figures/                   # 300 DPI architectural figures (Fig 2.1 to 3.3, 7.4)
│       ├── screenshots/               # High-resolution terminal and waveform screenshots
│       └── wave/
│           ├── wave.vcd               # Complete 9,116-cycle simulation waveform artifact
│           ├── wave_full.gtkw         # Top-level full inference overview GTKWave save
│           ├── wave_conv1_mac.gtkw    # Conv1 window & MAC tap sequencing GTKWave save
│           ├── wave_mlp_fsm.gtkw      # MLP Head systolic FSM state transitions GTKWave save
│           └── wave_end.gtkw          # Dense valid, argmax & done pulse GTKWave save
├── v2/
│   ├── verilog_src/                   # Active synthesizable Verilog-2001 RTL modules
│   ├── regression/
│   │   ├── test_10.py                 # Quick 10-image sanity regression test
│   │   ├── harness_emu_new_head.py    # Fast Q7.8 bit-exact software emulator harness
│   │   ├── harness.py                 # Full 10,000-image parallel RTL simulation harness
│   │   └── baseline_summary.json      # Golden baseline regression summary
│   └── v2_ui/
│       ├── backend/                   # FastAPI service for interactive inference
│       └── frontend/                  # React 19 + TypeScript + Vite interactive drawing canvas
└── v1/                                # Version 1.0 Baseline MLP RTL, weights, and testbenches
```

---

## 5. Essential Commands & How to Run

### 5.1 Run All Active Verilog Testbenches (13 Tests)
```cmd
run_all_tests.bat
```
*Expected Output:* `TESTBENCH RUNNER SUMMARY: 13 PASSED, 0 FAILED (100% Pass Rate)`

### 5.2 Run 10-Image Top-Level Hardware Regression
```cmd
cd v2\regression
python test_10.py
```
*Expected Output:* `FINAL SCORECARD: 10/10 PASSED (100.0% Hardware Accuracy), Mean Cycles = 9116.0, Dense Cycles = 2977.0`

### 5.3 Run Fast 10,000-Image Q7.8 Software Emulator
```cmd
cd v2\regression
python harness_emu_new_head.py
```
*Expected Output:* `10,000 images evaluated in ~18 seconds; Accuracy = 98.83%`

### 5.4 Run Full 10,000-Image Parallel Hardware RTL Regression
```cmd
cd v2\regression
python harness.py --workers 16
```
*Expected Output:* `Total Images: 10000 | RTL Accuracy: 0.9883 | RTL vs Emu Mismatches: 0 | Cycles Mean: 9116.0`

### 5.5 Inspect Waveforms in GTKWave
```cmd
gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_full.gtkw
```

### 5.6 Run Automated QA Gate on Generated Report
```cmd
python docs\review\build\check_report.py
```
*Expected Output:* `>> ALL QUALITY ASSURANCE CHECKS PASSED SUCCESSFULLY! <<`

### 5.7 Run Full-Stack Interactive Web UI
```cmd
run_v2_ui.bat
```
Then navigate to `http://localhost:5173` to draw digits and view live hardware cycle traces.

---

## 6. Micro-Architectural Invariants & Design Notes

1. **Strict Compiler Directives:**  
   All 18 active RTL modules enforce `` `timescale 1ns / 1ps `` and `` `default_nettype none `` (with `` `default_nettype wire `` at EOF), guaranteeing synthesis safety and preventing silent implicit 1-bit wire declarations.
2. **Dynamic Toolchain Detection:**  
   All Python regression and simulation harnesses use `shutil.which("iverilog")` with fallback to `C:\iverilog\bin` for cross-platform portability.
3. **Wraparound Arithmetic & Headroom Gate:**  
   `mac_q7_8.v` executes standard 16-bit two's complement modular addition without area-heavy saturation logic. Numerical stability is guaranteed by the training Headroom Gate ($|logit| < 128$), ensuring zero overflow throughout all 10,000 MNIST test images.
4. **Explicit Hardware Reset Requirement:**  
   In `v2_top.v`, `run_latch` latches high upon assertion of `start`, but does not auto-clear on `done`. The hardware `reset` signal must be pulsed active-high between consecutive inferences.
5. **Legacy Modules:**  
   `dense_array.v`, `dense_pe.v`, `layer_relu.v`, and `tb_dense_array.v` are retained for historical provenance but are not instantiated by `v2_top.v`.
