# CURRENT_STATE.md — DLCD Neural Accelerator Repository Status

**Status Date:** November 2026  
**Project:** Digital Logic & Computer Design (DLCD) Neural Accelerator — UE25CS251A  
**Target:** Hardware Neural Network Accelerator for Handwritten Digit Recognition (MNIST)  
**Single Source of Truth:** `docs/review/facts.json`  

---

## 1. Executive Summary & Verified Metrics

The **DLCD Neural Accelerator** is a hardware-software co-design project implementing custom digital ASIC/FPGA datapath logic in Verilog to perform neural network inference on handwritten digits (MNIST dataset, 0–9).

The codebase encompasses two complete architectural generations:
1. **Version 1 (V1) — Baseline Multi-Layer Perceptron (MLP):**
   - **Topology:** 100-input (10×10 image) $\rightarrow$ 16 (Hidden 1) $\rightarrow$ 6 (Hidden 2) $\rightarrow$ 10 (Output logits) $\rightarrow$ Argmax.
   - **Math Engine:** 16×16 unrolled 2D systolic array core utilizing weight-stationary dataflow (256 multipliers).
   - **Latency:** 159 clock cycles inference latency (259 clock cycles total from reset, including 100-cycle feature preload).
   - **Throughput (100 MHz):** 628,930.8 FPS (theoretical pipelined: 100 MHz / 159 cycles); 386,100.4 FPS (derived from reset including 100-cycle preload: 100 MHz / 259 cycles).
   - **Accuracy:** 93.06% on M15 optical digits split (95.39% on downsampled 10×10 MNIST testset).

2. **Version 2 (V2) — Convolutional Neural Network (CNN) + Systolic MLP Head:**
   - **Topology:** 400-input (20×20 image) $\rightarrow$ Conv1 (1 $\rightarrow$ 4 ch, 3×3, valid) $\rightarrow$ MaxPool1 (2×2, stride 2, 4 ch, 9×9) $\rightarrow$ Conv2 (4 $\rightarrow$ 8 ch, 3×3, valid) $\rightarrow$ MaxPool2 (2×2, stride 2, 8 ch, 5×5) $\rightarrow$ MLP Head (200 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 10) $\rightarrow$ Argmax.
   - **Hardware Multipliers:** Total = 292 (4 in Conv1 + 32 in Conv2 + 256 in Systolic Head).
   - **Execution Latency:** Exactly **9,116 clock cycles** (91.16 μs at 100 MHz clock frequency).
   - **Throughput (100 MHz):** 10,969.7 FPS (theoretical pipelined: 100 MHz / 9,116 cycles); 10,964.9 FPS (demonstrated with 4-cycle reset sequence: 100 MHz / 9,120 cycles).
   - **On-Chip Memory:** 16,623 words × 16-bit (265,968 bits / 32.47 KB) across weight ROMs, ping-pong RAMs, and line buffers.
   - **Classification Accuracy:** **98.83%** on the full 10,000 MNIST test images (9,883 / 10,000 correct in both PyTorch Float32 and Q7.8 integer emulator).
   - **Hardware Parity:** **100% bit-exact equivalence (0 mismatches)** across all 10,000 test images in Icarus Verilog simulation (`harness.py`).

---

## 2. Reconciled Pipeline Stage Latency Breakdown (9,116 Cycles)

| Stage ID | Pipeline Stage Name | Start Cycle | End Cycle | Cycles | Elapsed Time (100 MHz) | Function |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | Front-End Latch / Input Sampling | 0 | 1 | 1 | 0.01 μs | `start` registered into `run_latch` (`v2_top.v:16-23`), deasserting `internal_reset` (`v2_top.v:25`) |
| **2** | Conv1 + MaxPool1 Streaming | 1 | 4,893 | 4,892 | 48.92 μs | 4-channel 3×3 convolution + 2×2 max-pooling on 20×20 pixels |
| **3** | Conv2 Buffering + Conv2 + MaxPool2 | 4,893 | 6,137 | 1,244 | 12.44 μs | 8-filter 4-channel 3×3 convolution + 2×2 max-pooling into `ram_A` |
| **4** | MLP Head Systolic Multiplications | 6,137 | 9,114 | 2,977 | 29.77 μs | Time-multiplexed 16×16 systolic array computing 200→64→32→10 |
| **5** | Argmax Comparator Resolution | 9,114 | 9,115 | 1 | 0.01 μs | 10-input tournament comparator tree extracts predicted class |
| **6** | Inter-Stage Pipeline Alignment Gap | 9,115 | 9,116 | 1 | 0.01 μs | Final register latching and top-level `done` assertion |
| **TOTAL** | **Complete Hardware Inference** | **0** | **9,116** | **9,116** | **91.16 μs** | **Strictly bounded, deterministic execution** |

---

## 3. Active Verilog Modules Status & Directives

All 18 active RTL modules strictly enforce `` `timescale 1ns / 1ps `` and `` `default_nettype none `` discipline:

| Module Name | File Path | Role & Architecture | Multipliers | Compiler Directives |
| :--- | :--- | :--- | :---: | :--- |
| `v2_top` | `v2/verilog_src/v2_top.v` | Top-level chip integration & ROM instantiation | — | `timescale, `default_nettype none |
| `window_gen` | `v2/verilog_src/window_gen.v` | Conv1 line buffer (SR[0:46]) & 3×3 sliding window | — | `timescale, `default_nettype none |
| `conv_pe` | `v2/verilog_src/conv_pe.v` | Conv1 weight-stationary PE (9 taps, 1 MAC) | 1 | `timescale, `default_nettype none |
| `mac_q7_8` | `v2/verilog_src/mac_q7_8.v` | Signed 16×16 Q7.8 MAC ALU (`product[23:8]`) | 1 | `timescale, `default_nettype none |
| `conv1_array` | `v2/verilog_src/conv1_array.v` | Conv1 4-channel controller (IDLE, INIT, COMPUTE) | 4 | `timescale, `default_nettype none |
| `pool_window_gen` | `v2/verilog_src/pool_window_gen.v` | MaxPool1 2×2 window buffer | — | `timescale, `default_nettype none |
| `maxpool_pe` | `v2/verilog_src/maxpool_pe.v` | Fused 2×2 maxpool + ReLU comparator tournament | — | `timescale, `default_nettype none |
| `maxpool_array` | `v2/verilog_src/maxpool_array.v` | 4-channel MaxPool1 array | — | `timescale, `default_nettype none |
| `relu_q7_8` | `v2/verilog_src/relu_q7_8.v` | Non-negative clipping activation | — | `timescale, `default_nettype none |
| `conv2_window_gen`| `v2/verilog_src/conv2_window_gen.v`| Conv2 4-channel line buffers (4x SR[0:26]) | — | `timescale, `default_nettype none |
| `conv2_pe` | `v2/verilog_src/conv2_pe.v` | Conv2 4-channel parallel PE (4 MACs) | 4 | `timescale, `default_nettype none |
| `conv2_array` | `v2/verilog_src/conv2_array.v` | Conv2 8-filter controller (IDLE, INIT, COMPUTE) | 32 | `timescale, `default_nettype none |
| `pool2_window_gen`| `v2/verilog_src/pool2_window_gen.v`| MaxPool2 2×2 window buffer | — | `timescale, `default_nettype none |
| `maxpool2_array` | `v2/verilog_src/maxpool2_array.v` | 8-channel MaxPool2 array | — | `timescale, `default_nettype none |
| `mlp_head` | `v2/verilog_src/mlp_head.v` | 6-state FSM controller, dual ping-pong RAMs | — | `timescale, `default_nettype none |
| `systolic_array` | `v2/verilog_src/systolic_array.v`| 16×16 2D mesh of processing elements | 256 | `timescale, `default_nettype none |
| `systolic_pe` | `v2/verilog_src/systolic_pe.v` | Output-stationary PE with weight latch & skew DFFs | 1 | `timescale, `default_nettype none |
| `argmax` | `v2/verilog_src/argmax.v` | 10-input tournament comparator tree | — | `timescale, `default_nettype none |

*Non-instantiated legacy modules:* `dense_array.v`, `dense_pe.v`, `layer_relu.v`, and `tb_dense_array.v` remain in the directory for historical reference but are not in the active synthesis datapath.

---

## 4. Verification Suite & Test Commands

1. **Automated Hardware Suite (13 Tests):**
   ```cmd
   run_all_tests.bat
   ```
   *Status:* 13 PASSED, 0 FAILED (100% pass rate).
2. **10-Image Regression:**
   ```cmd
   cd v2\regression
   python test_10.py
   ```
   *Status:* 10/10 MATCH, Mean Cycles = 9,116.0, Dense Cycles = 2,977.0.
3. **Full 10,000-Image Hardware Regression:**
   ```cmd
   cd v2\regression
   python harness.py --workers 16
   ```
   *Status:* 10,000/10,000 MATCH (0 mismatches), Accuracy = 98.83%.
4. **Report QA Gate:**
   ```cmd
   python docs\review\build\check_report.py
   ```
   *Status:* ALL QUALITY ASSURANCE CHECKS PASSED.
