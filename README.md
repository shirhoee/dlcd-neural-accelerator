# DLCD Neural Network Accelerator — Hardware V1 & V2

[![Verilog-2001](https://img.shields.io/badge/RTL-Verilog--2001-blue.svg)](https://en.wikipedia.org/wiki/Verilog)
[![Simulation](https://img.shields.io/badge/Simulator-Icarus%20Verilog%20%2B%20GTKWave-brightgreen.svg)](http://iverilog.icarus.com/)
[![Accuracy](https://img.shields.io/badge/Testset%20Accuracy-98.70%25%20(Bit--Exact%20RTL)-orange.svg)](#2-verified-performance-scorecard-v1-vs-v2)
[![Latency](https://img.shields.io/badge/Latency-9%2C116%20Cycles%20(91.16%20%C2%B5s)-purple.svg)](#4-reconciled-pipeline-latency-breakdown-9116-cycles)
[![Throughput](https://img.shields.io/badge/Throughput-10%2C969.7%20FPS%20%40%20100MHz-red.svg)](#4-reconciled-pipeline-latency-breakdown-9116-cycles)

**Course:** Digital Logic and Computer Design Laboratory (UE25CS251A) — End Semester Assessment (ESA)  
**Institution:** Department of Computer Science & Engineering, PES University, Bengaluru  
**Target Application:** Deterministic Edge AI Hardware for MNIST Handwritten Digit Classification (0–9)  
**Hardware RTL:** Synthesizable Verilog-2001 (IEEE 1364-2001) under strict `` `default_nettype none `` discipline  
**Arithmetic Precision:** Signed 16-bit Q7.8 Fixed-Point (Scale Factor = 256.0), Strictly Bias-Free, Sequential MAC with Per-Step Truncation `product[23:8]`  
**Verification Baseline:** 100% Bit-Exact Equivalence with Custom Python Q7.8 Integer Emulator (0 mismatches across all 10,000 MNIST test images)  

---

## Team Roster & Project Ownership

| Student Name | Student Registration No. (SRN) | Core Project Role | Authored RTL & Subsystems |
| :--- | :--- | :--- | :--- |
| **Shreyansh Raj** | `PES2UG25CS516` | **Lead Hardware Architect & RTL Verification** | Top-level integration (`v2_top.v`), Argmax comparator (`argmax.v`), verification testbenches (`tb_submission.v`, `tb_top.v`), regression harness (`harness.py`), full-stack UI |
| **Sarthak Bhowmik** | `PES2UG25CS493` | **Digital Datapath & Systolic Array Design** | 16×16 systolic mesh (`systolic_array.v`), systolic PE (`systolic_pe.v`), time-multiplexed controller (`mlp_head.v`), ping-pong SRAMs |
| **Shaurya Singh** | `PES2UG25CS508` | **Convolutional PE & Line Buffer Subsystems** | 47-sr line buffer (`window_gen.v`), 9-tap sequential MAC PE (`conv_pe.v`), Conv1 array (`conv1_array.v`), Conv2 multichannel array (`conv2_array.v`), MaxPool+ReLU |
| **Shreya Anand** | `PES2UG25CS515` | **Q7.8 Quantization & Fixed-Point Golden Models** | Q7.8 arithmetic primitives (`mac_q7_8.v`, `relu_q7_8.v`), bit-exact integer emulators (`int_emulator_v2.py`), Headroom Gate, ROM generators |

---

## Table of Contents
1. [Project Overview & Key Architectural Innovations](#1-project-overview--key-architectural-innovations)
2. [Verified Performance Scorecard: V1 vs V2](#2-verified-performance-scorecard-v1-vs-v2)
3. [Top-Level Hardware Architecture & Datapath](#3-top-level-hardware-architecture--datapath)
4. [Reconciled Pipeline Latency Breakdown (9,116 Cycles)](#4-reconciled-pipeline-latency-breakdown-9116-cycles)
5. [Time-Multiplexed Systolic Head (62-Tile Schedule)](#5-time-multiplexed-systolic-head-62-tile-schedule)
6. [Q7.8 Fixed-Point Numerical Invariants](#6-q78-fixed-point-numerical-invariants)
7. [Finite State Machines (FSMs) & Control Flow](#7-finite-state-machines-fsms--control-flow)
8. [On-Chip Memory Budget & ROM Map](#8-on-chip-memory-budget--rom-map)
9. [Verification Suite & Essential Commands](#9-verification-suite--essential-commands)
10. [Full-Stack Interactive Web GUI](#10-full-stack-interactive-web-gui)
11. [Viva Voce Defense & Project Documentation Links](#11-viva-voce-defense--project-documentation-links)
12. [Repository Directory Structure](#12-repository-directory-structure)

---

## 1. Project Overview & Key Architectural Innovations

The **DLCD Neural Accelerator** is a custom hardware ASIC/FPGA design engineered for high-throughput, low-latency, and strictly deterministic classification of handwritten digits from the MNIST dataset.

The repository houses two complete generations of neural hardware:
- **Version 1.0 (Baseline MLP):** A fully-connected Multi-Layer Perceptron ($100 \to 16 \to 6 \to 10$) that processes heavily downsampled 10×10 images through an unrolled 16×16 systolic array in **159 clock cycles** (259 cycles from reset with 100-cycle serial preload), achieving **93.06% accuracy** (95.39% validation).
- **Version 2.0 (Proposed CNN Accelerator):** A 6-layer Convolutional Neural Network with 20×20 input resolution, streaming line-buffer window generators, fused MaxPool+ReLU units, and a time-multiplexed 16×16 systolic array head ($200 \to 64 \to 32 \to 10$) completing classification in **exactly 9,116 clock cycles** (91.16 µs at 100 MHz) with **98.70% bit-exact hardware accuracy** (+5.64% boost over V1).

### Key Architectural Innovations
1. **Zero FPUs with Q7.8 Fixed-Point Arithmetic:** All weights, activations, and accumulators use 16-bit signed two's complement integers with scale factor 256.0. Multipliers truncate at every step (`product[23:8]`), avoiding expensive 32-bit floating-point units.
2. **Preservation of 2D Spatial Resolution:** By upgrading input resolution from 10×10 to 20×20, we preserve critical digit topology (loops in 8s and 0s) while eliminating 49% of blank border padding compared to 28×28 inputs.
3. **Time-Multiplexed Systolic Array:** A naïve unrolled implementation of the dense classification layers would require **15,168 hardware multipliers**. By time-multiplexing a single 16×16 systolic array (256 MACs) across 62 matrix tiles with dual ping-pong RAMs (`ram_A` and `ram_B`), we saved over **98.3% of dense multiplier area**.
4. **Fused MaxPool + ReLU Optimization:** Because ReLU is monotonically non-decreasing, $\max(\text{ReLU}(x)) \equiv \text{ReLU}(\max(x))$. Placing the ReLU gate after the 2×2 tournament comparator tree eliminates **75% of ReLU multiplexer gates**.
5. **Strictly Bias-Free Training & The Headroom Gate:** All layers are trained without biases, eliminating 122 hardware adders and preventing bias saturation drift. Enforcing the Headroom Gate ($|x| < 128.0$) mathematically guarantees zero overflow, removing the need for area-heavy saturation logic.

---

## 2. Verified Performance Scorecard: V1 vs V2

All numbers below are extracted directly from the verified ground truth (`docs/review/facts.json`) and empirically measured via cycle-accurate simulation and full 10,000-image testset execution:

| Parameter / Architectural Metric | Version 1.0 (Baseline MLP) | Version 2.0 (Proposed CNN) | Relative Improvement / Architectural Note |
| :--- | :--- | :--- | :--- |
| **Model Topology** | $100 \to 16 \to 6 \to 10$ (Dense) | Conv1(4ch) $\to$ MP1 $\to$ Conv2(8ch) $\to$ MP2 $\to$ Systolic Head($200 \to 64 \to 32 \to 10$) | Hierarchical 2D feature extraction preserving spatial context |
| **Input Spatial Resolution** | 10×10 pixels (100 words) | 20×20 pixels (400 words) | **4× spatial information**; prevents stroke collapse |
| **Arithmetic Format** | Signed 16-bit Q7.8 | Signed 16-bit Q7.8 (`product[23:8]`) | Zero FPUs; 1 sign, 7 integer, 8 fractional bits |
| **Bias Policy** | Bias-free | Strictly Bias-Free | Eliminates 122 adders; zero bias drift |
| **Hardware Multipliers** | 256 (16×16 Systolic Mesh) | **292 leaf multipliers** | 4 in Conv1 + 32 in Conv2 + 256 in Systolic Array |
| **Unrolled Multipliers Avoided** | N/A | **15,168 multipliers avoided** | 59.25× multiplier area reduction in dense head |
| **On-Chip Memory (SRAM/ROM)** | ~3.2 KB | **32.47 KB (16,623 words)** | Includes image ROM, weight ROMs, line buffers, ping-pong RAMs |
| **Clock Frequency** | 100.0 MHz (10.0 ns) | 100.0 MHz (10.0 ns) | Standard target for low-power edge FPGAs (Artix-7/Zynq) |
| **Deterministic Latency** | 159 compute / 259 total | **9,116 clock cycles** | **91.16 µs** execution time (absolute done at cycle 9,117) |
| **Throughput @ 100 MHz** | 386,100 FPS | **10,969.7 FPS** (theoretical)<br>**10,964.9 FPS** (demonstrated) | Over 10,000 inferences/sec for real-time edge vision |
| **Hardware Testset Accuracy** | 93.06% (10k test set) | **98.70% (9,870 / 10,000)** | **+5.64% accuracy improvement** on full MNIST test set |
| **Float32 PyTorch Accuracy** | 95.39% (sub) / 93.06% | **98.83% (9,883 / 10,000)** | Only 13 images differ between Float32 and Q7.8 hardware |
| **RTL vs Python Emulator Parity** | 100% Bit-Exact | **100% Bit-Exact (0 mismatches)** | Verified across all 10,000 test images in `harness.py` |
| **Unit Testbench Pass Rate** | 100% Pass Rate | **13/13 Passed (100% Pass Rate)** | Verified via canonical `run_all_tests.bat` |

---

## 3. Top-Level Hardware Architecture & Datapath

```
                       TOP-LEVEL ACCELERATOR BLOCK DIAGRAM (v2_top.v)
  =========================================================================================

     [Image Memory] (400 words x 16-bit Q7.8)
           │
           │ pixel_addr [8:0] / pixel_in [15:0]
           ▼
     ┌───────────────┐
     │  window_gen   │ ◄── 47-element shift-register line buffer (sr[0..46])
     └───────┬───────┘     Extracts 3x3 receptive fields combinatorially (win_0..win_8)
             │
             │ 9 parallel taps
             ▼
     ┌───────────────┐
     │  conv1_array  │ ◄── 4 parallel PEs (4 multipliers), conv1_rom (36 weights)
     └───────┬───────┘     6-state FSM; 4,892 cycles total
             │
             │ 4 streaming channels (out_ch0..out_ch3)
             ▼
     ┌───────────────┐
     │ maxpool_array │ ◄── 4-channel 2x2 tournament max + fused ReLU gates
     └───────┬───────┘     Streaming zero-latency downsampling to 10x10 feature maps
             │
             │ 4 channels (100 feature vectors)
             ▼
     ┌───────────────┐
     │  conv2_array  │ ◄── 8 filter groups x 4 PEs (32 multipliers), conv2_rom (288 weights)
     └───────┬───────┘     4-channel adder trees per filter; 6-state FSM; 1,244 cycles
             │
             │ 8 streaming channels (out_ch0..out_ch7)
             ▼
     ┌───────────────┐
     │ maxpool2_array│ ◄── 8-channel 2x2 tournament max + fused ReLU gates
     └───────┬───────┘     Streaming downsampling to 5x5 feature maps (200 activations)
             │
             │ 8 channels (25 valid pulses = 200 activations)
             ▼
     ┌───────────────┐
     │   mlp_head    │ ◄── Time-multiplexed 16x16 systolic array (256 MACs), mlp_rom (992w)
     │               │     Dual Ping-Pong SRAMs: ram_A (208 words), ram_B (64 words)
     └───────┬───────┘     4-state FSM; 62 tiles @ 48 cyc/tile; 2,977 cycles total
             │
             │ 10 class logits (out_digit_0..out_digit_9)
             ▼
     ┌───────────────┐
     │    argmax     │ ◄── 4-level balanced binary comparator tree (1-cycle latency)
     └───────┬───────┘
             │
             ▼
      prediction [3:0] (0-9)  +  done strobe
```

---

## 4. Reconciled Pipeline Latency Breakdown (9,116 Cycles)

The complete hardware inference latency from `start` assertion to `done` pulse is **strictly bounded at exactly 9,116 clock cycles** (91.16 µs at 100 MHz):

$$\text{Total Latency} = T_{\text{Latch}} + T_{\text{Conv1+MP1}} + T_{\text{Conv2+MP2}} + T_{\text{MLP}} + T_{\text{Argmax}} + T_{\text{Handshake}} = 9,116\text{ cycles}$$

```
Cycle 0                                                                        Cycle 9,116
|---|---------------------------|-------------------|-------------------|---|---|
  1            4,892                    1,244                 2,977        1   1
Latch      Conv1 + MaxPool1        Conv2 + MaxPool2     MLP Head (Systolic) Arg Align
```

| Stage ID | Pipeline Stage Name | Start Cycle | End Cycle | Cycles | Elapsed Time (100 MHz) | Functional Operation |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | **Front-End Latch / Input Sampling** | 0 | 1 | **1** | 0.01 µs | `start` strobe sampled into `run_latch` in `v2_top.v:16-23`, deasserting `internal_reset` to enable Conv1 |
| **2** | **Conv1 + MaxPool1 Streaming** | 1 | 4,893 | **4,892** | 48.92 µs | 4-channel 3×3 convolution across 400 windows + streaming 2×2 max-pooling (400 $\to$ 100 pixels/channel) |
| **3** | **Conv2 Buffering + Conv2 + MP2** | 4,893 | 6,137 | **1,244** | 12.44 µs | Buffering 100 features + 8-filter 4-channel 3×3 convolution + 2×2 max-pooling into `ram_A` |
| **4** | **MLP Head Systolic Multiplications** | 6,137 | 9,114 | **2,977** | 29.77 µs | 62 tiles $\times$ 48 cycles (16 load + 32 compute) + 1 idle cycle computing $200 \to 64 \to 32 \to 10$ |
| **5** | **Argmax Comparator Resolution** | 9,114 | 9,115 | **1** | 0.01 µs | 4-level tournament comparator tree determines winning digit index `[0..9]` |
| **6** | **Inter-Stage Pipeline Alignment** | 9,115 | 9,116 | **1** | 0.01 µs | Output register latching and top-level `done` strobe assertion |
| **TOTAL** | **Complete Inference Datapath** | **0** | **9,116** | **9,116** | **91.16 µs** | **Deterministic, invariant execution time on every MNIST digit** |

> **Note on Cycle 9,116 vs 9,117:** Absolute Cycle 9,117 is the clock edge where the testbench samples `done == 1`. Because the testbench counter starts counting from Cycle 1 (the first active cycle of `run_latch`), the elapsed execution latency measured and printed by the testbench is $9,117 - 1 = \mathbf{9,116}$ clock cycles.

---

## 5. Time-Multiplexed Systolic Head (62-Tile Schedule)

The MLP dense classification head executes three fully-connected layers:
- **Layer 1 (Dense 1):** $200 \to 64$ ($200 \times 64 = 12,800$ weights)
- **Layer 2 (Dense 2):** $64 \to 32$ ($64 \times 32 = 2,048$ weights)
- **Layer 3 (Dense 3 / Logits):** $32 \to 10$ ($32 \times 10 = 320$ weights)
- **Total weights:** 15,168 weights.

Rather than implementing 15,168 multipliers, the controller partitions the matrix multiplications into 16×16 tiles executed on the **256-multiplier systolic array** using dual ping-pong RAMs (`ram_A` and `ram_B`):

| Layer Index | Input Dimension $\to$ Output Dimension | Source RAM | Dest RAM | Row Tiles $\times$ Col Tiles | Total Tiles | Cycles per Tile (Load + Compute) | Total Layer Latency |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Layer 1** | $200 \to 64$ | `ram_A` (208w) | `ram_B` (64w) | 13 rows $\times$ 4 cols | 52 tiles | 48 cycles (16 + 32) | **2,496 cycles** |
| **Layer 2** | $64 \to 32$ | `ram_B` (64w) | `ram_A` (208w) | 4 rows $\times$ 2 cols | 8 tiles | 48 cycles (16 + 32) | **384 cycles** |
| **Layer 3** | $32 \to 10$ | `ram_A` (208w) | Output Regs | 2 rows $\times$ 1 col | 2 tiles | 48 cycles (16 + 32) | **96 cycles** |
| **FSM Handover** | Pipeline flush & handshake | — | — | — | — | 1 cycle | **1 cycle** |
| **Total MLP Head** | **$200 \to 64 \to 32 \to 10$** | — | — | — | **62 tiles** | — | **2,977 cycles** |

*Each tile takes exactly 48 cycles:* 16 cycles shift-loading weights from `mlp_rom` (`LOAD_WEIGHT`) + 32 cycles streaming activations and accumulating partial sums (`COMPUTE`).

---

## 6. Q7.8 Fixed-Point Numerical Invariants

1. **Format Specification:**
   - 1 sign bit, 7 integer bits, 8 fractional bits ($S1I7F8$).
   - Multiplier / Scale Factor: $2^8 = 256.0$.
   - Numerical Range: $[-128.0, +127.99609375]$ (Raw integer: $[-32768, +32767]$).
   - Precision: $\frac{1}{256} \approx 0.00390625$.
2. **Product Realignment Slice:**
   - Multiplication of two Q7.8 numbers yields a 32-bit Q14.16 product.
   - Slicing `product[23:8]` drops the lower 8 fractional bits, restoring exact Q7.8 fractional alignment.
3. **Strictly Bias-Free Layers:**
   - Eliminates 122 hardware adders and prevents bias saturation drift.
4. **The Headroom Gate:**
   - Maximum measured activation across all 10,000 images is $41.15 \ll 128.0$.
   - Overflow is mathematically impossible, allowing clean two's complement wraparound arithmetic without area-heavy saturation logic.

---

## 7. Finite State Machines (FSMs) & Control Flow

The accelerator datapath is orchestrated by three synchronous FSMs:

### 7.1 `conv1_array` 6-State Controller (3-bit: `3'd0` to `3'd5`)
- `ST_INIT` (`3'd0`): Preloads 36 weights from `conv1_rom` into PE shift registers via `init_cnt` (0..8). Transitions to `ST_FETCH` when `init_cnt == 8`.
- `ST_ADVANCE` (`3'd1`): 1-cycle pipeline shift strobe that advances `window_gen` past the completed receptive field. Transitions to `ST_FETCH`.
- `ST_FETCH` (`3'd2`): Holds advance high until `window_gen` asserts `win_valid`. Transitions to `ST_MAC`.
- `ST_MAC` (`3'd3`): 9-cycle MAC accumulation across 4 parallel PEs. On cycle 0, pulses `clr_acc`; on cycles 0..8, asserts `mac_en`. Transitions to `ST_WAIT_VALID` when `mac_cnt == 8`.
- `ST_WAIT_VALID` (`3'd4`): Latches PE outputs. If `win_done == 1`, transitions to `ST_DONE`; else loops back to `ST_ADVANCE`.
- `ST_DONE` (`3'd5`): Conv1 complete; asserts `done` strobe.

### 7.2 `conv2_array` 6-State Multichannel Controller (3-bit: `3'd0` to `3'd5`)
- `ST_LOAD` (`3'd0`): Buffers 100 features from MaxPool1 across 4 channels (`write_addr` 0..99). Transitions to `ST_FETCH` on `write_addr == 99 && valid_in`.
- `ST_FETCH` (`3'd1`): Awaits window generator valid strobe `w_valid`. Transitions to `ST_MAC`.
- `ST_MAC` (`3'd2`): 9-cycle MAC accumulation across 8 filter groups (32 multipliers active). Transitions to `ST_WAIT_VALID` on `mac_cnt == 8`.
- `ST_WAIT_VALID` (`3'd3`): Sums 4-channel products through adder tree and asserts `valid_out`. If `w_done == 1`, transitions to `ST_DONE`; else to `ST_ADVANCE`.
- `ST_ADVANCE` (`3'd4`): Shifts line buffer by 1 pixel. Transitions to `ST_FETCH`.
- `ST_DONE` (`3'd5`): All 100 convolved spatial vectors produced; asserts `done`.

### 7.3 `mlp_head` 4-State Time-Multiplexed Controller (2-bit: `2'd0` to `2'd3`)
- `IDLE` (`2'd0`): Buffers 200 flattened features from MaxPool2 into `ram_A`. On `write_ptr == 192 && valid_in`, initializes layer counters and transitions to `LOAD_WEIGHT`.
- `LOAD_WEIGHT` (`2'd1`): Shifts 16 words from `mlp_rom` into systolic array (timer counts 0..15, 16 cycles). Transitions to `COMPUTE`.
- `COMPUTE` (`2'd2`): Streams activations through systolic mesh and accumulates partial sums (timer counts 0..31, 32 cycles). Latches valid outputs to ping-pong RAM with fused ReLU. On `timer == 31`, advances tile counters; if last tile of Layer 3, transitions to `DONE`; otherwise loops back to `LOAD_WEIGHT`.
- `DONE` (`2'd3`): Classification complete; asserts `valid_out`.

---

## 8. On-Chip Memory Budget & ROM Map

The total on-chip memory footprint across all storage structures is **16,623 words (32.47 KB / 265,968 bits)**:

| Memory Structure | RTL Location | Depth $\times$ Width | Word Count | Size (Bits) | Size (Bytes) | Role / Content |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Image Test ROM** | Testbench / Top | $400 \times 16\text{-bit}$ | 400 | 6,400 | 800 B | 20×20 normalized input image |
| **Conv1 Weight ROM** | `conv1_rom.txt` | $36 \times 16\text{-bit}$ | 36 | 576 | 72 B | 4 filters $\times$ 9 spatial taps |
| **Conv2 Weight ROM** | `conv2_rom.txt` | $288 \times 16\text{-bit}$ | 288 | 4,608 | 576 B | 8 filters $\times$ 4 input ch $\times$ 9 taps |
| **MLP Systolic ROM** | `mlp_rom.txt` | $992 \times 256\text{-bit}$ | 15,872 | 253,952 | 31.74 KB | 62 tiles $\times$ 16 rows $\times$ 16 weights |
| **Conv1 Line Buffer** | `window_gen.v` | $47 \times 16\text{-bit}$ | 47 | 752 | 94 B | Shift-register chain `sr[0..46]` |
| **Conv2 Line Buffers** | `conv2_window_gen.v`| $4 \times (27 \times 16\text{-bit})$ | 108 | 1,728 | 216 B | 4-channel shift registers |
| **Ping-Pong RAM A** | `mlp_head.v` | $208 \times 16\text{-bit}$ | 208 | 3,328 | 416 B | Layer 1 inputs & Layer 2 outputs |
| **Ping-Pong RAM B** | `mlp_head.v` | $64 \times 16\text{-bit}$ | 64 | 1,024 | 128 B | Layer 1 outputs & Layer 2 inputs |
| **TOTAL ON-CHIP STORAGE** | — | — | **16,623 words** | **265,968 bits** | **32.47 KB** | Fully synthesizable on block RAM |

---

## 9. Verification Suite & Essential Commands

### 9.1 Run All 13 Verilog Unit Testbenches
```cmd
run_all_tests.bat
```
*Expected Output:* `TESTBENCH RUNNER SUMMARY: 13 PASSED, 0 FAILED (100% Pass Rate)`

### 9.2 Run 10-Image Top-Level Hardware Regression
```cmd
cd v2\regression
python test_10.py
```
*Expected Output:* `FINAL SCORECARD: 10/10 PASSED (100.0% Hardware Accuracy), Mean Cycles = 9116.0`

### 9.3 Run Fast 10,000-Image Q7.8 Software Emulator
```cmd
cd v2\regression
python harness_emu_new_head.py
```
*Expected Output:* `10,000 images evaluated in ~18 seconds; Accuracy = 98.70% (9,870 / 10,000 correct)`

### 9.4 Run Full 10,000-Image Parallel Hardware RTL Regression
```cmd
cd v2\regression
python harness.py --workers 16
```
*Expected Output:* `Total Images: 10000 | RTL Accuracy: 0.9870 | RTL vs Emu Mismatches: 0 | Cycles Mean: 9116.0`

### 9.5 Automated Report QA Check
```cmd
python docs\review\build\check_report.py
```
*Expected Output:* `>> ALL QUALITY ASSURANCE CHECKS PASSED SUCCESSFULLY! <<`

### 9.6 View Simulation Waveforms in GTKWave
```cmd
gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_full.gtkw
```

---

## 10. Full-Stack Interactive Web GUI

The repository includes a modern web-based demonstration portal:
- **Frontend:** React 19, TypeScript, Vite 8, Lucide Icons, Canvas Drawing API, CSS Modules.
- **Backend:** FastAPI, Python 3.10+, Uvicorn, Asynchronous subprocess execution (`asyncio.to_thread`).

### Start Application Services (All-in-One)
```cmd
run_v2_ui.bat
```
Or start independently:
```cmd
# Terminal 1: Backend
cd v2\v2_ui\backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd v2\v2_ui\frontend
npm run dev
```
Navigate to `http://localhost:5173` to draw digits on the canvas and view live cycle traces, feature map activations, and FSM step transitions.

---

## 11. Viva Voce Defense & Project Documentation Links

- **[Comprehensive Viva Voce Preparation Guide (`docs/viva/VIVA_PREPARATION.md`)](docs/viva/VIVA_PREPARATION.md)**: 30+ questions and bulletproof model answers covering digital logic, fixed-point quantization, systolic array dataflow, timing derivations, and professor trap questions.
- **[Individual Team Portfolios & Defense Profiles (`docs/viva/TEAM_PORTFOLIO.md`)](docs/viva/TEAM_PORTFOLIO.md)**: Individual student contribution portfolios for Shreyansh Raj, Sarthak Bhowmik, Shaurya Singh, and Shreya Anand.
- **[Canonical End Semester Assessment Final Report (PDF, 46 Pages)](DLCD_Final_Project_Report_UE25CS251A.pdf)**: Complete academic submission document including mathematical derivations, RTL schematics, waveform timing diagrams, and IEEE bibliography.
- **[Single Source of Truth Facts (`docs/review/facts.json`)](docs/review/facts.json)**: Machine-readable JSON database of all verified measurements and metrics.

---

## 12. Repository Directory Structure

```
DLCD_Neural_Accelerator/
├── README.md                          # Master project manual (this file)
├── CURRENT_STATE.md                   # Formal verified repository status
├── run_all_tests.bat                  # Canonical automated testbench runner (13 testbenches)
├── run_v2_ui.bat                      # Full-stack launcher for backend + frontend
├── DLCD_Final_Project_Report_UE25CS251A.docx # ESA Mini-Project Report (Word DOCX)
├── DLCD_Final_Project_Report_UE25CS251A.pdf  # ESA Mini-Project Report (46 pages PDF)
├── docs/
│   ├── viva/
│   │   ├── VIVA_PREPARATION.md        # Comprehensive 30+ Viva Voce questions & model answers
│   │   └── TEAM_PORTFOLIO.md          # Individual team member portfolios & defense profiles
│   └── review/
│       ├── facts.json                 # Single source of truth for all verified numbers
│       ├── confusion_matrix.png       # 10x10 confusion matrix over 10,000 MNIST test images
│       ├── confusion_matrix.csv       # Confusion matrix raw numerical counts
│       ├── figures/                   # 300 DPI architectural figures (Fig 2.1 to 3.3, 7.4)
│       ├── screenshots/               # High-resolution terminal and GTKWave screenshots
│       └── wave/
│           ├── wave.vcd               # Complete 9,116-cycle simulation waveform artifact
│           ├── wave_full.gtkw         # Top-level full inference overview GTKWave save
│           ├── wave_conv1_mac.gtkw    # Conv1 window & MAC tap sequencing GTKWave save
│           ├── wave_mlp_fsm.gtkw      # MLP Head systolic FSM state transitions GTKWave save
│           └── wave_end.gtkw          # Dense valid, argmax & done pulse GTKWave save
├── v2/
│   ├── verilog_src/                   # Active synthesizable Verilog-2001 RTL modules
│   │   ├── v2_top.v                   # Master top-level chip integration
│   │   ├── window_gen.v               # 47-sr line buffer & 3x3 receptive window
│   │   ├── conv_pe.v                  # 9-tap sequential MAC unit (modulo-9 counter)
│   │   ├── mac_q7_8.v                 # Signed 16x16 Q7.8 MAC (product[23:8])
│   │   ├── conv1_array.v              # Conv1 4-channel controller (6-state FSM)
│   │   ├── maxpool_pe.v               # Fused 2x2 maxpool + ReLU comparator tournament
│   │   ├── maxpool_array.v            # 4-channel MaxPool1 array
│   │   ├── relu_q7_8.v                # Non-negative zero-clamping activation
│   │   ├── conv2_window_gen.v         # Conv2 4-channel line buffers
│   │   ├── conv2_pe.v                 # Conv2 4-channel parallel PE (4 MACs)
│   │   ├── conv2_array.v              # Conv2 8-filter controller (6-state FSM)
│   │   ├── maxpool2_array.v           # 8-channel MaxPool2 array
│   │   ├── mlp_head.v                 # Time-multiplexed MLP head (4-state FSM)
│   │   ├── systolic_array.v           # 16x16 2D mesh of processing elements
│   │   ├── systolic_pe.v              # Weight-stationary systolic PE
│   │   └── argmax.v                   # 4-level tournament comparator tree
│   ├── regression/                    # Automated regression & simulation testbenches
│   │   ├── test_10.py                 # Quick 10-image sanity regression test
│   │   ├── harness_emu_new_head.py    # Fast Q7.8 bit-exact software emulator harness
│   │   └── harness.py                 # Full 10,000-image parallel RTL simulation harness
│   └── v2_ui/
│       ├── backend/                   # FastAPI service for interactive inference
│       └── frontend/                  # React 19 + TypeScript + Vite interactive GUI
└── v1/                                # Version 1.0 Baseline MLP RTL, weights, and testbenches
```
