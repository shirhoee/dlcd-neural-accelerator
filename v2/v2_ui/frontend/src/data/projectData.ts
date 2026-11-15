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
    description: "Convolutional Processing Element: 9-tap sequential Multiply-Accumulate unit with stationary weight storage and modulo-9 tap counter (no FSM).",
    verilogFile: "conv_pe.v",
    latencyCycles: "Exactly 9 clock cycles per 3x3 window",
    arithmeticType: "Signed Q7.8 Fixed-Point (prod[23:8] per-step truncation)",
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
      "4-bit modulo-9 binary up-counter (tap_idx 0..8; no FSM)"
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
    latencyCycles: "4,892 clock cycles for complete 20x20 image (400 windows)",
    arithmeticType: "4x parallel Q7.8 sequential MACs (4 multipliers total)",
    fsmName: "conv1_array_fsm",
    ports: [
      { name: "clk", direction: "input", width: "1", description: "System clock" },
      { name: "reset", direction: "input", width: "1", description: "Synchronous reset" },
      { name: "conv1_weights", direction: "input", width: "[575:0]", description: "Flat 4 channels x 9 weights bus" },
      { name: "pixel_addr", direction: "output", width: "[8:0]", description: "Image memory address (0 to 399)" },
      { name: "pixel_in", direction: "input", width: "[15:0]", description: "Streaming input pixel" },
      { name: "out_ch0 .. out_ch3", direction: "output", width: "[15:0]", description: "4-channel parallel convolved pixels" },
      { name: "valid_out", direction: "output", width: "1", description: "Valid output strobe (400 total pulses)" },
      { name: "done", direction: "output", width: "1", description: "Conv1 processing complete strobe" }
    ],
    schematicSummary: [
      "1x window_gen module (47-element shift register line buffer)",
      "4x conv_pe instances (Channel 0 to 3, 4 multipliers)",
      "6-state master FSM (ST_INIT, ST_ADVANCE, ST_FETCH, ST_MAC, ST_WAIT_VALID, ST_DONE)"
    ],
    verilogSnippet: `module conv1_array (
    input wire clk, reset,
    input wire [575:0] conv1_weights,
    output wire [8:0] pixel_addr,
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
    latencyCycles: "1,244 clock cycles (100 windows across 4 channels)",
    arithmeticType: "4-input adder trees with Q7.8 sequential MACs (32 multipliers total)",
    fsmName: "conv2_array_fsm",
    ports: [
      { name: "clk, reset, valid_in", direction: "input", width: "1", description: "Control strobes" },
      { name: "in_ch0 .. in_ch3", direction: "input", width: "[15:0]", description: "4-channel streaming inputs from MaxPool1" },
      { name: "conv2_weights", direction: "input", width: "[4607:0]", description: "Flat 288 weights bus (8 out x 4 in x 9 taps)" },
      { name: "out_ch0 .. out_ch7", direction: "output", width: "[15:0]", description: "8-channel convolved outputs" },
      { name: "valid_out", direction: "output", width: "1", description: "Valid output strobe (100 total pulses)" },
      { name: "done", direction: "output", width: "1", description: "Conv2 processing complete strobe" }
    ],
    schematicSummary: [
      "8x conv2_pe instances (32 multipliers total)",
      "Each PE instantiates 4x parallel mac_q7_8 units",
      "4-channel combinational adder tree per PE",
      "100-word input shift register buffer for stream gaps",
      "6-state master FSM (ST_LOAD, ST_FETCH, ST_MAC, ST_WAIT_VALID, ST_ADVANCE, ST_DONE)"
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
    latencyCycles: "2,977 clock cycles integrated in v2_top (2,978 standalone; 62 tiles @ 48 cyc/tile + 1 idle)",
    arithmeticType: "16x16 2D Systolic Matrix Multiplier with Weight-Stationary Dataflow (256 multipliers)",
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
      "Fused ReLU activation feedback on hidden layer outputs"
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
    latencyCycles: "32 cycles compute + 16 cycles load per 16x16 matrix tile (48 cycles/tile)",
    arithmeticType: "Weight-Stationary systolic dataflow (256 multipliers)",
    ports: [
      { name: "clk, rst, load_weight", direction: "input", width: "1", description: "Clock and mode controls" },
      { name: "weight_in_left", direction: "input", width: "[255:0]", description: "16x 16-bit weights loaded from left edge (shift right)" },
      { name: "in_val_top", direction: "input", width: "[255:0]", description: "16x 16-bit activations streamed from top edge (shift down)" },
      { name: "acc_out_right", direction: "output", width: "[255:0]", description: "16x 16-bit accumulated partial sums from right edge" }
    ],
    schematicSummary: [
      "16x16 2D mesh of systolic_pe modules (256 MAC units)",
      "Horizontal weight loading shift registers (w_wire[r][c] -> w_wire[r][c+1])",
      "Vertical activation pipelining registers (x_wire[r][c] -> x_wire[r+1][c])",
      "Horizontal partial sum accumulation (y_wire[r][c] -> y_wire[r][c+1])"
    ],
    verilogSnippet: `module systolic_array #(parameter ROWS=16, COLS=16) (
    input wire clk, rst, load_weight,
    input wire [(ROWS*16)-1:0] weight_in_left,
    input wire [(COLS*16)-1:0] in_val_top,
    output wire [(ROWS*16)-1:0] acc_out_right
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
    id: "conv1_array_fsm",
    title: "Conv1 Array 6-State Master Sequencer",
    module: "conv1_array.v",
    cycleBudget: "4,892 cycles total (400 spatial windows across 20x20 input)",
    states: [
      { name: "ST_INIT", desc: "Reset active: Shift-load 36 weights (9 taps x 4 channels) into PEs via tap_load_idx counter (0 to 8).", isInitial: true },
      { name: "ST_ADVANCE", desc: "Mandatory 1-cycle pipeline shift strobe to move line buffer past completed receptive window." },
      { name: "ST_FETCH", desc: "Pump line buffer advance strobe until window_gen asserts window_valid." },
      { name: "ST_MAC", desc: "9-cycle sequential MAC execution across 4 parallel conv_pe units; clr_acc on cycle 0, mac_en active." },
      { name: "ST_WAIT_VALID", desc: "Sample synchronized valid_out from conv_pe instances; strobe valid_out to MaxPool1." },
      { name: "ST_DONE", desc: "All 400 window convolutions complete; assert done strobe to top-level controller.", isFinal: true }
    ],
    transitions: [
      { from: "ST_INIT", to: "ST_FETCH", condition: "init_cnt == 8", action: "Transition to ST_FETCH once weights are preloaded" },
      { from: "ST_ADVANCE", to: "ST_FETCH", condition: "1 clock cycle pulse", action: "Unconditionally advance to ST_FETCH" },
      { from: "ST_FETCH", to: "ST_MAC", condition: "win_valid == 1", action: "Begin 9-cycle MAC accumulation (mac_cnt <= 0)" },
      { from: "ST_MAC", to: "ST_WAIT_VALID", condition: "mac_cnt == 8", action: "Accumulation complete; latch final product" },
      { from: "ST_WAIT_VALID", to: "ST_DONE", condition: "win_done == 1", action: "Final window completed; assert done" },
      { from: "ST_WAIT_VALID", to: "ST_ADVANCE", condition: "!win_done", action: "Shift window buffer for next coordinate" },
      { from: "ST_DONE", to: "ST_DONE", condition: "Held until reset", action: "Static completed state" }
    ]
  },
  {
    id: "conv2_array_fsm",
    title: "Conv2 Array 6-State Multichannel Controller",
    module: "conv2_array.v",
    cycleBudget: "1,244 cycles total (100 spatial windows across 4 channels to 8 filters)",
    states: [
      { name: "ST_LOAD", desc: "Buffer 100 features from MaxPool1 across 4 channels into buf_ch0..buf_ch3 (write_addr 0 to 99).", isInitial: true },
      { name: "ST_FETCH", desc: "Await window generator valid strobe (w_valid) for 3x3 receptive field in 10x10 feature maps." },
      { name: "ST_MAC", desc: "Execute 9-cycle sequential MAC across 8 filter groups (32 multipliers active in parallel)." },
      { name: "ST_WAIT_VALID", desc: "Sum 4-channel products through adder tree; register 8-channel convolved outputs; strobe valid_out." },
      { name: "ST_ADVANCE", desc: "Advance spatial coordinate counters across 10x10 input feature maps." },
      { name: "ST_DONE", desc: "All 100 convolved spatial vectors computed; assert done strobe.", isFinal: true }
    ],
    transitions: [
      { from: "ST_LOAD", to: "ST_FETCH", condition: "write_addr == 99 && valid_in", action: "Input buffer filled; begin spatial convolution" },
      { from: "ST_FETCH", to: "ST_MAC", condition: "w_valid == 1", action: "Receptive window ready; start MACs (mac_cnt <= 0)" },
      { from: "ST_MAC", to: "ST_WAIT_VALID", condition: "mac_cnt == 8", action: "9 taps accumulated; route to adder tree" },
      { from: "ST_WAIT_VALID", to: "ST_DONE", condition: "w_done == 1", action: "Final 100th window processed; assert done" },
      { from: "ST_WAIT_VALID", to: "ST_ADVANCE", condition: "!w_done", action: "Advance to next spatial window" },
      { from: "ST_ADVANCE", to: "ST_FETCH", condition: "1 clock cycle pulse", action: "Fetch next receptive field taps" },
      { from: "ST_DONE", to: "ST_DONE", condition: "Held until reset", action: "Static completed state" }
    ]
  },
  {
    id: "mlp_head_fsm",
    title: "Systolic MLP Head 4-State Time-Multiplexed Controller",
    module: "mlp_head.v",
    cycleBudget: "2,977 cycles inside v2_top (Layer 1: 2,496, Layer 2: 384, Layer 3: 96, + 1 idle)",
    states: [
      { name: "IDLE", desc: "Buffering 200 input features from MaxPool2 into ram_A; write_ptr advances by 8 per valid pulse.", isInitial: true },
      { name: "LOAD_WEIGHT", desc: "Shift-loading 16x16 weight matrix tile from mlp_rom into systolic array (timer counts 0 to 15, 16 cycles).", isInitial: false },
      { name: "COMPUTE", desc: "Streaming activation vectors through systolic mesh (timer 0..31, 32 cycles); collecting outputs, applying fused ReLU, writing to ping-pong RAM.", isInitial: false },
      { name: "DONE", desc: "Assert valid_out strobe; final 10 logits ready on out_digit_0..out_digit_9.", isFinal: true }
    ],
    transitions: [
      { from: "IDLE", to: "LOAD_WEIGHT", condition: "write_ptr == 192 && valid_in", action: "layer <= 1, r_idx <= 0, c_idx <= 0, rom_addr <= 0" },
      { from: "LOAD_WEIGHT", to: "COMPUTE", condition: "timer == 15", action: "Weights latched; timer <= 0, state <= COMPUTE" },
      { from: "COMPUTE", to: "LOAD_WEIGHT", condition: "timer == 31 && !last_tile", action: "Advance tile/column index, load next weight tile" },
      { from: "COMPUTE", to: "DONE", condition: "timer == 31 && layer == 3 && c_idx == 1", action: "valid_out <= 1, state <= DONE" },
      { from: "DONE", to: "IDLE", condition: "Held until reset", action: "Classification complete; awaiting next image" }
    ]
  }
];

export const V1_V2_COMPARISON_METRICS = {
  v1: {
    name: "Version 1 (Baseline MLP)",
    architecture: "100 -> 16 -> 6 -> 10 (3 Dense Layers)",
    inputResolution: "10x10 (100 pixels)",
    accuracy: "93.06% (10k test set) / 95.39% (validation subset)",
    multipliers: "256 (16x16 Systolic Array)",
    cycles: "159 clock cycles (259 total with 100-cycle preload)",
    latency: "1.59 µs compute / 2.59 µs total (@ 100 MHz)",
    spatialFeatures: "None (Global flattening loses 2D local context)",
    noiseTolerance: "Low (Sensitive to 1-pixel shifts and stroke variations)"
  },
  v2: {
    name: "Version 2 (CNN + Systolic Head)",
    architecture: "400 -> Conv1 (4 ch) -> MP1 -> Conv2 (8 ch) -> MP2 -> 200 -> 64 -> 32 -> 10",
    inputResolution: "20x20 (400 pixels)",
    accuracy: "98.70% (Bit-exact Q7.8 Hardware) / 98.83% (PyTorch FP32)",
    multipliers: "292 Leaf Multipliers (256 Systolic + 32 Conv2 + 4 Conv1)",
    cycles: "9,116 clock cycles",
    latency: "91.16 µs (@ 100 MHz; 10,969.7 FPS)",
    spatialFeatures: "High (2D 3x3 receptive fields, translation invariance)",
    noiseTolerance: "Very High (Tolerant to stroke thickness, position, and noise)"
  }
};
