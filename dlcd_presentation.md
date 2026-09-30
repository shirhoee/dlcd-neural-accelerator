# Digital Logic and Computer Design (DLCD) Project Presentation
## Hardware Acceleration of Neural Networks: From MLP to CNN

---

## Slide 1: Introduction & Project Goal
**Talking Points:**
- **Goal:** To design, simulate, and implement a hardware accelerator for Neural Network inference on an FPGA/RTL level.
- We focused on recognizing handwritten digits (MNIST dataset).
- The project is divided into two major phases: **Version 1 (V1)** and **Version 2 (V2)**.
- We successfully bridged the gap between software Machine Learning (PyTorch) and Digital Hardware Design (Verilog), proving bit-for-bit equivalence.

> [!NOTE]
> Emphasize to your teacher that the core achievement is creating a custom digital datapath (RTL) that exactly matches a trained software model without relying on generic CPUs or GPUs.

---

## Slide 2: Version 1 (V1) - The Baseline MLP
**Architecture:** Multi-Layer Perceptron (Dense/Fully Connected Network)
**Topology:** 100 (Input 10x10) -> 16 -> 6 -> 10 (Output)
**Key Hardware Concepts:**
- **Systolic Array:** We utilized a 16x16 Systolic Array core. A systolic array allows data to flow rhythmically through a 2D grid of Processing Elements (PEs), making it extremely efficient for matrix multiplication.
- **Data Flow:** Pixels are fed into the array, multiplied by weights stored in ROMs, and accumulated.
- **Quantization:** We used a Fixed-Point number format (Q7.8). This means 7 bits for the integer part and 8 bits for the fractional part (16 bits total). This avoids costly floating-point logic in hardware.

**Result:** V1 successfully classified images, but simple MLPs struggle with spatial image features, limiting the maximum accuracy.

---

## Slide 3: Motivation for Version 2 (V2)
**Talking Points:**
- To achieve state-of-the-art accuracy, we needed to upgrade the architecture to a **Convolutional Neural Network (CNN)**.
- CNNs use sliding filters to detect spatial patterns (edges, curves) regardless of where they appear in the image.
- **Challenge:** CNNs require completely different digital logic (sliding windows, line buffers, max pooling) compared to the dense matrix multiplications of V1.

---

## Slide 4: Version 2 (V2) - The CNN Architecture Upgrade
**Topology:**
1. **Conv1:** 3x3 Convolution (1 channel -> 4 channels)
2. **MaxPool1:** 2x2 Downsampling
3. **Conv2:** 3x3 Convolution (4 channels -> 8 channels)
4. **MaxPool2:** 2x2 Downsampling
5. **MLP Head:** 200 -> 64 -> 32 -> 10 Fully Connected Layers

**Key Hardware Additions:**
- **Line Buffers & Window Generators:** We designed custom `window_gen` modules that buffer incoming pixel streams and output 3x3 sliding windows in a single clock cycle.
- **Convolutional PEs:** Compute 9 Multiply-Accumulate (MAC) operations in parallel per channel.
- **Pipeline Architecture:** The entire V2 design is deeply pipelined. As soon as Conv1 finishes a pixel, it flows directly into MaxPool1, then Conv2, without stalling.

---

## Slide 5: The Hardware Area Dilemma & Time-Multiplexing
**Talking Points:**
- **The Problem:** The V2 MLP head (200->64->32->10) requires **15,168** individual MAC operations per image. Unrolling this fully in hardware would require massive amounts of silicon area and routing, making it impossible to synthesize efficiently.
- **Our Optimization:** We applied **Time-Multiplexing**. 
- Instead of building 15,000 multipliers, we reused a single **16x16 Systolic Array (256 MACs)** imported from V1.
- We designed a complex Finite State Machine (`mlp_head.v`) that chops the large matrices into 16x16 "tiles" and cycles them through the array.
- **Latency Hiding:** Because the preceding MaxPool2 layer outputs features slowly (taking ~6,100 cycles to complete), our systolic array (which takes ~2,900 cycles to compute the dense layers) completely hides its latency in the pipeline gap! We achieved massive area savings with **zero throughput penalty**.

> [!TIP]
> This is a crucial engineering tradeoff to highlight to your teacher. Showcasing that you understand Area vs. Throughput tradeoffs (using a smaller multiplexed unit to save area while hiding latency) demonstrates deep Digital Design comprehension.

---

## Slide 6: Verification & Bit-for-Bit Equivalence
**Talking Points:**
- Hardware design is prone to subtle bugs (overflows, truncation errors).
- We built a custom **Python Integer Emulator** (`int_emulator_v2.py`) that identically mimics the Verilog Q7.8 truncation and hardware overflow rules.
- **Regression Testing:** We ran 10,000 images through both PyTorch (Software) and the Verilog RTL (Hardware).
- **Result:** The hardware produced exactly **0 mismatches** against the integer emulator. We successfully proved that our digital logic behaves identically to the mathematical model.

---

## Slide 7: Conclusion & V1 vs V2 Comparison
| Metric | Version 1 (MLP) | Version 2 (CNN) |
|--------|-----------------|-----------------|
| **Architecture** | 100->16->6->10 | Conv -> Pool -> Conv -> Pool -> Dense |
| **Math Engine** | Unrolled Systolic | Pipelined Window Gens + Tiled Systolic |
| **Accuracy** | ~92-95% | ~98.8% |
| **Complexity** | Moderate | High (Deep Pipelining, Line Buffers, State Machines) |

**Final Thoughts:**
- The V2 upgrade demonstrates advanced digital logic design, memory management (ping-pong RAMs), and system-level architectural optimizations (time-multiplexing).
