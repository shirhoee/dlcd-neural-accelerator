# DLCD Neural Network Accelerator — Individual Team Portfolios & Defense Profiles
**Course:** UE25CS251A — Digital Logic and Computer Design Laboratory  
**Assessment:** End Semester Assessment (ESA) Mini-Project Viva Voce  
**Department:** Computer Science & Engineering, PES University, Bengaluru  
**Project:** Design and Implementation of an End-to-End Q7.8 Fixed-Point CNN Hardware Accelerator  

---

## Executive Overview: What This Project Was About

Modern edge-AI and embedded devices require real-time, deterministic, low-power machine learning inference without the area and thermal penalties of 32-bit floating-point units (FPUs). In this laboratory mini-project, our 4-member team designed, implemented, and verified an end-to-end, bit-exact Convolutional Neural Network (CNN) hardware accelerator in synthesizable Verilog-2001 (IEEE 1364-2001).

### Key Architectural Achievements
1. **Zero FPUs with Q7.8 Fixed-Point:** All weights, activations, and arithmetic run in signed 16-bit Q7.8 fixed-point format with per-step truncation `product[23:8]`.
2. **Preserving 2D Spatial Resolution:** We pre-process digits at 20×20 resolution (4× spatial data of 10×10 MLPs), eliminating morphological stroke erosion.
3. **Hardware Reuse via Time-Multiplexing:** Rather than synthesizing 15,168 unrolled multipliers for the dense classification head, we time-multiplexed a 16×16 systolic array (256 MACs) across all 3 layers in 2,977 cycles using dual ping-pong RAMs (`ram_A` and `ram_B`).
4. **98.70% Bit-Exact Hardware Accuracy:** Evaluated across the full 10,000 MNIST test images in RTL simulation, matching our Python golden emulator with **0 bit discrepancies** and delivering a **+5.64% boost** over the V1 baseline (93.06%).
5. **Deterministic Latency & High Throughput:** Inference executes in exactly **9,116 clock cycles** (91.16 µs at 100 MHz), delivering **10,969.7 frames per second** with only **292 leaf multipliers** and **32.47 KB** on-chip memory.

---

## Team Roster & Role Summary

| Member Name | Student Registration No. (SRN) | Core Project Role & Primary Domain | Key Verilog Modules Authored | Primary Software / Verification Artifacts |
| :--- | :--- | :--- | :--- | :--- |
| **Shreyansh Raj** | `PES2UG25CS516` | Lead Hardware Architect & Full-Stack RTL Verification | `v2_top.v`, `argmax.v`, `tb_submission.v`, `tb_top.v` | `test_10.py`, `harness.py`, FastAPI backend, React UI |
| **Sarthak Bhowmik** | `PES2UG25CS493` | Digital Datapath & Systolic Array Design | `systolic_array.v`, `systolic_pe.v`, `mlp_head.v` | `tb_systolic_array.v`, `tb_mlp_head.v`, tile schedules |
| **Shaurya Singh** | `PES2UG25CS508` | Convolutional PE & Line Buffer Subsystems | `window_gen.v`, `conv_pe.v`, `conv1_array.v`, `conv2_array.v`, `maxpool_pe.v` | Unit testbenches, adder tree synthesis, FSM control |
| **Shreya Anand** | `PES2UG25CS515` | Q7.8 Quantization & Fixed-Point Golden Models | `mac_q7_8.v`, `relu_q7_8.v`, `maxpool_array.v` | `fixed_point_math.py`, `int_emulator_v2.py`, weight export |

---

## Member 1: Shreyansh Raj (PES2UG25CS516)

### Role: Lead Hardware Architect & Full-Stack RTL Verification

### 1. Primary Responsibilities & Ownership
- **Top-Level Architectural Integration (`v2_top.v`):** Designed the master top-level wrapper interconnecting all 6 pipeline stages (Conv1, MaxPool1, Conv2, MaxPool2, Systolic MLP Head, Argmax) with a standardized handshake control interface: `clk`, `reset`, `start`, `pixel_in`, `pixel_addr`, `prediction`, `done`.
- **Tournament Argmax Unit (`argmax.v`):** Designed a 4-level balanced binary comparator tree that resolves the winning digit index `[0..9]` from 10 signed Q7.8 logits in a single pipelined clock cycle.
- **System-Wide Timing & Latency Reconciliation:** Formulated and proved the canonical 9,116-cycle execution latency model, resolving the timing relationship between start registration (`run_latch`) and done strobe sampling.
- **Automated Regression Suite (`harness.py`, `test_10.py`):** Developed a parallel Python verification harness executing multi-threaded Icarus Verilog instances against 10,000 MNIST test images.
- **Full-Stack Hardware Visualizer:** Engineered the production React 19 / TypeScript / Vite 8 frontend and asynchronous FastAPI backend, enabling live digit drawing, bit-exact RTL simulation, waveform inspection, and interactive FSM state tracking.

### 2. Deep Technical Challenges Solved
1. **Inter-Stage Pipeline Handshaking:** Ensured zero-latency data transfer between streaming stages (Conv1 $\to$ MaxPool1 and Conv2 $\to$ MaxPool2) and synchronous block-buffered stages (MLP Head) without pipeline bubbles or FIFO overflows.
2. **Start-Latch Synchronization:** Implemented the `run_latch` register in `v2_top.v` to safely capture single-cycle `start` pulses and deassert internal reset synchronously, guaranteeing deterministic Cycle-0 start alignment across all submodules.
3. **Headless Multi-Process Regression:** Built a fault-tolerant Python test harness that compiled Verilog RTL to `vvp` bytecode once, distributed test vectors across CPU cores via worker pools, and streamed results with zero file-locking conflicts.

### 3. Key Viva Defense Questions for Shreyansh
- **Q: How does `v2_top` sequence the entire pipeline?**  
  *Answer:* "`v2_top` operates as an interlocking hierarchical wrapper. A single-cycle `start` pulse sets `run_latch`, which deasserts `internal_reset`. `conv1_array` begins streaming pixel addresses (0..399) to image memory. As Conv1 generates convolved channels, `maxpool_array` performs on-the-fly streaming 2×2 pooling. When MaxPool1 finishes at Cycle 4,893, `conv2_array` buffers the 100 features and computes 8 output channels, which are pooled and stored into `ram_A` inside `mlp_head`. `mlp_head` then executes 62 matrix tiles, latches 10 logits to `argmax`, and `argmax` outputs the 4-bit prediction alongside a `done` pulse at Cycle 9,116."
- **Q: How does your Argmax module handle duplicate maximum logits?**  
  *Answer:* "`argmax.v` implements strict lower-index tie-breaking logic. If two class logits are identical, the comparator defaults to the lower index: `(val_a >= val_b) ? idx_a : idx_b`. This guarantees 100% deterministic, hazard-free classification."
- **Q: What is the exact difference between absolute Cycle 9,117 and latency 9,116?**  
  *Answer:* "Cycle 0 is when the testbench asserts `start`. At Cycle 1, `start` is sampled into `run_latch`. The testbench elapsed cycle counter increments on each subsequent clock edge until `done` is asserted at absolute Cycle 9,117. Therefore, the actual hardware execution duration is $9,117 - 1 = \mathbf{9,116}$ clock cycles."

---

## Member 2: Sarthak Bhowmik (PES2UG25CS493)

### Role: Digital Datapath & Systolic Array Design

### 1. Primary Responsibilities & Ownership
- **2D Systolic Array Mesh (`systolic_array.v`):** Designed and implemented the 16×16 2D processing grid containing 256 interconnected Processing Elements, enforcing strict nearest-neighbor spatial routing.
- **Systolic Processing Element (`systolic_pe.v`):** Authored the core PE microarchitecture implementing Kung's Weight-Stationary dataflow with horizontal weight shifting, vertical activation streaming, and horizontal partial sum accumulation.
- **Time-Multiplexed MLP Controller (`mlp_head.v`):** Architected the 4-state FSM controller (`IDLE`, `LOAD_WEIGHT`, `COMPUTE`, `DONE`) that maps all three dense layers ($200 \to 64 \to 32 \to 10$) onto the single 16×16 array.
- **Dual Ping-Pong SRAM Subsystem:** Implemented on-chip dual memories (`ram_A` with 208 words, `ram_B` with 64 words) with alternating read/write ports to eliminate external memory accesses between dense layers.
- **Standalone Unit Verification (`tb_systolic_array.v`, `tb_mlp_head.v`):** Verified bit-exact 16×16 matrix multiplications and layer sequencing under standalone Icarus Verilog testbenches.

### 2. Deep Technical Challenges Solved
1. **Time-Multiplexing 15,168 Weights onto 256 MACs:** Designed an automated tile-partitioning scheme:
   - Layer 1 ($200 \to 64$): 13 row tiles $\times$ 4 col tiles = 52 tiles.
   - Layer 2 ($64 \to 32$): 4 row tiles $\times$ 2 col tiles = 8 tiles.
   - Layer 3 ($32 \to 10$): 2 row tiles $\times$ 1 col tile = 2 tiles.
   Total = 62 tiles executed in 2,977 cycles, achieving a 59.25× reduction in hardware multiplier footprint.
2. **Ping-Pong Buffer Handover:** Eliminated data-hazard races by alternating source and destination memories between layers: Layer 1 reads `ram_A` and writes `ram_B`; Layer 2 reads `ram_B` and writes `ram_A`; Layer 3 reads `ram_A` and writes output registers.
3. **Weight-Stationary Shift Sequencing:** Formulated the 16-cycle shift-loading mechanism (`LOAD_WEIGHT`) that pre-loads a 16×16 tile from `mlp_rom` row-by-row before streaming activations for 32 cycles.

### 3. Key Viva Defense Questions for Sarthak
- **Q: Why did you choose Weight-Stationary dataflow over Output-Stationary?**  
  *Answer:* "In neural network matrix multiplication where input vectors are processed sequentially, holding weights stationary inside PEs minimizes local register toggling and power dissipation. Weights are loaded once from ROM in 16 cycles and remain static while activations stream through the array. Partial sums are accumulated horizontally across rows, allowing computed outputs to emerge directly from the right edge with zero dedicated output-draining cycles."
- **Q: Explain how a single 16×16 tile executes in 48 cycles.**  
  *Answer:* "Each tile execution consists of two distinct phases:
  1. `LOAD_WEIGHT` (16 cycles): The controller shifts a 16×16 weight block from `mlp_rom` into the systolic array row-by-row (counter counts 0..15).
  2. `COMPUTE` (32 cycles): 16 activation words stream down from the top edge. It takes 16 cycles for the first activation to propagate to the bottom row, and an additional 16 cycles for partial sums to accumulate and emerge from the right edge. On cycles 16 through 31, valid outputs are latched into ping-pong RAM with fused ReLU.
  Total per tile = $16 + 32 = \mathbf{48}$ clock cycles."
- **Q: Why does `ram_A` have 208 words when MaxPool2 only outputs 200 features?**  
  *Answer:* "Because the systolic array operates on 16-element vectors, all input dimensions must be multiples of 16. The 200 input features are padded with 8 zeros to reach 208 ($13 \times 16 = 208$). This allows 13 clean row tiles without requiring complex boundary masking logic."

---

## Member 3: Shaurya Singh (PES2UG25CS508)

### Role: Convolutional PE & Line Buffer Subsystems

### 1. Primary Responsibilities & Ownership
- **2D Spatial Window Generator (`window_gen.v`):** Designed the 47-element shift-register line buffer that exposes 9 spatial pixels simultaneously for continuous 3×3 convolutions across 20×20 images.
- **Convolutional PE (`conv_pe.v`):** Designed the 9-tap sequential Multiply-Accumulate unit with internal weight shift registers, 9:1 multiplexer, modulo-9 tap counter (`tap_idx`), and accumulator feedback register.
- **Conv1 4-Channel Parallel Array (`conv1_array.v`):** Implemented the 6-state master FSM (`ST_INIT`, `ST_ADVANCE`, `ST_FETCH`, `ST_MAC`, `ST_WAIT_VALID`, `ST_DONE`) controlling 4 parallel `conv_pe` units.
- **Conv2 Multi-Channel Subsystem (`conv2_array.v`):** Architected the 8-filter convolution array instantiating 32 MAC units and 4-channel combinational adder trees.
- **Fused MaxPool + ReLU Hardware Units (`maxpool_pe.v`, `maxpool_array.v`):** Implemented 2×2 tournament comparator trees with fused zero-clamping logic.

### 2. Deep Technical Challenges Solved
1. **Zero-Latency Line Buffering:** Avoided expensive multi-port SRAM by utilizing a 47-element shift register (`sr[0..46]`). Wire taps at $0..2$, $20..22$, and $40..42$ provide full 3×3 receptive fields on every clock edge without reading RAM.
2. **Channel Adder Trees in Conv2:** Conv2 combines 4 input channels into 8 output filters ($8 \times 4 \times 9 = 288$ weights). Designed a balanced 2-level signed adder tree per filter group that sums 4 parallel MAC outputs with bit-level truncation into an 8-channel convolved stream.
3. **FSM Interlocking with Window Generator:** Created a robust handshake mechanism where `conv1_array` pulses `win_advance` and waits for `win_valid`, preventing incorrect convolutions along image borders and scanline wrap-arounds.

### 3. Key Viva Defense Questions for Shaurya
- **Q: Why does `window_gen.v` have exactly 47 shift registers?**  
  *Answer:* "For a 20×20 image, each row contains 20 pixels. A 3×3 window requires access to pixels from Row $r$, Row $r+1$, and Row $r+2$. To hold two full rows plus 3 pixels of the third row requires $20 + 20 + 3 = 43$ registers. An additional 4 registers provide pipeline boundary buffering for zero-padding alignment, resulting in a 47-register shift chain (`sr[0..46]`)."
- **Q: Explain the mathematical proof behind fused MaxPool + ReLU.**  
  *Answer:* "The ReLU activation function $f(x) = \max(0, x)$ is monotonically non-decreasing. For any set of numbers $\{a, b, c, d\}$, the maximum value after applying ReLU is identical to applying ReLU to the maximum value:
  $$\max(\text{ReLU}(a), \text{ReLU}(b), \text{ReLU}(c), \text{ReLU}(d)) \equiv \text{ReLU}(\max(a, b, c, d))$$
  By placing the ReLU gate *after* the 2×2 comparator tree instead of before it, we evaluate ReLU once instead of 4 times, eliminating 75% of ReLU multiplexer gates."
- **Q: Why does `conv_pe.v` not need its own FSM?**  
  *Answer:* "`conv_pe.v` is a purely datapath execution unit. It contains a 4-bit binary counter (`tap_idx` counting 0..8) and three control wires: `load_weight`, `mac_en`, and `clr_acc`. The higher-level state sequencing (loading weights during reset, clearing accumulators on Tap 0, enabling MAC across 9 taps, and asserting valid strobes) is managed entirely by the 6-state FSM in `conv1_array.v`. This separation of control and datapath keeps the PE modular and compact."

---

## Member 4: Shreya Anand (PES2UG25CS515)

### Role: Q7.8 Quantization & Fixed-Point Golden Models

### 1. Primary Responsibilities & Ownership
- **Q7.8 Fixed-Point Mathematical Specification:** Defined the signed 16-bit Q7.8 arithmetic rules (1 sign, 7 integer, 8 fractional bits; scale factor 256.0), establishing the numerical foundation of the entire accelerator.
- **Arithmetic Verilog Primitives (`mac_q7_8.v`, `relu_q7_8.v`):** Implemented synthesizable Verilog modules for signed Q7.8 multiplication with per-step truncation `product[23:8]` and zero-clamping ReLU.
- **Bit-Exact Python Integer Emulator (`fixed_point_math.py`, `int_emulator_v2.py`):** Developed a golden Python emulator that models exact 16-bit two's complement integer math, 32-bit products, right shifts by 8, and wraparound behavior.
- **Model Training & Quantization Pipeline (`train_v2_quantized.py`):** Trained the PyTorch CNN model using bias-free layers and evaluated post-training quantization on all 10,000 MNIST test images (98.83% Float32 $\to$ 98.70% Q7.8).
- **The Q7.8 Headroom Gate:** Conceived and implemented the automated Headroom Gate ($|x| < 128.0$), proving mathematically that internal activations never overflow 16-bit limits.
- **ROM Generation Tooling (`export_v2_weights.py`):** Wrote the export scripts formatting quantized weights into synthesizable Verilog `$readmemh` hex ROM files (`conv1_rom.txt`, `conv2_rom.txt`, `mlp_rom.txt`).

### 2. Deep Technical Challenges Solved
1. **Quantization Noise Mitigation:** Post-training quantization often causes accuracy collapse. By enforcing bias-free training and tuning weight decay, the Q7.8 quantized model retained **98.70% accuracy**, suffering only 13 misclassifications across 10,000 images compared to 32-bit floating point.
2. **Per-Step Truncation vs Wide Accumulator:** Proved that truncating `product[23:8]` at every MAC step matches hardware exactly, preventing bit drift between the Python golden model and Verilog RTL.
3. **Headroom Gate Verification:** Tracked dynamic activation ranges across all 10,000 test images:
   - Conv1 peak activation: $14.32$ (integer limit: 128.0)
   - Conv2 peak activation: $28.74$ (integer limit: 128.0)
   - Dense peak activation: $41.15$ (integer limit: 128.0)
   This mathematical guarantee allowed the RTL datapath to omit heavy saturation clamping circuits, saving area and critical path delay.

### 3. Key Viva Defense Questions for Shreya
- **Q: Why is the truncation slice `product[23:8]` and not `product[15:0]` or `product[31:16]`?**  
  *Answer:* "When two 16-bit Q7.8 numbers are multiplied, the product is a 32-bit signed Q14.16 number with 16 fractional bits. To restore the Q7.8 representation with 8 fractional bits, we must discard the lowest 8 fractional bits ($Product[7:0]$). Slicing the next 16 bits ($Product[23:8]$) preserves 8 fractional bits (bits 15:8) and 8 integer/sign bits (bits 23:16). Slicing $Product[15:0]$ would discard all integer information, while $Product[31:16]$ would shift the decimal point by 8 positions, scaling the value down by 256×!"
- **Q: Why are your neural network layers strictly bias-free?**  
  *Answer:* "Biases in neural networks act as constant offsets. In fixed-point hardware:
  1. Each bias requires an additional 16-bit adder per neuron and extra ROM storage.
  2. Biases often have different magnitude distributions than weights, increasing overflow risk.
  By training our model without biases (`bias=False`), the optimizer adjusted weights to be zero-centered. Our model achieved 98.83% Float32 and 98.70% Q7.8 accuracy, proving that biases are completely redundant for digit classification while saving 122 hardware adders and ROM words."
- **Q: How did you ensure 0 bit discrepancies between Python and Verilog RTL?**  
  *Answer:* "Our Python golden model (`fixed_point_math.py`) does not use floating-point operations. It converts every number to a 16-bit signed integer. During multiplication, it performs `(A * B) >> 8`, clamps to 16-bit two's complement `((prod + 32768) % 65536) - 32768`, and executes additions in exact two's complement integer space. Because this mirrors the gate-level Verilog logic bit-for-bit, RTL simulation across all 10,000 images matched the Python emulator with zero bit mismatches."

---

## 5. Team Collaboration & Shared System Architecture Map

```
+--------------------------------------------------------------------------------------------------+
|                                    PROJECT ARCHITECTURE MAP                                      |
+--------------------------------------------------------------------------------------------------+
|  1. Q7.8 QUANTIZATION & MATH (Shreya Anand)                                                      |
|     - Scale: 256.0, Range: [-128, +127.99], mac_q7_8.v (prod[23:8]), Headroom Gate (<128.0)     |
|     - Golden Python Emulator: int_emulator_v2.py (10k images, 98.70% bit-exact accuracy)        |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
|  2. CONVOLUTIONAL FRONT-END & LINE BUFFERS (Shaurya Singh)                                       |
|     - window_gen.v (47-sr line buffer, 9 taps parallel)                                          |
|     - conv1_array.v (4 PEs, 6-state FSM, 4,892 cycles)                                           |
|     - maxpool1_array.v & maxpool2_array.v (fused 2x2 tournament max + ReLU, 75% gates saved)     |
|     - conv2_array.v (8 filters x 4 PEs = 32 MACs, 4-ch adder tree, 6-state FSM, 1,244 cycles)   |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
|  3. SYSTOLIC ARRAY & TIME-MULTIPLEXED HEAD (Sarthak Bhowmik)                                     |
|     - systolic_array.v (16x16 mesh, 256 PEs, Kung Weight-Stationary dataflow)                    |
|     - mlp_head.v (4-state FSM, dual ping-pong RAMs: ram_A 208w, ram_B 64w)                       |
|     - 62-Tile Schedule (200->64->32->10 executed in 2,977 cycles; 15,168 multipliers avoided)   |
+--------------------------------------------------------------------------------------------------+
                                               │
                                               ▼
+--------------------------------------------------------------------------------------------------+
|  4. TOP-LEVEL WRAPPER, ARGMAX & FULL-STACK VERIFICATION (Shreyansh Raj)                          |
|     - v2_top.v (Master 6-stage interlocking wrapper, run_latch start registration)               |
|     - argmax.v (4-level binary tournament comparison tree, 1-cycle latency)                      |
|     - Timing Model: 9,116 clock cycles (91.16 us @ 100 MHz; 10,969.7 FPS)                       |
|     - Multi-threaded Python test harness (10,000 images verified bit-exact)                       |
|     - Interactive Web GUI: React 19 + TypeScript + FastAPI backend                               |
+--------------------------------------------------------------------------------------------------+
```
