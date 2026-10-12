---
trigger: model_decision
description: Apply these guidelines whenever working on Verilog RTL modules, testbenches, simulation models, or hardware-software co-design interfaces.
---

## Hardware RTL Architecture & Verification Patterns (Verilog-2001 + Icarus Verilog)

### 1. Invariant Digital Design Rules
* **Q7.8 Truncation Discipline:** Every multiply-accumulate (MAC) step must multiply signed 16-bit inputs ($16 \times 16 \rightarrow 32$) and truncate bits $[23:8]$ to return to Q7.8 signed 16-bit format. Never use floating-point or wider word rounding that drifts from physical silicon behavior.
* **Weight-Stationary Dataflow:** Weights are loaded once into shift registers and held stationary. Streaming inputs propagate rhythmically through PEs.
* **Mutual Exclusivity:** Ensure that `load_weight` and `compute` / `mac_en` cannot corrupt accumulator registers on the same clock edge.
* **Time-Multiplexed MLP Head Contract:** The 16×16 systolic array in `mlp_head.v` executes over 2,900 clock cycles, completely hidden within the 6,139-cycle MaxPool2 streaming arrival. Do not alter memory interface timing without re-verifying latency hiding.

### 2. RTL Coding Standards
* **Net Declarations:** Always include `` `default_nettype none `` in testbenches to prevent silent single-bit implicit wire synthesis bugs.
* **Signed Bit Widths:** Explicitly annotate `signed` for all arithmetic wires and registers. Mismatched signed/unsigned comparisons create catastrophic 2's complement bugs.
* **Combinational Memory Access:** The sliding window generator (`window_gen.v`) assumes zero-latency combinational read of `pixel_in` relative to `pixel_addr`.
* **Zero Simulation Bloat:** Never output `.vcd`, `.vvp`, or `.out` simulation files into the tracked source directory (`v2/verilog_src/`). Use temporary build directories.

### 3. Verification & Bit-Exact Emulation
* **Bit-for-Bit Equivalence:** Any architectural change to Verilog modules must be verified against the Python Q7.8 Integer Emulator (`int_emulator_v2.py`) with zero mismatches.
* **Headroom Gate Check:** Never export weights without running the Q7.8 headroom check verifying $\max|\text{logit}| < 127.99$.
