# Digital Logic and Computer Design (DLCD) Project Presentation
## Hardware Acceleration of Neural Networks: From MLP to CNN

**Course:** UE25CS251A — Digital Logic & Computer Design Laboratory  
**Assessment:** End Semester Assessment (ESA)  
**Team Members:** Shreyansh Raj, Sarthak Bhowmik, Shaurya Singh, Shreya Anand  

---

## Slide 1: Introduction & Project Goal
**Talking Points:**
- **Goal:** To design, simulate, and verify a bit-exact custom hardware accelerator for Neural Network inference on an RTL/FPGA level.
- **Application:** Handwritten digit classification on the benchmark MNIST dataset (0–9).
- **Two Architectural Generations:**
  1. **Version 1 (V1):** Baseline Multi-Layer Perceptron (100 $\rightarrow$ 16 $\rightarrow$ 6 $\rightarrow$ 10).
  2. **Version 2 (V2):** Hierarchical 2D Convolutional Neural Network with time-multiplexed systolic classification head.
- **Key Achievement:** Bridged the gap between software Machine Learning (PyTorch) and Digital Hardware Design (synthesizable Verilog-2001), achieving bit-for-bit equivalence with zero floating-point units and pure hardware execution during the 9,116-cycle compute window without host CPU arithmetic or control involvement (host supplies pixels via `pixel_addr`/`pixel_in`).

---

## Slide 2: Version 1 (V1) — The Baseline MLP
**Architecture:** Fully Connected Multi-Layer Perceptron (Dense Network)  
**Topology:** 100 inputs (10×10 image) $\rightarrow$ 16 $\rightarrow$ 6 $\rightarrow$ 10 (Output logits)  
**Key Hardware Concepts:**
- **Systolic Array:** Utilized a 16×16 2D Systolic Array core (256 multipliers) with weight-stationary dataflow. Data flows rhythmically through nearest-neighbor PEs, maximizing multiplier utilization.
- **Inference Latency:** 159 clock cycles (1.59 μs @ 100 MHz); 259 clock cycles total from reset including 100-cycle feature preload.
- **Quantization:** Q7.8 signed fixed-point format (16 bits: 1 sign bit, 7 integer bits, 8 fractional bits; multiplier = 256.0), eliminating costly FPUs.
- **Accuracy Limitation:** 93.06% accuracy on M15 optical digits (95.39% on downsampled 10×10 MNIST). Spatial stroke features and topological loops (such as enclosures in 8, 0, 6, 9) collapse when severely downsampled to 10×10, forming a fundamental accuracy bottleneck for simple MLPs.

---

## Slide 3: Motivation for Version 2 (V2)
**Talking Points:**
- To achieve state-of-the-art accuracy (>98.8%), we upgraded the architecture to a **2D Convolutional Neural Network (CNN)**.
- CNNs preserve 20×20 spatial input resolution (400 words, a 4× increase in pixel density) and use sliding filter banks to extract translation-invariant edge, curve, and stroke representations.
- **Design Challenge:** CNNs require streaming line buffers, multi-channel adder trees, and spatial pooling units—radically different from the matrix multiply datapath of V1.

---

## Slide 4: Version 2 (V2) — The Pipelined CNN Architecture
**Topology:**
1. **Input:** 20×20 pixels streaming into line buffers.
2. **Conv1:** 4 filters × 3×3 Convolution (1 channel $\rightarrow$ 4 channels, valid padding, produces 18×18).
3. **MaxPool1:** 2×2 Downsampling + Fused ReLU (4 channels, produces 9×9).
4. **Conv2:** 8 filters × 4 input channels × 3×3 Convolution (produces 7×7).
5. **MaxPool2:** 2×2 Downsampling + Fused ReLU (produces 8 channels × 5×5 = 200 flattened features).
6. **MLP Head:** Time-multiplexed 16×16 Systolic Array computing 200 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 10.
7. **Argmax:** 10-input tournament comparator tree asserting predicted digit and `done`.

**Total Multipliers:** Exactly **292 hardware multipliers** (4 in Conv1 + 32 in Conv2 + 256 in Systolic Head).

---

## Slide 5: Key Architectural Innovations & Tradeoffs

### 1. Time-Multiplexing the 16×16 Systolic Array
- **The Problem:** A naive unrolled dense classification head (200 $\rightarrow$ 64 $\rightarrow$ 32 $\rightarrow$ 10) requires 15,168 parallel hardware multipliers, far exceeding edge FPGA budgets.
- **The Solution:** We reused the verified 16×16 systolic array (256 multipliers) across all three dense layers using dual ping-pong RAMs (`ram_A` [208 words], `ram_B` [64 words]).
- **Result:** **98.3% reduction in multipliers** (from 15,168 down to 256) while computing the entire classification head in just 2,977 clock cycles.

### 2. Fused MaxPool + ReLU Optimization
- Because the ReLU activation function $f(x) = \max(0, x)$ is monotonically non-decreasing, it commutes with the max-pooling operator:
  $$\max(\text{ReLU}(x_0), \dots, \text{ReLU}(x_3)) = \text{ReLU}(\max(x_0, \dots, x_3))$$
- Placing the non-negative clamping gate *after* the 2×2 tournament comparator tree eliminates **75% of ReLU logic operations** with zero bit distortion.

### 3. Wraparound Arithmetic & Training Headroom Gate
- To maintain single-cycle MAC ALU timing without multi-level saturation clamp delays, `mac_q7_8.v` implements natural two's complement modular addition.
- We enforced a strict **Headroom Gate** during training ($|logit| < 128.0$). As a result, no activation ever overflows $[-128, +127.996]$ across all 10,000 test images.

---

## Slide 6: Execution Latency Breakdown (9,116 Cycles)
**Deterministic Latency:** Exactly **9,116 clock cycles** (91.16 μs at 100 MHz; 10,969.7 FPS theoretical pipelined, 10,964.9 FPS demonstrated with 4-cycle reset sequence).

| Stage | Cycles | Time (100 MHz) | Share (%) | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Front-End Latch** | 1 | 0.01 μs | 0.01% | `start` strobe sampled into `run_latch` |
| **Conv1 + MaxPool1** | 4,892 | 48.92 μs | 53.66% | Streaming 4-channel 3×3 convolution and 2×2 pooling |
| **Conv2 + MaxPool2** | 1,244 | 12.44 μs | 13.65% | 8-filter 4-channel convolution storing 200 features |
| **MLP Head (Systolic)** | 2,977 | 29.77 μs | 32.66% | 3 dense layers across 62 tiles (48 cycles/tile) |
| **Argmax Comparator** | 1 | 0.01 μs | 0.01% | Tournament comparator extracts winning class |
| **Inter-Stage Alignment**| 1 | 0.01 μs | 0.01% | Pipeline output latch and `done` pulse |
| **TOTAL** | **9,116** | **91.16 μs** | **100.0%** | **Reconciled, deterministic real-time latency** |

---

## Slide 7: Verification & Bit-for-Bit Equivalence
**Rigorous Multi-Level Verification:**
1. **Unit Testbenches:** Canonical test suite (`run_all_tests.bat`) runs **13 active testbenches with 100% pass rate (13/13)**.
2. **Q7.8 Integer Emulator:** Custom bit-exact Python emulator (`int_emulator_v2.py`) models identical per-step truncation `product[23:8]`.
3. **10-Image Sanity Test:** `test_10.py` achieves 10/10 correct matches, identical 9,116-cycle count.
4. **Full 10,000-Image Hardware Regression:**
   - Evaluated all 10,000 MNIST test images in Icarus Verilog (`harness.py`).
   - **RTL Hardware Accuracy: 98.83% (9,883 / 10,000)**.
   - **RTL vs Emulator Mismatches: EXACTLY 0**.
   - Proven 100% bit-exact equivalence between hardware and software.

---

## Slide 8: Architectural Comparison: V1 vs V2

| Specification Metric | Version 1 (Baseline MLP) | Version 2 (Proposed CNN) |
| :--- | :--- | :--- |
| **Network Topology** | 100 $\rightarrow$ 16 $\rightarrow$ 6 $\rightarrow$ 10 | Conv1 $\rightarrow$ MP1 $\rightarrow$ Conv2 $\rightarrow$ MP2 $\rightarrow$ Systolic Head |
| **Spatial Resolution**| 10×10 pixels (100 words) | 20×20 pixels (400 words) |
| **Math Units** | 256 Multipliers (16×16 Mesh) | 292 Multipliers (Conv1: 4, Conv2: 32, Systolic: 256) |
| **On-Chip Memory** | Distributed Registers | 16,623 words (32.47 KB) ping-pong SRAM & ROM |
| **Inference Latency** | 159 cycles (1.59 μs) | 9,116 cycles (91.16 μs) |
| **MNIST Test Accuracy**| 93.06% | **98.83% (+5.77% accuracy improvement)** |
| **Hardware Parity** | 100% Bit-Exact Match | **100% Bit-Exact Match (0 mismatches on 10,000 images)**|

---

## Slide 9: Conclusion & Summary
- Successfully designed, simulated, and verified an end-to-end CNN accelerator in pure Verilog-2001.
- Eliminated FPUs with Q7.8 signed fixed-point arithmetic while reaching **98.83% accuracy**.
- Solved the silicon area dilemma by time-multiplexing a 16×16 systolic array, slashing multiplier requirements by 98.3%.
- Full 10,000-image hardware regression confirms **0 bit-level mismatches** against golden models.
- Complete documentation, 46-page synchronized report, and interactive "Glass Box" web visualizer demonstrate full-stack engineering excellence.
