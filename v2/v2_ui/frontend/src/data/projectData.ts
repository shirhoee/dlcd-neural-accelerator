import { TeamMember, CircuitModule, FsmDefinition } from '../types/api';

export const TEAM_MEMBERS: TeamMember[] = [
  {
    name: "Shreyansh Raj",
    srn: "PES2UG25CS516",
    role: "Lead Hardware Architect & RTL Verification",
    avatar: "SR"
  },
  {
    name: "Sarthak Bhowmik",
    srn: "PES2UG25CS493",
    role: "Digital Datapath & Systolic Array Design",
    avatar: "SB"
  },
  {
    name: "Shaurya Singh",
    srn: "PES2UG25CS508",
    role: "Convolutional PE & Line Buffer Subsystems",
    avatar: "SS"
  },
  {
    name: "Shreya Anand",
    srn: "PES2UG25CS515",
    role: "Q7.8 Quantization & Fixed-Point Golden Models",
    avatar: "SA"
  }
];

export const CIRCUIT_MODULES: CircuitModule[] = [
  {
    id: "window_gen",
    name: "window_gen",
    category: "input",
    description: "Sliding-Window Generator: Maps 20x20 input stream to 3x3 receptive fields with zero-latency combinational output.",
    verilogFile: "window_gen.v",
    latencyCycles: "1 cycle per pixel (400 cycles total)",
    arithmeticType: "Pass-through 16-bit shift register",
    ports: [
      { name: "clk", direction: "input", width: "1", description: "Primary system clock" },
      { name: "reset", direction: "input", width: "1", description: "Synchronous reset" },
      { name: "pixel_in", direction: "input", width: "[15:0]", description: "Incoming stream pixel (Q7.8)" },
      { name: "win_0 .. win_8", direction: "output", width: "[15:0]", description: "Parallel 3x3 receptive window outputs" },
      { name: "valid_out", direction: "output", width: "1", description: "Window valid strobe" }
    ],
    schematicSummary: [
      "47-element shift-register line buffer",
      "Virtual 22x22 zero-padded boundary muxes",
      "Combinational 9-word parallel output tap bus"
    ],
    verilogSnippet: `module window_gen (
    input wire clk, reset, valid_in,
    input wire signed [15:0] pixel_in,
    output reg signed [15:0] win_0, win_1, win_2,
    output reg signed [15:0] win_3, win_4, win_5,
    output reg signed [15:0] win_6, win_7, win_8,
    output reg valid_out
);`
  },
  {
    id: "conv_pe",
    name: "conv_pe",
    category: "conv1",
    description: "Convolutional Processing Element: 9-tap sequential Multiply-Accumulate unit with stationary weight storage.",
    verilogFile: "conv_pe.v",
    latencyCycles: "Exactly 9 clock cycles per 3x3 window",
    arithmeticType: "Signed Q7.8 Fixed-Point (prod[23:8] per-step truncation)",
    fsmName: "conv_pe_fsm",
    ports: [
      { name: "clk", direction: "input", width: "1", description: "System clock" },
      { name: "reset", direction: "input", width: "1", description: "Synchronous reset" },
      { name: "load_weight", direction: "input", width: "1", description: "Active-high shift enable for weight loading" },
      { name: "weight_in", direction: "input", width: "[15:0]", description: "Serial weight stream during config" },
      { name: "mac_en", direction: "input", width: "1", description: "MAC computation clock enable" },
      { name: "clr_acc", direction: "input", width: "1", description: "Synchronous clear for accumulator feedback" },
      { name: "pixel_in", direction: "input", width: "[15:0]", description: "Streaming window pixel (Q7.8)" },
      { name: "out_acc", direction: "output", width: "[15:0]", description: "Accumulated convolution sum" },
      { name: "valid_out", direction: "output", width: "1", description: "Active-high output valid strobe" }
    ],
    schematicSummary: [
      "9x 16-bit weight shift registers (W0..W8)",
      "16-bit 9:1 multiplexer addressed by tap_idx",
      "16x16 signed multiplier -> 32-bit product",
      "Fixed-point truncator: prod[23:8]",
      "16-bit signed accumulator adder + feedback reg",
      "4-bit modulo-9 binary up-counter"
    ],
    verilogSnippet: `module conv_pe (
    input wire clk, reset, load_weight, mac_en, clr_acc,
    input wire signed [15:0] weight_in, pixel_in,
    output reg signed [15:0] out_acc,
    output reg valid_out
);`
  },
  {
    id: "mac_q7_8",
    name: "mac_q7_8",
    category: "conv1",
    description: "Sequential Multiply-Accumulate Unit: Multiplies two Q7.8 16-bit numbers, shifts by 8 bits, and accumulates into 16-bit sum.",
    verilogFile: "mac_q7_8.v",
    latencyCycles: "1 clock cycle",
    arithmeticType: "Signed Q7.8 (1 sign, 7 integer, 8 fractional bits)",
    ports: [
      { name: "a", direction: "input", width: "[15:0]", description: "Signed 16-bit multiplier input A (Q7.8)" },
      { name: "b", direction: "input", width: "[15:0]", description: "Signed 16-bit multiplier input B (Q7.8)" },
      { name: "c", direction: "input", width: "[15:0]", description: "Signed 16-bit accumulator feedback (Q7.8)" },
      { name: "out", direction: "output", width: "[15:0]", description: "Truncated accumulated output: c + (a*b)[23:8]" }
    ],
    schematicSummary: [
      "16-bit x 16-bit signed multiplier (32-bit output)",
      "Bit slicer: [23:8] restores Q7.8 fractional alignment",
      "16-bit signed 2's complement adder"
    ],
    verilogSnippet: `module mac_q7_8 (
    input wire signed [15:0] a, b, c,
    output wire signed [15:0] out
);
    wire signed [31:0] prod = a * b;
    wire signed [15:0] prod_q7_8 = prod[23:8];
    assign out = c + prod_q7_8;
endmodule`
  },
  {
    id: "conv1_array",
    name: "conv1_array",
    category: "conv1",
    description: "4-Channel Parallel Convolution Array: Wraps window_gen and 4 conv_pe instances computing 4 channels in parallel.",
    verilogFile: "conv1_array.v",
    latencyCycles: "4,894 clock cycles for complete 20x20 image",
    arithmeticType: "4x parallel Q7.8 sequential MACs",
    ports: [
      { name: "clk", direction: "input", width: "1", description: "System clock" },
      { name: "reset", direction: "input", width: "1", description: "Synchronous reset" },
      { name: "conv1_weights", direction: "input", width: "[575:0]", description: "Flat 4 channels x 9 weights bus" },
      { name: "pixel_in", direction: "input", width: "[15:0]", description: "Streaming input pixel" },
      { name: "out_ch0 .. out_ch3", direction: "output", width: "[15:0]", description: "4-channel parallel convolved pixels" },
      { name: "valid_out", direction: "output", width: "1", description: "Valid output strobe (400 total pulses)" }
    ],
    schematicSummary: [
      "1x window_gen module",
      "4x conv_pe instances (Channel 0 to 3)",
      "Master sequencer generating clr_acc on Tap 0"
    ],
    verilogSnippet: `module conv1_array (
    input wire clk, reset,
    input wire [575:0] conv1_weights,
    input wire signed [15:0] pixel_in,
    output wire signed [15:0] out_ch0, out_ch1, out_ch2, out_ch3,
    output wire valid_out, done
);`
  },
  {
    id: "maxpool_pe",
    name: "maxpool_pe",
    category: "pool1",
    description: "2x2 Signed Pooling PE: Purely combinational 4-way comparator finding the maximum signed Q7.8 value among 4 inputs.",
    verilogFile: "maxpool_pe.v",
    latencyCycles: "Combinational (0 cycles)",
    arithmeticType: "Signed 16-bit 2's complement comparisons ($signed)",
    ports: [
      { name: "in0, in1, in2, in3", direction: "input", width: "[15:0]", description: "4 pixels of the 2x2 spatial window" },
      { name: "out_max", direction: "output", width: "[15:0]", description: "Maximum signed pixel value" }
    ],
    schematicSummary: [
      "2-stage binary tree of signed 16-bit comparators",
      "Deterministic lower-index tie-breaking logic"
    ],
    verilogSnippet: `module maxpool_pe (
    input wire signed [15:0] in0, in1, in2, in3,
    output wire signed [15:0] out_max
);
    wire signed [15:0] max_row0 = (in0 >= in1) ? in0 : in1;
    wire signed [15:0] max_row1 = (in2 >= in3) ? in2 : in3;
    assign out_max = (max_row0 >= max_row1) ? max_row0 : max_row1;
endmodule`
  },
  {
    id: "relu_q7_8",
    name: "relu_q7_8",
    category: "pool1",
    description: "Combinational Rectified Linear Unit: Passes positive Q7.8 values and clamps negative values to 16'sd0.",
    verilogFile: "relu_q7_8.v",
    latencyCycles: "Combinational (0 cycles)",
    arithmeticType: "Non-linear zero clamping on sign bit",
    ports: [
      { name: "in_val", direction: "input", width: "[15:0]", description: "Signed 16-bit input" },
      { name: "out_val", direction: "output", width: "[15:0]", description: "max(0, in_val)" }
    ],
    schematicSummary: [
      "Sign-bit detection: in_val[15]",
      "2:1 multiplexer selecting between 16'd0 and in_val"
    ],
    verilogSnippet: `module relu_q7_8 (
    input wire signed [15:0] in_val,
    output wire signed [15:0] out_val
);
    assign out_val = (in_val[15] == 1'b1) ? 16'sd0 : in_val;
endmodule`
  },
  {
    id: "conv2_array",
    name: "conv2_array",
    category: "conv2",
    description: "Conv2 Array Subsystem: 8 parallel PEs with 4-channel adder trees convolving 4 input channels to 8 output channels.",
    verilogFile: "conv2_array.v",
    latencyCycles: "1,072 clock cycles",
    arithmeticType: "4-input adder trees with Q7.8 sequential MACs",
    ports: [
      { name: "clk, reset, valid_in", direction: "input", width: "1", description: "Control strobes" },
      { name: "in_ch0 .. in_ch3", direction: "input", width: "[15:0]", description: "4-channel streaming inputs from MaxPool1" },
      { name: "conv2_weights", direction: "input", width: "[4607:0]", description: "Flat 288 weights bus (8 out x 4 in x 9 taps)" },
      { name: "out_ch0 .. out_ch7", direction: "output", width: "[15:0]", description: "8-channel convolved outputs" },
      { name: "valid_out", direction: "output", width: "1", description: "Valid output strobe (100 total pulses)" }
    ],
    schematicSummary: [
      "8x conv2_pe instances",
      "Each PE instantiates 4x parallel mac_q7_8 units",
      "4-channel combinational adder tree per PE",
      "100-word input shift register buffer for stream gaps"
    ],
    verilogSnippet: `module conv2_array (
    input wire clk, reset, valid_in,
    input wire signed [15:0] in_ch0, in_ch1, in_ch2, in_ch3,
    input wire [4607:0] conv2_weights,
    output wire signed [15:0] out_ch0, out_ch1, out_ch2, out_ch3,
    output wire signed [15:0] out_ch4, out_ch5, out_ch6, out_ch7,
    output wire valid_out, done
);`
  },
  {
    id: "mlp_head",
    name: "mlp_head",
    category: "mlp",
    description: "Time-Multiplexed Systolic MLP Head: Reuses 16x16 systolic array across 200->64->32->10 using dual ping-pong RAMs.",
    verilogFile: "mlp_head.v",
    latencyCycles: "2,978 clock cycles (runs concurrently with Conv2/MaxPool2 pipeline)",
    arithmeticType: "16x16 2D Systolic Matrix Multiplier with Weight-Stationary Dataflow",
    fsmName: "mlp_head_fsm",
    ports: [
      { name: "clk, reset, valid_in", direction: "input", width: "1", description: "System control strobes" },
      { name: "in_ch0 .. in_ch7", direction: "input", width: "[15:0]", description: "8 streaming channels from MaxPool2" },
      { name: "out_digit_0 .. out_digit_9", direction: "output", width: "[15:0]", description: "10 final output logits" },
      { name: "valid_out", direction: "output", width: "1", description: "Inference complete strobe" }
    ],
    schematicSummary: [
      "Dual Ping-Pong RAMs: ram_A (208 words), ram_B (64 words)",
      "1x 16x16 systolic_array (256 MAC units total)",
      "992-word 256-bit weight ROM (mlp_rom.txt)",
      "4-state FSM controller (IDLE, LOAD_WEIGHT, COMPUTE, DONE)",
      "Fused ReLU activation feedback"
    ],
    verilogSnippet: `module mlp_head (
    input wire clk, reset, valid_in,
    input wire signed [15:0] in_ch0, in_ch1, in_ch2, in_ch3,
    input wire signed [15:0] in_ch4, in_ch5, in_ch6, in_ch7,
    output wire signed [15:0] out_digit_0, ..., out_digit_9,
    output reg valid_out
);`
  },
  {
    id: "systolic_array",
    name: "systolic_array",
    category: "mlp",
    description: "16x16 2D Systolic Array: 256 interconnected Processing Elements in a grid performing 2D matrix multiplication with zero bus contention.",
    verilogFile: "systolic_array.v",
    latencyCycles: "32 cycles per 16x16 matrix tile",
    arithmeticType: "Weight-Stationary systolic dataflow",
    ports: [
      { name: "clk, reset, load_weight", direction: "input", width: "1", description: "Clock and mode controls" },
      { name: "weight_in_left", direction: "input", width: "[255:0]", description: "16x 16-bit weights loaded from left edge" },
      { name: "in_val_top", direction: "input", width: "[255:0]", description: "16x 16-bit activations streamed from top edge" },
      { name: "acc_out_right", direction: "output", width: "[255:0]", description: "16x 16-bit accumulated partial sums from right edge" }
    ],
    schematicSummary: [
      "16x16 2D mesh of systolic_pe modules",
      "Horizontal weight loading shift registers",
      "Vertical activation pipelining registers",
      "Horizontal accumulation adder pipeline"
    ],
    verilogSnippet: `module systolic_array #(parameter ROWS=16, COLS=16) (
    input wire clk, reset, load_weight,
    input wire [ROWS*16-1:0] weight_in_left,
    input wire [COLS*16-1:0] in_val_top,
    output wire [ROWS*16-1:0] acc_out_right
);`
  },
  {
    id: "argmax",
    name: "argmax",
    category: "output",
    description: "Argmax Layer: Purely combinational 4-stage binary comparison tree selecting winning digit index [0-9] from 10 signed logits.",
    verilogFile: "argmax.v",
    latencyCycles: "1 clock cycle (pipelined output register)",
    arithmeticType: "Signed 16-bit comparisons with lower-index tie-breaking",
    ports: [
      { name: "clk, reset, valid_in", direction: "input", width: "1", description: "Clock and latch enable" },
      { name: "in_0 .. in_9", direction: "input", width: "[15:0]", description: "10 signed Q7.8 logits" },
      { name: "prediction", direction: "output", width: "[3:0]", description: "Predicted digit index (0 to 9)" },
      { name: "valid_out", direction: "output", width: "1", description: "Prediction ready pulse" }
    ],
    schematicSummary: [
      "4-stage binary tree of signed comparators",
      "Deterministic lower-index priority encoding",
      "1-cycle registered output buffer"
    ],
    verilogSnippet: `module argmax (
    input wire clk, reset, valid_in,
    input wire signed [15:0] in_0, in_1, ..., in_9,
    output reg [3:0] prediction,
    output reg valid_out
);`
  },
  {
    id: "v2_top",
    name: "v2_top",
    category: "output",
    description: "Top-Level Pipelined CNN Accelerator Wrapper: Interlocks all 6 layers behind standard control interface (clk, reset, start, pixel_in, prediction, done).",
    verilogFile: "v2_top.v",
    latencyCycles: "Exactly 9,116 clock cycles (91.16 µs at 100 MHz)",
    arithmeticType: "End-to-End Q7.8 Signed Fixed-Point CNN Accelerator",
    ports: [
      { name: "clk, reset, start", direction: "input", width: "1", description: "Global clock, reset, and start strobes" },
      { name: "pixel_addr", direction: "output", width: "[8:0]", description: "Address for streaming input pixel (0 to 399)" },
      { name: "pixel_in", direction: "input", width: "[15:0]", description: "Streaming input pixel from memory" },
      { name: "prediction", direction: "output", width: "[3:0]", description: "Final classified digit (0-9)" },
      { name: "done", direction: "output", width: "1", description: "Asserted high when classification is complete" }
    ],
    schematicSummary: [
      "Instantiates Conv1, MaxPool1, Conv2, MaxPool2, MLP Head, and Argmax",
      "Self-contained Weight ROMs: conv1_rom (36), conv2_rom (288)",
      "Zero-latency handshake interlocking throughout pipeline"
    ],
    verilogSnippet: `module v2_top (
    input wire clk, reset, start,
    output reg [8:0] pixel_addr,
    input wire signed [15:0] pixel_in,
    output wire [3:0] prediction,
    output wire done
);`
  }
];

export const FSM_DEFINITIONS: FsmDefinition[] = [
  {
    id: "conv_pe_fsm",
    title: "Conv PE 9-Tap Sequential MAC Finite State Machine",
    module: "conv_pe.v",
    cycleBudget: "9 cycles per window",
    states: [
      { name: "IDLE", desc: "Awaiting mac_en strobe; accumulator and tap counter held static.", isInitial: true },
      { name: "TAP_0", desc: "Clear accumulator feedback (clr_acc = 1), multiply Tap 0 weight with incoming pixel." },
      { name: "TAP_1_7", desc: "Accumulate taps 1 through 7 sequentially, tap_idx increments on each rising clock edge." },
      { name: "TAP_8", desc: "Final 9th tap MAC; assert valid_out strobe on the following clock cycle.", isFinal: true }
    ],
    transitions: [
      { from: "IDLE", to: "TAP_0", condition: "mac_en == 1 && clr_acc == 1", action: "tap_idx <= 1, out_acc <= prod[23:8]" },
      { from: "TAP_0", to: "TAP_1_7", condition: "mac_en == 1", action: "tap_idx <= tap_idx + 1, out_acc <= out_acc + prod" },
      { from: "TAP_1_7", to: "TAP_8", condition: "tap_idx == 8", action: "valid_out <= 1" },
      { from: "TAP_8", to: "TAP_0", condition: "clr_acc == 1", action: "Reset tap_idx to 0 for next window" }
    ]
  },
  {
    id: "mlp_head_fsm",
    title: "Systolic MLP Head 4-State Time-Multiplexed Controller",
    module: "mlp_head.v",
    cycleBudget: "2,978 cycles total (Layer 1: 1,664, Layer 2: 768, Layer 3: 546)",
    states: [
      { name: "IDLE", desc: "Buffering 200 input features from MaxPool2 into ram_A; write_ptr advances by 8 per valid pulse.", isInitial: true },
      { name: "LOAD_WEIGHT", desc: "Shift-loading 16x16 weight matrix tile from mlp_rom.txt into systolic array (timer counts 0 to 15)." },
      { name: "COMPUTE", desc: "Streaming activation vectors through systolic mesh; collecting right-edge outputs, applying fused ReLU, writing to ping-pong RAM." },
      { name: "DONE", desc: "Assert valid_out strobe; final 10 logits ready on out_digit_0..out_digit_9.", isFinal: true }
    ],
    transitions: [
      { from: "IDLE", to: "LOAD_WEIGHT", condition: "write_ptr == 192 && valid_in", action: "layer <= 1, state <= LOAD_WEIGHT" },
      { from: "LOAD_WEIGHT", to: "COMPUTE", condition: "timer == 15", action: "timer <= 0, state <= COMPUTE" },
      { from: "COMPUTE", to: "LOAD_WEIGHT", condition: "timer == 31 && !last_tile", action: "Advance tile index, load next weights" },
      { from: "COMPUTE", to: "DONE", condition: "timer == 31 && layer == 3 && last_tile", action: "valid_out <= 1, state <= DONE" },
      { from: "DONE", to: "IDLE", condition: "1 clock cycle pulse", action: "Return to IDLE for next image" }
    ]
  }
];

export const V1_V2_COMPARISON_METRICS = {
  v1: {
    name: "Version 1 (Baseline MLP)",
    architecture: "100 -> 16 -> 6 -> 10 (3 Dense Layers)",
    inputResolution: "10x10 (100 pixels)",
    accuracy: "93.06%",
    multipliers: "256 (16x16 Systolic Array)",
    cycles: "6,139 clock cycles",
    latency: "61.39 µs (@ 100 MHz)",
    spatialFeatures: "None (Global flattening loses 2D local context)",
    noiseTolerance: "Low (Sensitive to 1-pixel shifts and stroke variations)"
  },
  v2: {
    name: "Version 2 (CNN + Systolic Head)",
    architecture: "400 -> Conv1 (4 ch) -> MP1 -> Conv2 (8 ch) -> MP2 -> 200 -> 64 -> 32 -> 10",
    inputResolution: "20x20 (400 pixels)",
    accuracy: "98.83%",
    multipliers: "256 (Reused V1 Systolic Array via Time-Multiplexing!)",
    cycles: "9,116 clock cycles",
    latency: "91.16 µs (@ 100 MHz)",
    spatialFeatures: "High (2D 3x3 receptive fields, translation invariance)",
    noiseTolerance: "Very High (Tolerant to stroke thickness, position, and noise)"
  }
};
