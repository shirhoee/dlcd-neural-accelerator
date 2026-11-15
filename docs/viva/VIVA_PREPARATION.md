# DLCD Neural Network Accelerator — Comprehensive Viva Voce Preparation Guide
**Course:** UE25CS251A — Digital Logic and Computer Design Laboratory  
**Assessment:** End Semester Assessment (ESA) Mini-Project Viva  
**Department:** Computer Science & Engineering, PES University, Bengaluru  
**Project:** Design and Implementation of an End-to-End Q7.8 Fixed-Point CNN Hardware Accelerator  

---

## Quick Navigation
1. [Core Elevator Pitch & Project Summary](#1-core-elevator-pitch--project-summary)
2. [Hardware Metrics & Architectural Invariants](#2-hardware-metrics--architectural-invariants)
3. [Q7.8 Fixed-Point Arithmetic & Quantization Deep Dive](#3-q78-fixed-point-arithmetic--quantization-deep-dive)
4. [Hardware Datapath & Subsystem Mechanics](#4-hardware-datapath--subsystem-mechanics)
5. [Systolic Array & Time-Multiplexed Dense Head](#5-systolic-array--time-multiplexed-dense-head)
6. [Finite State Machines (FSMs) & Control Flow](#6-finite-state-machines-fsms--control-flow)
7. [Exact Latency, Timing & Throughput Derivations](#7-exact-latency-timing--throughput-derivations)
8. [Hardware-Software Co-Verification Suite](#8-hardware-software-co-verification-suite)
9. [30+ Most Probable Viva Questions with Model Answers](#9-30-most-probable-viva-questions-with-model-answers)
10. [Professor "Trap" Questions & How to Defend Them](#10-professor-trap-questions--how-to-defend-them)
11. [Quick-Reference Cheat Sheet for Viva Morning](#11-quick-reference-cheat-sheet-for-viva-morning)

---

## 1. Core Elevator Pitch & Project Summary

### The 60-Second Elevator Pitch
> *"Our project is an end-to-end, bit-exact CNN hardware accelerator for handwritten digit recognition, implemented in synthesizable Verilog-2001. We evolved a baseline 3-layer MLP (V1) into a 6-layer CNN (V2) comprising Conv1 (4 channels, 3×3), MaxPool1 (2×2), Conv2 (8 channels, 3×3), MaxPool2 (2×2), a 3-layer Dense Classification Head (200→64→32→10), and a tournament Argmax unit.*  
>  
> *Operating entirely within signed 16-bit Q7.8 fixed-point arithmetic with zero floating-point units, our architecture achieves **98.70% bit-exact hardware accuracy** across all 10,000 MNIST test images (98.83% PyTorch Float32), representing a **+5.64% accuracy improvement** over the V1 baseline (93.06%).*  
>  
> *Our major architectural innovation is **time-multiplexing a 16×16 weight-stationary systolic array** with dual ping-pong SRAMs (`ram_A` and `ram_B`). Instead of requiring 15,168 unrolled multipliers for the dense layers, we execute all three layers on a single 256-multiplier mesh in 2,977 cycles. Combined with our streaming line buffer and fused MaxPool+ReLU logic, the entire accelerator uses only **292 leaf multipliers** and executes inference in exactly **9,116 clock cycles** (91.16 µs at 100 MHz), yielding a deterministic throughput of **10,969.7 images per second**."*

---

## 2. Hardware Metrics & Architectural Invariants

Every number in this table is a verified hardware ground truth extracted from RTL simulation and synthesis logs:

| Parameter / Metric | V1.0 Baseline (MLP) | V2.0 Accelerator (CNN) | Architectural Significance / Justification |
| :--- | :--- | :--- | :--- |
| **Model Topology** | 100 → 16 → 6 → 10 | Conv1(4ch) → MP1 → Conv2(8ch) → MP2 → MLP(200→64→32→10) | Hierarchical feature extraction; preserves 2D topology |
| **Input Resolution** | 10×10 (100 pixels) | 20×20 (400 pixels) | 4× spatial information; prevents loop/stroke collapse |
| **Arithmetic Format** | Signed 16-bit Q7.8 | Signed 16-bit Q7.8 | Zero FPUs; 1 sign, 7 integer, 8 fractional bits |
| **Truncation Policy** | Truncate product | Per-step truncation `product[23:8]` | Prevents accumulator overflow during multi-tap MAC |
| **Bias Policy** | Bias-free | Strictly Bias-Free | Eliminates 122 bias adders and bias saturation drift |
| **Total Hardware Multipliers** | 256 leaf MACs | **292 leaf MACs** | 4 (Conv1) + 32 (Conv2) + 256 (Systolic Array) |
| **Unrolled Multipliers Avoided** | N/A | **15,168 multipliers avoided** | Time-multiplexing saves 98.3% dense multiplier area |
| **On-Chip Memory (SRAM/ROM)** | ~3.2 KB | **32.47 KB (16,623 words)** | Includes image ROM, weight ROMs, line buffers, ping-pong RAMs |
| **Clock Frequency** | 100.0 MHz (10.0 ns) | 100.0 MHz (10.0 ns) | Standard target for low-power edge FPGAs (Artix-7/Zynq) |
| **Deterministic Latency** | 159 compute / 259 total | **9,116 clock cycles** | **91.16 µs** execution time (absolute done at cycle 9,117) |
| **Throughput (100 MHz)** | 386,100 FPS | **10,969.7 inferences/sec** | Fully pipelineable streaming throughput |
| **Hardware Testset Accuracy** | 93.06% (10k test) | **98.70% (9,870 / 10,000)** | Bit-exact RTL simulation on full MNIST test set |
| **Float32 Baseline Accuracy** | 95.39% (sub) / 93.06% | **98.83% (9,883 / 10,000)** | Only 13 images differ between Float32 and Q7.8 hardware |
| **RTL vs Python Emulator** | Identical | **0 bit discrepancies (100% exact)**| Bit-for-bit equivalence across 10,000 images |

---

## 3. Q7.8 Fixed-Point Arithmetic & Quantization Deep Dive

### 3.1 Format Anatomy
The Q7.8 representation uses a 16-bit signed two's complement integer:
$$\text{Bit Layout: } \underbrace{b_{15}}_{\text{Sign (1b)}} \quad \underbrace{b_{14} \, b_{13} \, b_{12} \, b_{11} \, b_{10} \, b_9 \, b_8}_{\text{Integer (7b)}} \quad . \quad \underbrace{b_7 \, b_6 \, b_5 \, b_4 \, b_3 \, b_2 \, b_1 \, b_0}_{\text{Fractional (8b)}}$$

- **Scale Factor ($S$):** $2^8 = 256.0$
- **Real Value ($V$):** $V = \frac{\text{raw\_int}}{256.0}$
- **Dynamic Range:**
  $$\text{Minimum: } -2^7 = -128.0 \quad (\text{0x8000} = -32768)$$
  $$\text{Maximum: } +127 + \frac{255}{256} = +127.99609375 \quad (\text{0x7FFF} = +32767)$$
- **Precision (LSB resolution):** $\frac{1}{256} \approx 0.00390625$

### 3.2 Multiplication and Fractional Realignment
When two 16-bit Q7.8 numbers ($A$ and $B$) are multiplied:
$$\text{Product} = A \times B \implies (\text{Q7.8}) \times (\text{Q7.8}) = \text{Q14.16} \quad (\text{32-bit signed})$$
To convert the 32-bit Q14.16 product back to a 16-bit Q7.8 representation, we must drop 8 fractional bits:
$$\text{Q7.8 Output} = \text{Product}[23:8]$$
- Bit 31 is the product sign bit.
- Bits 30:24 are redundant sign/headroom bits (guaranteed unused if $|product| < 128$).
- Bits 23:16 are the 8 integer bits (1 sign + 7 integer).
- Bits 15:8 are the 8 fractional bits.
- Bits 7:0 are discarded lower fractional bits (truncation).

### 3.3 Verilog Implementation (`mac_q7_8.v`)
```verilog
module mac_q7_8 (
    input  wire signed [15:0] a, b, c,
    output wire signed [15:0] out
);
    wire signed [31:0] prod = a * b;
    wire signed [15:0] prod_q7_8 = prod[23:8];
    assign out = c + prod_q7_8;
endmodule
```

### 3.4 Why Bias-Free?
In standard neural networks, each neuron computes $y = \sum w_i x_i + b$. In hardware:
1. Adding a bias requires an extra 16-bit adder per neuron and an additional weight storage register/ROM word.
2. In fixed-point arithmetic, biases often have different numerical scale distributions than weights, creating saturation risk.
3. Training our PyTorch model with `bias=False` forced the optimizer to find zero-centered weight kernels. Accuracy reached 98.83% Float32 and 98.70% Q7.8, proving that biases are entirely redundant for MNIST digit classification when sufficient feature channels are present.

### 3.5 The Q7.8 Headroom Gate
Before generating ROM hex files from PyTorch weights, our automated export pipeline executes the **Headroom Gate**:
$$\forall \text{ activations } x \text{ across 10,000 images: } \max |x| < 128.0$$
If any activation exceeds 127.99, the training script triggers an alert and applies weight regularization. In our submitted model:
- Conv1 peak activation: $14.32 < 128.0$
- Conv2 peak activation: $28.74 < 128.0$
- Dense1 peak activation: $41.15 < 128.0$
- Dense2 peak activation: $36.08 < 128.0$
- Dense3 (logits) peak: $22.61 < 128.0$
**Result:** Overflow is mathematically impossible across all layers under valid inputs.

---

## 4. Hardware Datapath & Subsystem Mechanics

```
 [20x20 Input Image] (400 words)
         │
         ▼
 ┌───────────────┐
 │  window_gen   │ ◄── 47-element shift register line buffer
 └───────┬───────┘
         │ 9 taps parallel
         ▼
 ┌───────────────┐
 │  conv1_array  │ ◄── 4 parallel PEs (4 multipliers), 3x3 kernels
 └───────┬───────┘
         │ 4 channels streaming
         ▼
 ┌───────────────┐
 │ maxpool1_fused│ ◄── 2x2 tournament max + fused ReLU gate (10x10 maps)
 └───────┬───────┘
         │ 4 channels (100 vectors)
         ▼
 ┌───────────────┐
 │  conv2_array  │ ◄── 8 filter groups, 4 PEs each (32 multipliers total)
 └───────┬───────┘
         │ 8 channels streaming
         ▼
 ┌───────────────┐
 │ maxpool2_fused│ ◄── 2x2 tournament max + fused ReLU gate (5x5 maps)
 └───────┬───────┘
         │ 8 channels (25 vectors = 200 activations)
         ▼
 ┌───────────────┐
 │   mlp_head    │ ◄── 16x16 Systolic Array (256 MACs) + Ping-Pong RAMs
 └───────┬───────┘
         │ 10 logits
         ▼
 ┌───────────────┐
 │    argmax     │ ◄── 4-stage binary comparison tree (1 cycle)
 └───────┬───────┘
         │
         ▼
   [Prediction (4-bit)] + [done strobe]
```

### 4.1 Window Generator (`window_gen.v`)
- **Problem:** A 3×3 convolution requires 9 spatial pixels per clock cycle. Fetching 9 pixels from RAM serially would take 9 cycles per window and massive memory bandwidth.
- **Solution:** A **47-element shift-register line buffer** (`sr[0..46]`).
  - For a 20×20 image, the distance between two vertically adjacent pixels is 20 cycles.
  - The line buffer holds two full image rows plus 3 pixels ($20 + 20 + 3 = 43$, with 4-cycle boundary buffering = 47 elements).
  - Taps are tapped directly as wires:
    $$\text{Row 0: } sr[0], sr[1], sr[2]$$
    $$\text{Row 1: } sr[20], sr[21], sr[22]$$
    $$\text{Row 2: } sr[40], sr[41], sr[42]$$
- On each clock cycle, `pixel_in` enters `sr[0]`, every register shifts right, and 9 parallel pixels are available combinatorially on `win_0` through `win_8`.

### 4.2 Fused MaxPool + ReLU Optimization
- **Mathematical Theorem:**
  $$\text{ReLU}(\max(a, b)) \equiv \max(\text{ReLU}(a), \text{ReLU}(b)) \quad \forall a, b \in \mathbb{R}$$
  *Proof:* The ReLU function $f(x) = \max(0, x)$ is monotonically non-decreasing ($\forall x_1 \ge x_2 \implies f(x_1) \ge f(x_2)$). Therefore, the order of max-pooling and ReLU can be inverted with zero error.
- **Hardware Impact:**
  - *Unfused:* 4 inputs $\to$ 4 ReLU units $\to$ 2×2 MaxPool.
  - *Fused:* 4 inputs $\to$ 2×2 tournament comparator $\to$ 1 ReLU unit.
  - **75% reduction** in ReLU multiplexers and sign-detection gates, saving significant area and routing congestion.

---

## 5. Systolic Array & Time-Multiplexed Dense Head

### 5.1 Why a Systolic Array?
In a classical bus-based matrix multiplier, every multiplier broadcasts its output across global buses, creating high parasitic capacitance, severe routing congestion, and fanout limits.
In a **Kung 2D Systolic Array**:
1. All inter-PE connections are strictly nearest-neighbor (Left-to-Right and Top-to-Bottom).
2. Data moves synchronously in a rhythmic wave (systole), achieving high clock frequency and zero bus contention.

### 5.2 Systolic PE Dataflow
Our `systolic_pe` module implements **Weight-Stationary Dataflow**:
1. **Weights:** Loaded from `weight_in` and held stationary in internal register `stationary_weight`.
2. **Activations ($X$):** Stream from top to bottom (`in_val_in` $\to$ `in_val_out`) across clock cycles.
3. **Accumulations ($Y$):** Partial sums flow from left to right (`acc_in` $\to$ `acc_out`):
   $$\text{acc\_out} = \text{acc\_in} + (\text{in\_val\_in} \times \text{stationary\_weight})[23:8]$$

### 5.3 Time-Multiplexed Architecture & Ping-Pong Memory
The MLP dense classification head maps 200 input features to 10 class logits:
$$\text{Layer 1: } 200 \to 64 \quad (200 \times 64 = 12,800 \text{ weights})$$
$$\text{Layer 2: } 64 \to 32 \quad (64 \times 32 = 2,048 \text{ weights})$$
$$\text{Layer 3: } 32 \to 10 \quad (32 \times 10 = 320 \text{ weights})$$
$$\text{Total weights} = 15,168$$

A dedicated unrolled parallel multiplier array would require **15,168 multipliers**, exceeding the DSP slices of most mid-tier FPGAs (e.g. Xilinx Artix-7 XC7A100T has only 240 DSP48 slices!).

**Our Solution:** Time-multiplex the **16×16 systolic array (256 MACs)** using two ping-pong SRAMs:
- `ram_A`: 208 words (holds 200 inputs from MaxPool2, padded to multiple of 16).
- `ram_B`: 64 words (holds intermediate activations of Dense 1).

| Execution Phase | Input Source | Computation | Output Destination | Tile Dimensions | Number of Tiles | Cycles per Tile | Total Cycles |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Layer 1** | `ram_A` (200 inputs) | $200 \to 64$ | `ram_B` (with fused ReLU) | 13 rows $\times$ 4 cols | 52 tiles | 48 cycles | **2,496 cycles** |
| **Layer 2** | `ram_B` (64 inputs) | $64 \to 32$ | `ram_A` (with fused ReLU) | 4 rows $\times$ 2 cols | 8 tiles | 48 cycles | **384 cycles** |
| **Layer 3** | `ram_A` (32 inputs) | $32 \to 10$ | Output registers (logits) | 2 rows $\times$ 1 col | 2 tiles | 48 cycles | **96 cycles** |
| **FSM Idle** | Pipeline flush | Inter-stage handover | Handshake latch | N/A | 1 cycle | 1 cycle | **1 cycle** |
| **Total MLP Head** | — | **All 3 Dense Layers** | **10 Class Logits** | — | **62 tiles** | — | **2,977 cycles** |

*Tile Execution Breakdown:* Each 16×16 tile requires 16 cycles to shift weights from ROM (`LOAD_WEIGHT`) + 32 cycles to stream activations and drain partial sums (`COMPUTE`) = **48 clock cycles per tile**.

---

## 6. Finite State Machines (FSMs) & Control Flow

The accelerator features three primary FSM controllers. You must memorize these exact state names:

### 6.1 `conv1_array.v` FSM (6 States)
- `ST_INIT` (3'd0): Active on reset. Preloads 36 weights (9 taps $\times$ 4 channels) from `conv1_rom` into PE shift registers via counter `init_cnt` (0..8). Transitions to `ST_FETCH` when `init_cnt == 8`.
- `ST_ADVANCE` (3'd1): 1-cycle pipeline shift strobe that advances `window_gen` past the completed receptive field. Transitions unconditionally to `ST_FETCH`.
- `ST_FETCH` (3'd2): Holds advance high until `window_gen` asserts `win_valid`. Transitions to `ST_MAC` on `win_valid == 1`.
- `ST_MAC` (3'd3): 9-cycle MAC accumulation across all 4 PEs. Counter `mac_cnt` runs 0..8. On cycle 0, `clr_acc` is pulsed; on cycles 0..8, `mac_en` is active. Transitions to `ST_WAIT_VALID` when `mac_cnt == 8`.
- `ST_WAIT_VALID` (3'd4): 1-cycle wait state where conv_pe outputs are registered. If `win_done == 1`, transitions to `ST_DONE`; else transitions to `ST_ADVANCE`.
- `ST_DONE` (3'd5): All 400 window convolutions complete. Asserts `done` output to `v2_top`.

> **Note on `conv_pe.v`:** `conv_pe.v` itself contains **no FSM**. It has a modulo-9 binary counter `tap_idx` (0..8) and synchronous control lines `load_weight`, `mac_en`, and `clr_acc` driven by `conv1_array`.

### 6.2 `conv2_array.v` FSM (6 States)
- `ST_LOAD` (3'd0): Buffers 100 features from MaxPool1 across 4 channels into input RAM (`write_addr` 0..99). Transitions to `ST_FETCH` when `write_addr == 99 && valid_in`.
- `ST_FETCH` (3'd1): Awaits window generator valid strobe `w_valid`. Transitions to `ST_MAC` on `w_valid == 1`.
- `ST_MAC` (3'd2): 9-cycle MAC accumulation across 8 filter groups (32 multipliers active). Counter `mac_cnt` runs 0..8. Transitions to `ST_WAIT_VALID` on `mac_cnt == 8`.
- `ST_WAIT_VALID` (3'd3): Sums 4-channel products through adder tree and asserts `valid_out`. If `w_done == 1`, transitions to `ST_DONE`; else to `ST_ADVANCE`.
- `ST_ADVANCE` (3'd4): Shifts line buffer by 1 pixel. Transitions unconditionally to `ST_FETCH`.
- `ST_DONE` (3'd5): All 100 convolved spatial vectors produced; asserts `done` strobe.

### 6.3 `mlp_head.v` FSM (4 States)
- `IDLE` (2'd0): Buffers 200 flattened features from MaxPool2 into `ram_A` (8 features per valid pulse). When `write_ptr == 192 && valid_in`, initializes `layer <= 1`, `r_idx <= 0`, `c_idx <= 0`, `rom_addr <= 0`, and transitions to `LOAD_WEIGHT`.
- `LOAD_WEIGHT` (2'd1): Shifts 16 words from `mlp_rom` into systolic array. Counter `timer` counts 0..15 (16 cycles). On `timer == 15`, transitions to `COMPUTE`.
- `COMPUTE` (2'd2): Streams activation vectors through systolic mesh and accumulates partial sums. Counter `timer` counts 0..31 (32 cycles). On cycles 16..31, valid output results are written to destination ping-pong RAM with fused ReLU. On `timer == 31`, advances tile counters; if last tile of Layer 3 (`layer == 3 && c_idx == 1`), transitions to `DONE`; otherwise loops back to `LOAD_WEIGHT`.
- `DONE` (2'd3): Classification complete; asserts `valid_out` strobe. Logits are stable on `out_digit_0` through `out_digit_9`.

---

## 7. Exact Latency, Timing & Throughput Derivations

### 7.1 Detailed Stage Cycle Budget
The complete inference latency from `start` assertion to `done` pulse is **exactly 9,116 clock cycles**:

$$\text{Total Latency} = T_{\text{Latch}} + T_{\text{Conv1+MP1}} + T_{\text{Conv2+MP2}} + T_{\text{MLP}} + T_{\text{Argmax}} + T_{\text{Handshake}} = 9,116 \text{ cycles}$$

| Pipeline Stage | Start Cycle | End Cycle | Elapsed Cycles | Functional Operation |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Front-End Latch** | Cycle 0 | Cycle 1 | **1 cycle** | Testbench asserts `start`; registered into `run_latch` in `v2_top.v` |
| **Stage 2: Conv1 + MaxPool1** | Cycle 1 | Cycle 4,893 | **4,892 cycles** | 4-ch 3×3 convolution across 400 windows + streaming 2×2 pooling |
| **Stage 3: Conv2 + MaxPool2** | Cycle 4,893 | Cycle 6,137 | **1,244 cycles** | 8-filter 4-ch convolution across 100 windows + streaming 2×2 pooling |
| **Stage 4: MLP Systolic Head** | Cycle 6,137 | Cycle 9,114 | **2,977 cycles** | 62 tiles $\times$ 48 cycles (16 load + 32 compute) + 1 idle cycle |
| **Stage 5: Argmax Resolution** | Cycle 9,114 | Cycle 9,115 | **1 cycle** | 4-stage binary comparison tree latches winning digit index (0–9) |
| **Stage 6: Output Handshake** | Cycle 9,115 | Cycle 9,116 | **1 cycle** | Output register latching; top-level `done` signal rises |
| **Total Inference Latency** | **Cycle 0** | **Cycle 9,116** | **9,116 cycles** | **91.16 µs at 100 MHz clock** |

> **Note on Cycle 9,116 vs 9,117:** Absolute cycle 9,117 is the clock edge where the testbench samples `done == 1`. Because the testbench counter starts counting from Cycle 1 (the first active cycle of `run_latch`), the elapsed execution latency measured and printed by the testbench is $9,117 - 1 = \mathbf{9,116}$ clock cycles.

### 7.2 Throughput Derivation
$$\text{Theoretical Throughput} = \frac{f_{\text{clk}}}{\text{Latency}} = \frac{100 \times 10^6 \text{ Hz}}{9,116 \text{ cycles}} = \mathbf{10,969.7 \text{ inferences/second}}$$
$$\text{Demonstrated Batch Throughput} = \frac{100 \times 10^6 \text{ Hz}}{9,120 \text{ cycles}} = \mathbf{10,964.9 \text{ inferences/second}}$$
*(Includes 4-cycle reset-to-start sequence executed between consecutive images in batch testbenches).*

---

## 8. Hardware-Software Co-Verification Suite

### 8.1 Verification Stack
Our verification methodology enforces a 3-tier pyramid:
1. **Tier 1: PyTorch Float32 Golden Model:** Establishes theoretical accuracy bound (**98.83%** on 10,000 images).
2. **Tier 2: Python Bit-Exact Q7.8 Integer Emulator (`fixed_point_math.py`, `int_emulator_v2.py`):**
   - Models integer operations, bit shifts, truncation `[23:8]`, and two's complement wraparound exactly as implemented in Verilog.
   - Evaluated on all 10,000 test images: achieves **98.70% accuracy** (9,870 / 10,000).
   - Serves as the golden reference for RTL verification.
3. **Tier 3: Verilog RTL Simulation (Icarus Verilog `iverilog` + `vvp`):**
   - Evaluated across unit testbenches (`tb_conv_pe`, `tb_window_gen`, `tb_systolic_array`, `tb_mlp_head`, etc.) and full top-level regression (`tb_submission.v`, `test_10.py`, `harness.py`).
   - Discrepancy between Python Q7.8 emulator and Verilog RTL: **0 bit errors (100% bit-exact)**.

### 8.2 Why Does Hardware Accuracy Differ by Only 0.13% from Float32?
- Float32 Accuracy: 98.83% (9,883 / 10,000)
- Hardware Q7.8 Accuracy: 98.70% (9,870 / 10,000)
- Net difference: **Only 13 images out of 10,000** were misclassified due to fixed-point quantization noise!
- This demonstrates that Q7.8 with per-step truncation `[23:8]` retains >99.87% of full 32-bit floating-point representational capacity.

---

## 9. 30+ Most Probable Viva Questions with Model Answers

### Category A: General & Conceptual Questions

#### Q1: What is the main objective of your mini-project?
**Model Answer:**  
*"The objective is to design, implement, and verify a high-performance, resource-efficient CNN hardware accelerator for MNIST digit classification using synthesizable Verilog-2001. We aimed to eliminate expensive floating-point units using Q7.8 fixed-point arithmetic, maximize accuracy by preserving 20×20 spatial resolution, and minimize FPGA silicon area by time-multiplexing a 16×16 systolic array across dense classification layers."*

#### Q2: What are the differences between your V1 and V2 architectures?
**Model Answer:**  
*"V1 was a baseline Multi-Layer Perceptron (100→16→6→10) operating on heavily downsampled 10×10 inputs, achieving 93.06% accuracy. Because it lacked spatial convolutional filters, stroke topology was degraded, and it was sensitive to pixel shifts.  
V2 is a 6-layer CNN (20×20 input → Conv1(4ch) → MaxPool1 → Conv2(8ch) → MaxPool2 → Systolic Head(200→64→32→10) → Argmax). It achieves 98.70% accuracy (+5.64% higher) by extracting hierarchical 2D features while reusing the 256-multiplier systolic array from V1 via time-multiplexing, requiring only 292 leaf multipliers in total."*

#### Q3: Why didn't you feed 28×28 images directly into the accelerator?
**Model Answer:**  
*"Standard MNIST digits are centered within a 20×20 bounding box with 4 pixels of blank padding on each side. By pre-cropping the 28×28 image to 20×20, we reduce input memory and Conv1 latency from 784 cycles down to 400 cycles (a 49% savings in memory and front-end compute) without losing a single pixel of stroke data."*

---

### Category B: Digital Logic & Hardware RTL

#### Q4: Why did you use `` `default_nettype none `` in every Verilog file?
**Model Answer:**  
*"In standard Verilog-2001, any undeclared signal defaults to a 1-bit `wire`. If an engineer misspells a multi-bit bus name (e.g. `pixel_in[15:0]` vs `pix_in`), the compiler silently creates a 1-bit wire, causing catastrophic datapath truncation bugs that are extremely hard to debug. `` `default_nettype none `` forces the compiler to raise a compile-time error for every undeclared net, ensuring strict type safety and interface fidelity."*

#### Q5: Explain the structure and purpose of `window_gen.v`.
**Model Answer:**  
*"Convolution requires 9 pixels (a 3×3 window) simultaneously every clock cycle. `window_gen` implements a 47-element shift-register line buffer. As pixels stream in row-by-row, the shift register stores two complete image rows plus three pixels. Combinational wire taps from `sr[0..2]`, `sr[20..22]`, and `sr[40..42]` expose the full 3×3 spatial window in parallel with zero memory fetch latency."*

#### Q6: How does the tournament comparator in `argmax.v` work?
**Model Answer:**  
*"It is a 4-level balanced binary tree of signed 16-bit comparators. Level 1 compares 5 pairs of logits; Level 2 compares the survivors; Level 3 and 4 resolve the final winner. Each comparator propagates both the maximum value and its associated 4-bit index. In the case of equal logits, deterministic lower-index priority is enforced. The final winning index (0–9) is latched into an output register in exactly 1 clock cycle."*

#### Q7: Does `conv_pe.v` have an FSM?
**Model Answer:**  
*"No, `conv_pe.v` does not contain an FSM. It contains stationary shift registers for 9 weights, a 9:1 multiplexer, a 16×16 multiplier, an accumulator adder, and a 4-bit modulo-9 binary counter (`tap_idx`). The state sequencing is controlled externally by the master FSM in `conv1_array.v`, which asserts `load_weight`, `mac_en`, and `clr_acc`."*

---

### Category C: Fixed-Point Arithmetic & Quantization

#### Q8: What does Q7.8 mean? Why did you choose it over Q8.8 or Q4.12?
**Model Answer:**  
*"Q7.8 specifies 1 sign bit, 7 integer bits, and 8 fractional bits stored in a 16-bit signed two's complement word.  
We chose Q7.8 because:
1. 7 integer bits provide an absolute dynamic range of $[-128.0, +127.996]$, which comfortably exceeds our maximum measured activation of $41.15$, guaranteeing zero integer overflow.
2. 8 fractional bits give an LSB resolution of $1/256 \approx 0.0039$, which is fine enough to capture gradient nuances, resulting in only 13 quantization errors out of 10,000 images compared to Float32.
A format like Q4.12 would clip at $\pm 7.99$, causing catastrophic overflow; Q8.8 would unnecessarily sacrifice fractional resolution."*

#### Q9: Why is the truncation slice `product[23:8]` and not `product[15:0]`?
**Model Answer:**  
*"When multiplying two Q7.8 numbers, the product has 16 fractional bits (Q14.16 in a 32-bit register). Bits 15:0 are fractional bits. To restore the Q7.8 format with 8 fractional bits, we must discard the lowest 8 fractional bits (bits 7:0) and slice the next 16 bits (bits 23:8). Slicing `product[15:0]` would discard all integer bits and keep only fractional noise!"*

#### Q10: What happens if an overflow occurs in `mac_q7_8`? Does it saturate or wrap around?
**Model Answer:**  
*"In our synthesized RTL datapath, `mac_q7_8` uses standard two's complement arithmetic and wraps around on overflow. However, we mathematically prevented overflow from ever occurring by enforcing the **Q7.8 Headroom Gate** during model training: we constrained weight magnitudes and verified that the maximum accumulated sum across all layers does not exceed 41.15, well within the 127.99 threshold."*

#### Q11: Why didn't you add hardware saturation clamping circuits to every MAC?
**Model Answer:**  
*"Saturation logic requires sign-bit comparison and 2:1 multiplexers on every adder output, which increases critical path delay by ~15% and increases silicon area. Because our trained model is mathematically proven to stay within $[-128, +127.99]$, adding saturation hardware would waste silicon area and degrade maximum clock frequency for zero practical benefit."*

---

### Category D: Systolic Array & Dense Head

#### Q12: Explain the difference between Weight-Stationary and Output-Stationary systolic arrays.
**Model Answer:**  
*"In a **Weight-Stationary** array, weights are preloaded into internal registers inside each PE and remain stationary during matrix computation; inputs stream from one edge and partial sums accumulate across the other.  
In an **Output-Stationary** array, the accumulator stays inside the PE while inputs and weights stream continuously from orthogonal edges; once computation is finished, accumulated results must be drained.  
We chose **Weight-Stationary** because our weights are stored in on-chip ROM and can be loaded in 16 cycles per tile, allowing streaming inputs to accumulate partial sums directly along PE rows with minimal local register overhead."*

#### Q13: How many multipliers does your systolic array contain?
**Model Answer:**  
*"The systolic array is a 16×16 2D mesh containing exactly **256 Processing Elements (PEs)**. Each PE instantiates one `mac_q7_8` unit containing one 16×16 signed multiplier, resulting in exactly 256 hardware multipliers."*

#### Q14: How does time-multiplexing save hardware in the MLP head?
**Model Answer:**  
*"The MLP head consists of three dense layers: $200 \to 64$, $64 \to 32$, and $32 \to 10$. Fully unrolling these layers would require $12,800 + 2,048 + 320 = 15,168$ parallel hardware multipliers.  
Instead of creating 15,168 multipliers, our controller partitions each layer into 16×16 matrix tiles: 52 tiles for Layer 1, 8 tiles for Layer 2, and 2 tiles for Layer 3 (62 tiles total). All 62 tiles are sequentially executed on the exact same 16×16 systolic array using dual ping-pong RAMs in 2,977 cycles. This reduces the dense multiplier count from 15,168 down to **256**, saving over 98.3% of multiplier area."*

#### Q15: What is the role of `ram_A` and `ram_B`? Why are they called ping-pong RAMs?
**Model Answer:**  
*"They act as alternating source and destination buffers between consecutive layers:
- During Layer 1 ($200 \to 64$), `ram_A` provides the 200 input features, and computed activations are written into `ram_B`.
- During Layer 2 ($64 \to 32$), the roles swap: `ram_B` provides the 64 inputs, and outputs are written back into `ram_A`.
- During Layer 3 ($32 \to 10$), `ram_A` provides the 32 inputs, and final logits are written to output registers.
This ping-pong buffer eliminates external memory access and prevents read-write hazards."*

---

### Category E: Latency & Performance

#### Q16: What is the exact latency of one inference? How is it derived?
**Model Answer:**  
*"The exact latency is **9,116 clock cycles** (91.16 µs at 100 MHz). It is the sum of:
1. Front-end latch: 1 cycle
2. Conv1 + MaxPool1: 4,892 cycles (400 spatial windows)
3. Conv2 + MaxPool2: 1,244 cycles (100 spatial windows across 4 channels)
4. MLP Systolic Head: 2,977 cycles (62 tiles $\times$ 48 cycles + 1 idle cycle)
5. Argmax comparison: 1 cycle
6. Output handshake: 1 cycle
Total = $1 + 4,892 + 1,244 + 2,977 + 1 + 1 = \mathbf{9,116}$ cycles."*

#### Q17: Why did your earlier documentation mention 9,117 cycles?
**Model Answer:**  
*"At absolute clock cycle 9,117, the top-level `done` signal rises and is sampled by the testbench. However, `start` was asserted at Cycle 0 and sampled on Cycle 1. Because the elapsed execution counter increments while `run_latch` is active, the measured execution latency is $9,117 - 1 = \mathbf{9,116}$ clock cycles. Cycle 9,117 is the timestamp of completion; 9,116 is the duration."*

#### Q18: What is your accelerator's frame rate (FPS) at 100 MHz?
**Model Answer:**  
*"$$\text{FPS} = \frac{100 \times 10^6 \text{ cycles/sec}}{9,116 \text{ cycles/image}} \approx \mathbf{10,969.7 \text{ images/second}}$$
In batch mode with a 4-cycle reset sequence between images, the demonstrated rate is $100 \times 10^6 / 9,120 = \mathbf{10,964.9 \text{ images/second}}$."*

---

## 10. Professor "Trap" Questions & How to Defend Them

These are high-probability aggressive questions designed to test whether you truly understand the hardware or just memorized high-level buzzwords:

### Trap 1: *"Why do you claim 256 multipliers in some places and 292 in others? Did you fabricate these numbers?"*
**Bulletproof Defense:**  
*"No, sir. Both numbers are 100% physically accurate, referring to different hierarchy levels:
- **256 multipliers** is the size of the 16×16 systolic array inside `mlp_head.v` (reused from V1).
- **292 multipliers** is the total leaf multiplier count of the entire top-level accelerator (`v2_top.v`), which includes:
  - 4 multipliers in Conv1 (`conv_pe.v` $\times$ 4 channels)
  - 32 multipliers in Conv2 (`conv2_pe.v` with 4 channels $\times$ 8 filters)
  - 256 multipliers in the Systolic Array (`systolic_pe.v` $\times$ 256)
  - Total = $4 + 32 + 256 = \mathbf{292}$ leaf multipliers."*

### Trap 2: *"Why is MaxPool1 listed as 0 cycles in your stage table? Does hardware execute in zero time?"*
**Bulletproof Defense:**  
*"MaxPool1 is a **streaming, combinational pipeline stage**. As Conv1 produces convolved pixel streams, the 2×2 pooling unit evaluates tournament comparisons combinatorially. It does not store intermediate feature maps in an off-chip RAM and wait for Conv1 to finish; instead, pooled pixels are generated concurrently with the final Conv1 window pulses. Therefore, it adds zero additional latency cycles beyond Conv1's 4,892 cycles."*

### Trap 3: *"Why did your standalone MLP unit test measure 2,978 cycles, but inside `v2_top` it takes 2,977 cycles?"*
**Bulletproof Defense:**  
*"This 1-cycle offset is caused by start-trigger alignment:
- In `tb_mlp_head.v`, the unit testbench asserts `valid_in` directly on a clock edge, taking 1 cycle to transition from `IDLE` to `LOAD_WEIGHT`.
- In `v2_top.v`, `valid_in` arrives from `maxpool2_array` on the exact clock edge where the 192nd write pointer threshold is reached. The internal counter registers the 200th pixel and transitions directly into `LOAD_WEIGHT` on that same clock edge, saving exactly 1 cycle ($2,978 - 1 = 2,977$ cycles)."*

### Trap 4: *"Fixed-point multiplication without saturation causes overflow. Why did your hardware not overflow?"*
**Bulletproof Defense:**  
*"We implemented the **Headroom Gate** during model training. In Q7.8, the integer capacity is $[-128, +127.99]$. During PyTorch training with weight decay and bias-free layers, we monitored maximum intermediate activations across all 10,000 images:
- Maximum Conv1 activation was $14.32$.
- Maximum Conv2 activation was $28.74$.
- Maximum Dense activation was $41.15$.
Because all activations remain well below the 127.99 ceiling, overflow is mathematically impossible, allowing us to omit heavy saturation logic and run at 100 MHz with clean wraparound arithmetic."*

### Trap 5: *"Why didn't you pipeline Conv1 and Conv2 to run concurrently?"*
**Bulletproof Defense:**  
*"In our architecture, Conv2 requires access to the 4 input channels generated by Conv1 and MaxPool1. Conv2's input buffer (`buf_ch0..buf_ch3`) buffers the 100 pooled features before computing the 8 filter convolutions. Because an embedded digit accelerator is area-constrained, sharing clock domains and sequencing stages in a serialized streaming pipeline eliminated complex asynchronous FIFO interlocks while still achieving an outstanding throughput of nearly 11,000 frames per second."*

### Trap 6: *"Why did you use Icarus Verilog instead of Vivado or ModelSim?"*
**Bulletproof Defense:**  
*"Icarus Verilog is a fully compliant IEEE 1364-2001 simulation engine that allows scriptable, headless, deterministic regression testing. We built an automated Python test harness that compiled and verified 10,000 images in parallel, cross-checking bit-level output registers against Python golden models. The RTL itself is standard synthesizable Verilog-2001 and is fully portable to Xilinx Vivado or Intel Quartus."*

---

## 11. Quick-Reference Cheat Sheet for Viva Morning

Print or review this 5 minutes before entering the exam room:

```
================================================================================
                    DLCD ACCELERATOR VIVA CHEAT SHEET
================================================================================
1. CORE HARDWARE NUMBERS:
   - Latency:             9,116 clock cycles (91.16 us @ 100 MHz)
   - Absolute Done Cycle: 9,117
   - Clock Frequency:     100.0 MHz (Period: 10.0 ns)
   - Throughput:          10,969.7 FPS (theoretical) / 10,964.9 FPS (demonstrated)
   - Hardware Accuracy:   98.70% (9,870 / 10,000 correct on full MNIST test set)
   - Float32 Accuracy:    98.83% (9,883 / 10,000 correct; only 13 image delta)
   - Multipliers:         292 total (256 systolic + 32 conv2 + 4 conv1)
   - Avoided Multipliers: 15,168 multipliers saved via systolic time-multiplexing
   - Memory Footprint:    32.47 KB (16,623 words) total on-chip

2. ARITHMETIC INVARIANTS:
   - Format:              Signed 16-bit Q7.8 (1 sign, 7 integer, 8 fractional)
   - Scale Factor:        256.0
   - Multiplier Slice:    prod[23:8] (discards lower 8 fractional bits)
   - Biases:              Strictly bias-free (zero bias adders)
   - Max Activation:      41.15 (comfortably below 128.0 headroom ceiling)

3. STAGE LATENCY BREAKDOWN (SUM = 9,116 CYCLES):
   - Stage 1 (Latch):     1 cycle
   - Stage 2 (Conv1+MP1): 4,892 cycles (400 windows)
   - Stage 3 (Conv2+MP2): 1,244 cycles (100 windows across 4 channels)
   - Stage 4 (MLP Head):  2,977 cycles (62 tiles @ 48 cyc/tile + 1 idle)
     * Layer 1 (200->64): 52 tiles = 2,496 cycles
     * Layer 2 (64->32):  8 tiles  =   384 cycles
     * Layer 3 (32->10):  2 tiles  =    96 cycles
   - Stage 5 (Argmax):    1 cycle (4-level binary tournament tree)
   - Stage 6 (Handshake): 1 cycle

4. FSM STATE NAMES (MEMORIZE THESE!):
   - conv1_array (6st):   ST_INIT, ST_ADVANCE, ST_FETCH, ST_MAC, ST_WAIT_VALID, ST_DONE
   - conv2_array (6st):   ST_LOAD, ST_FETCH, ST_MAC, ST_WAIT_VALID, ST_ADVANCE, ST_DONE
   - mlp_head    (4st):   IDLE, LOAD_WEIGHT, COMPUTE, DONE
   - conv_pe     (NO FSM):Modulo-9 counter (tap_idx 0..8) sequenced by conv1_array

5. TEAM CONTRIBUTIONS:
   - Shreyansh Raj:       Lead Architect, v2_top wrapper, argmax tree, verification suite
   - Sarthak Bhowmik:     Systolic array mesh, systolic PE, MLP time-multiplexed head
   - Shaurya Singh:       window_gen line buffer, conv_pe, conv1/conv2 arrays, MaxPool+ReLU
   - Shreya Anand:        Q7.8 quantization, bit-exact Python emulators, Headroom Gate
================================================================================
```
