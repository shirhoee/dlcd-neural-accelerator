# Mini Project Submission: Digital Circuit Design Specification & Datapath Schematic

**Course:** Digital Logic & Computer Design (DLCD)  
**Project Title:** Hardware Neural Network Accelerator (DLCD Neural Accelerator)  
**Selected Module:** Convolutional Processing Element (`conv_pe.v`) with Sequential Q7.8 MAC Unit (`mac_q7_8.v`)  
**Student Name:** Shreyansh Raj  
**SRN / Roll Number:** [SRN / Roll Number]  
**Date:** October 2026  

---

## 1. Executive Summary & Module Purpose

In the custom digital neural network accelerator, the **Convolutional Processing Element (`conv_pe.v`)** executes the 2D spatial convolution for the frontend convolutional layer (Conv1).

A fully unrolled 2D convolution requires 9 parallel hardware multipliers per output channel, which demands substantial FPGA DSP and logic resources. To minimize area and routing complexity, this design implements a **9-tap time-multiplexed, weight-stationary sequential Multiply-Accumulate (MAC) processing element**.

### Key Characteristics:
- **Arithmetic Precision:** Signed Q7.8 Fixed-Point (16-bit signed two's complement: 1 sign bit, 7 integer bits, 8 fractional bits; scale factor $S = 2^8 = 256$, dynamic range $[-128.0, +127.996]$).
- **Dataflow:** Weight-Stationary. The 9 filter weights for the $3 \times 3$ kernel are shifted into internal registers during configuration and held stationary while incoming streaming pixels are evaluated sequentially.
- **Cycle Budget:** Exactly 9 clock cycles per $3 \times 3$ receptive field window.
- **Throughput:** Computes 1 output pixel feature every 9 clock cycles with continuous streaming support.
- **Hardware Component Footprint (`conv_pe`):**
  - 1 Signed $16 \times 16$ Multiplier (in `mac_q7_8.v`)
  - 1 Signed 16-bit Adder (in `mac_q7_8.v`)
  - 9 16-bit Weight Registers (`weights[0:8]`, arranged as a shift register; intentionally unreset)
  - 1 16-bit Accumulator Register (`out_acc`)
  - 1 16-bit 2-to-1 Feedback Multiplexer (`clr_acc` selector)
  - 1 16-bit 9-to-1 Weight Multiplexer (addressed by `tap_idx`)
  - 1 4-bit Synchronous Modulo-9 Counter with Comparator (`tap_idx`, counts $0$ to $8$)
  - 1 1-bit Output Valid Flip-Flop (`valid_out`)
  *(Note: The full Conv1 array in `conv1_array.v` instantiates 4 of these `conv_pe` instances in parallel, one for each output feature channel).*

---

## 2. Port Interface & Signal Contract

### Table 1: Port List of `conv_pe.v`

| Signal Name | Direction | Bit Width | Type | Active Level | Description |
|---|---|---|---|---|---|
| `clk` | Input | 1 | Clock | Rising Edge | Primary system clock (synchronous domain). |
| `reset` | Input | 1 | Control | High (1) | Synchronous reset. Resets `tap_idx` to 0, `out_acc` to 0, and `valid_out` to 0. *(Weights are intentionally not reset to conserve routing resources).* |
| `load_weight` | Input | 1 | Control | High (1) | Active-high shift enable for serial weight loading. Weights must be shifted in reverse order ($W_8$ first down to $W_0$ last) so that $W_0$ resides in `weights[0]`. |
| `weight_in` | Input | [15:0] | Data (Q7.8) | — | Serial 16-bit signed weight stream fed during configuration. |
| `mac_en` | Input | 1 | Control | High (1) | Clock-enable for MAC computation and tap counter advance. When low, `tap_idx` and `out_acc` hold their current states. |
| `clr_acc` | Input | 1 | Control | High (1) | Asserted during Tap 0 to clear accumulator feedback to `16'sd0` for starting a new convolution window. |
| `pixel_in` | Input | [15:0] | Data (Q7.8) | — | 16-bit signed streaming pixel value from sliding-window generator. |
| `out_acc` | Output | [15:0] | Data (Q7.8) | — | 16-bit signed accumulated convolution sum. Valid when `valid_out` is high. |
| `valid_out` | Output | 1 | Status | High (1) | 1-cycle active-high pulse registered on the clock cycle following Tap 8, indicating that the completed 9-tap sum is valid on `out_acc`. |

---

## 3. Register Transfer Level (RTL) Datapath Schematic

The architectural schematic of the `conv_pe` module is illustrated below:

![Conv1 Processing Element Circuit Diagram](./conv_pe_circuit_diagram.png)

### Datapath Description:
1. **Weight Storage & Selection:** The 9 kernel coefficients ($W_0$ to $W_8$) reside in a $9 \times 16$-bit shift register. A 9-to-1 multiplexer driven by `tap_idx[3:0]` routes the active weight `weights[tap_idx]` to the multiplier.
2. **Multiplier (`mac_q7_8`):** The selected 16-bit signed weight and the streaming 16-bit signed `pixel_in` are multiplied, yielding a 32-bit signed product in Q15.16 format.
3. **Truncation Slice:** Truncation is performed combinationaly by extracting bits `product[23:8]`. The upper 8 bits (`[31:24]`) are discarded based on headroom verification, and the lower 8 bits (`[7:0]`) are truncated (floor), aligning the result back to 16-bit Q7.8.
4. **Accumulator Feedback & MUX:** A 2-to-1 multiplexer selects between `16'sd0` (when `clr_acc = 1` during Tap 0) and the previous accumulator value `out_acc` (when `clr_acc = 0`). The 16-bit adder sums the truncated product with the selected accumulator base.
5. **Output Registers:** On each rising clock edge with `mac_en = 1`, `out_acc` registers the adder output. When `tap_idx == 8`, `valid_out` registers high for the subsequent clock cycle and `tap_idx` wraps to 0.

---

## 4. Control Unit & Tap Sequencer

The `conv_pe` module does not require a complex multi-state FSM controller. Sequencing is governed by a synchronous 4-bit modulo-9 ring counter (`tap_idx`, counting $0$ through $8$), enabled by `mac_en`.

- When `mac_en = 1`, `tap_idx` advances by 1 each clock cycle. When `tap_idx` reaches 8, it wraps back to 0 on the next active cycle.
- When `mac_en = 0`, the counter freezes, preserving the current state and accumulator values.
- Weight loading is orthogonal: asserting `load_weight = 1` shifts the weights independently of `tap_idx`.

### Modulo-9 Ring Counter Sequence:
```
[ tap_idx = 0 ] --> [ tap_idx = 1 ] --> [ tap_idx = 2 ] --> ... --> [ tap_idx = 8 ]
      ^                                                                     |
      +------------------------ (wraps to 0) -------------------------------+
```

### Signal Sequence Across a 9-Tap Window:

| Cycle Phase | `mac_en` | `clr_acc` | `tap_idx` | Feedback MUX (`acc_in`) | Multiplier Operation ($P_i$) | `valid_out` |
|---|---|---|---|---|---|---|
| **Tap 0** | 1 | 1 | 0 | `16'sd0` | $P_0 = \text{pixel}_0 \times W_0$ | 0 |
| **Tap 1** | 1 | 0 | 1 | `out_acc` ($P_0$) | $P_1 = \text{pixel}_1 \times W_1$ | 0 |
| **Tap 2** | 1 | 0 | 2 | `out_acc` ($P_0 + P_1$) | $P_2 = \text{pixel}_2 \times W_2$ | 0 |
| **Tap 3..7** | 1 | 0 | 3..7 | `out_acc` ($\sum_{k=0}^{i-1} P_k$) | $P_i = \text{pixel}_i \times W_i$ | 0 |
| **Tap 8** | 1 | 0 | 8 | `out_acc` ($\sum_{k=0}^{7} P_k$) | $P_8 = \text{pixel}_8 \times W_8$ | 0 |
| **Handoff (Tap 0 of next window)** | 1 | 1 | 0 | `16'sd0` | $P_0' = \text{pixel}_0' \times W_0$ | **1** (asserted for completed window) |

---

## 5. Q7.8 Fixed-Point Mathematical Formulation

Fixed-point arithmetic maps real values to signed integers using a uniform scale factor $S = 2^B$, where $B = 8$:

$$X_{\text{fixed}} = \text{round}(X_{\text{real}} \times 2^8)$$

### Multiplication & Bit Format:
Given two signed Q7.8 operands:
$$A \in \text{Q7.8} \quad (1\text{ sign bit}, 7\text{ integer bits}, 8\text{ fractional bits})$$
$$B \in \text{Q7.8} \quad (1\text{ sign bit}, 7\text{ integer bits}, 8\text{ fractional bits})$$

The 32-bit two's complement product is in **Q15.16** format:
$$\text{Product} = A \times B \quad (1\text{ sign bit}, 15\text{ integer bits}, 16\text{ fractional bits}, \text{Scale } 2^{16})$$

To return the result to 16-bit Q7.8 format, the product is scaled by $2^{-8}$ via bit-slicing:
$$\text{Product}_{\text{Q7.8}} = \lfloor (A \times B) / 2^8 \rfloor = \text{Product}[23:8]$$

### Bit-Level Breakdown of `product[31:0]`:
```
Product [31:0]:
  [31:24] (8 bits) : Extended integer bits (discarded; headroom verified to avoid overflow)
  [23:16] (8 bits) : Q7.8 Integer part (1 sign bit + 7 integer bits)
  [15:8]  (8 bits) : Q7.8 Fractional part
  [7:0]   (8 bits) : Lower sub-fractional bits (truncated floor; dropped)
```

Extracting `product[23:8]` performs an exact arithmetic right-shift of 8 bits at zero combinational logic cost (pure wiring slice).

### Headroom & Overflow Behavior:
The RTL adder and accumulator perform standard 16-bit signed arithmetic without saturation logic; if a value exceeds $[-128.0, +127.996]$, it wraps around. To eliminate overflow during hardware execution, the neural network training pipeline incorporates a Headroom Gate during export:
- Maximum model output logit observed across the test set is $72.5$, safely below the Q7.8 capacity limit of $+127.996$.
- Input pixels are normalized within $[0.0, 1.0]$ ($0$ to $255$ integer in Q7.8), and kernel weights are bounded. Intermediate 9-tap sums remain strictly within the 16-bit range.

---

## 6. Cycle-Accurate Timing Diagram

The timing trace below illustrates two consecutive 9-tap convolution windows with seamless back-to-back streaming:

```
Clock Cycle :  0    1    2    3   ...   7    8    9   10   11   ...
clk         : _/ \_/ \_/ \_/ \_/ ... \_/ \_/ \_/ \_/ \_/ \_/ \_
mac_en      : _____/==============================================
clr_acc     : _____/=====\___________________________/=====\______
pixel_in    : -----< p0 >< p1 >< p2 > ... < p7 >< p8 >< q0 >< q1 >-
tap_idx     : -----<  0 ><  1 ><  2 > ... <  7 ><  8 ><  0 ><  1 >-
weights[idx]: -----< w0 >< w1 >< w2 > ... < w7 >< w8 >< w0 >< w1 >-
mac_result  : -----< Acc0>< Acc1>< Acc2> ...<Acc7><Acc8><New0><New1>
out_acc     : ----------<Acc0><Acc1> ... ... <Acc7><Acc8><New0>---
valid_out   : _______________________________________/=====\______
                                                          ^
                                                Window 1 Result Valid
```

---

## 7. Verilog Code Implementation (`conv_pe.v` & `mac_q7_8.v`)

### Core MAC Module (`mac_q7_8.v`):
```verilog
module mac_q7_8 (
    input  wire signed [15:0] weight,
    input  wire signed [15:0] in_val,
    input  wire signed [15:0] acc_in,
    output reg  signed [15:0] acc_out
);
    wire signed [31:0] product;

    assign product = weight * in_val;
    always @(*) begin
        acc_out = acc_in + product[23:8];
    end
endmodule
```

### Processing Element Module (`conv_pe.v`):
```verilog
module conv_pe (
    input  wire clk,
    input  wire reset,
    
    // Weight loading interface
    input  wire load_weight,       // Shift enable for weights
    input  wire signed [15:0] weight_in,
    
    // Pixel input interface
    input  wire mac_en,            // Enable MAC operation
    input  wire clr_acc,           // When mac_en is high, ignores previous accumulator value
    input  wire signed [15:0] pixel_in,
    
    // Output
    output reg  signed [15:0] out_acc,
    output reg  valid_out          // Asserted high on the cycle the 9th tap finishes
);
    // 9 weight registers for a 3x3 kernel (Weight-Stationary)
    reg signed [15:0] weights [0:8];
    reg [3:0] tap_idx; // 0 to 8 counter
    
    wire signed [15:0] mac_result;
    wire signed [15:0] current_weight = weights[tap_idx];
    wire signed [15:0] acc_in = clr_acc ? 16'sd0 : out_acc;
    
    // Instantiation of verified Q7.8 MAC
    mac_q7_8 mac_inst (
        .in_val(pixel_in),
        .weight(current_weight),
        .acc_in(acc_in),
        .acc_out(mac_result)
    );

    always @(posedge clk) begin
        if (reset) begin
            tap_idx   <= 0;
            out_acc   <= 0;
            valid_out <= 0;
            // Note: weights are intentionally not reset to save routing resources
        end else begin
            if (load_weight) begin
                // Shift register for weight loading
                weights[8] <= weights[7];
                weights[7] <= weights[6];
                weights[6] <= weights[5];
                weights[5] <= weights[4];
                weights[4] <= weights[3];
                weights[3] <= weights[2];
                weights[2] <= weights[1];
                weights[1] <= weights[0];
                weights[0] <= weight_in;
            end
            
            if (mac_en) begin
                out_acc <= mac_result;
                
                if (tap_idx == 8) begin
                    tap_idx   <= 0;
                    valid_out <= 1;
                end else begin
                    tap_idx   <= tap_idx + 1;
                    valid_out <= 0;
                end
            end else begin
                valid_out <= 0;
            end
        end
    end
endmodule
```

---

## 8. Verification Results & Hardware Resource Analysis

### 1. Directed Testbench Verification (`tb_conv_pe.v`):
The module was verified using the self-checking testbench `v2/verilog_src/tb_conv_pe.v` compiled with Icarus Verilog:
- **Test Case 1 (Interior $3 \times 3$ Window):** Evaluated 9 non-zero pixel inputs ($P_1 = [0.10, 0.20, \dots, 0.90]$) against signed kernel weights. Expected Q7.8 golden result from Python: `104` ($0.40625$). The RTL simulation output produced `104` (`PASS`).
- **Test Case 2 (Edge $3 \times 3$ Window with Zero-Padding):** Evaluated boundary pixels with zero-padded corner and border positions ($P_2 = [0, 0, 0, 0, 0.50, 0.60, 0, 0.80, 0.90]$). Expected Q7.8 golden result: `19` ($0.0742$). The RTL simulation output produced `19` (`PASS`).
- **Summary:** Zero mismatches detected across directed test cases (`ALL TESTS PASSED.`).

### 2. Critical Path Analysis (Estimated Design Analysis, Unsynthesized):
- **Combinational Critical Path:** `pixel_in` / `current_weight` $\rightarrow$ $16 \times 16$ Multiplier $\rightarrow$ `product[23:8]` Truncation Wiring $\rightarrow$ 16-bit Signed Adder $\rightarrow$ `out_acc` flip-flop setup time.
- **Timing Estimate:** When targeted to typical FPGA fabrics (such as Xilinx Artix-7), the multiplier and adder map directly into a single DSP48E1 slice or equivalent LUT logic. The single-cycle combinational delay is estimated to easily support operating clock frequencies in the range of 100 to 150 MHz without requiring multi-stage pipeline registers.

### 3. Hardware Resource Trade-Off Arithmetic:
Compared to a fully unrolled parallel 2D convolution engine that instantiates 9 multipliers per channel:
$$\text{Multiplier Reduction Ratio} = \frac{9 - 1}{9} = \frac{8}{9} \approx 88.89\%$$

By time-multiplexing a single hardware multiplier across 9 clock cycles, the design reduces multiplier resource requirements by $88.89\%$ per convolutional channel while maintaining deterministic 9-cycle throughput for real-time inference.
