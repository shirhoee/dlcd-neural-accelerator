`timescale 1ns / 1ps

/*
 * V2 - N3b: Conv1 Array
 * Instantiates 1 window_gen and 4 conv_pe modules to process a full Conv1 layer.
 * 
 * ==========================================
 * INTERFACE CONTRACT: BIT-SLICING CONVENTION
 * ==========================================
 * The flat input bus `conv1_weights [575:0]` contains 36 weights (4 channels x 9 taps).
 * Bit-slicing is organized by channel, then by tap order:
 * 
 * Channels:
 * - Channel 0: Bits [143:0]
 * - Channel 1: Bits [287:144]
 * - Channel 2: Bits [431:288]
 * - Channel 3: Bits [575:432]
 * 
 * Taps within each Channel (e.g. for Channel 0):
 * - Tap 0 (Top-Left)     : [15:0]
 * - Tap 1 (Top-Mid)      : [31:16]
 * - Tap 2 (Top-Right)    : [47:32]
 * - Tap 3 (Mid-Left)     : [63:48]
 * - Tap 4 (Center)       : [79:64]
 * - Tap 5 (Mid-Right)    : [95:80]
 * - Tap 6 (Bottom-Left)  : [111:96]
 * - Tap 7 (Bottom-Mid)   : [127:112]
 * - Tap 8 (Bottom-Right) : [143:128]
 * 
 * The weight-stationary conv_pe expects to shift in Tap 8 first, down to Tap 0,
 * so this module explicitly muxes `tap_load_idx = 8 - init_cnt` during ST_INIT.
 */

module conv1_array (
    input wire clk,
    input wire reset,
    
    // Weight delivery (Flat 576-bit bus, see contract above)
    input wire [575:0] conv1_weights,
    
    // Memory Contract Interface (Combinational Image ROM)
    output wire [8:0] pixel_addr,
    input wire signed [15:0] pixel_in,
    
    // Streaming Output
    output wire signed [15:0] out_ch0,
    output wire signed [15:0] out_ch1,
    output wire signed [15:0] out_ch2,
    output wire signed [15:0] out_ch3,
    output wire valid_out,
    output wire done
);

    // FSM States
    localparam ST_INIT       = 3'd0; // Load weights into 4 PEs (9 cycles)
    localparam ST_ADVANCE    = 3'd1; // Mandatory 1-cycle pipeline shift to move past completed window
    localparam ST_FETCH      = 3'd2; // Pump advance until window_gen asserts window_valid
    localparam ST_MAC        = 3'd3; // 9-cycle accumulation across all 4 PEs
    localparam ST_WAIT_VALID = 3'd4; // 1-cycle wait for conv_pe valid_out
    localparam ST_DONE       = 3'd5; // Done

    reg [2:0] state;
    reg [3:0] init_cnt; // 0 to 8
    reg [3:0] mac_cnt;  // 0 to 8

    // Window Generator Signals
    wire win_advance;
    wire win_valid;
    wire win_done;
    
    wire signed [15:0] win_out [0:8];
    
    window_gen u_window_gen (
        .clk(clk),
        .reset(reset),
        .advance(win_advance),
        .pixel_addr(pixel_addr),
        .pixel_in(pixel_in),
        .out_0(win_out[0]),
        .out_1(win_out[1]),
        .out_2(win_out[2]),
        .out_3(win_out[3]),
        .out_4(win_out[4]),
        .out_5(win_out[5]),
        .out_6(win_out[6]),
        .out_7(win_out[7]),
        .out_8(win_out[8]),
        .window_valid(win_valid),
        .done(win_done)
    );

    // Control wiring
    assign win_advance = (state == ST_ADVANCE) || (state == ST_FETCH && !win_valid);
    
    wire mac_en_sig  = (state == ST_MAC);
    wire clr_acc_sig = (state == ST_MAC && mac_cnt == 0);
    wire load_wt_sig = (state == ST_INIT);

    // Muxing 9-parallel window outputs to 1 serial stream for PEs
    reg signed [15:0] pixel_to_pe;
    always @(*) begin
        if (mac_cnt <= 8) pixel_to_pe = win_out[mac_cnt];
        else pixel_to_pe = 16'd0;
    end

    // Muxing weights during ST_INIT (Tap 8 down to Tap 0)
    wire [3:0] tap_load_idx = 8 - init_cnt;
    wire [15:0] w0 = conv1_weights[ (0 * 144) + (tap_load_idx * 16) +: 16 ];
    wire [15:0] w1 = conv1_weights[ (1 * 144) + (tap_load_idx * 16) +: 16 ];
    wire [15:0] w2 = conv1_weights[ (2 * 144) + (tap_load_idx * 16) +: 16 ];
    wire [15:0] w3 = conv1_weights[ (3 * 144) + (tap_load_idx * 16) +: 16 ];

    wire pe_valid [0:3];
    
    // PE Instances
    conv_pe pe0 (
        .clk(clk), .reset(reset),
        .load_weight(load_wt_sig), .weight_in(w0),
        .mac_en(mac_en_sig), .clr_acc(clr_acc_sig),
        .pixel_in(pixel_to_pe),
        .out_acc(out_ch0), .valid_out(pe_valid[0])
    );

    conv_pe pe1 (
        .clk(clk), .reset(reset),
        .load_weight(load_wt_sig), .weight_in(w1),
        .mac_en(mac_en_sig), .clr_acc(clr_acc_sig),
        .pixel_in(pixel_to_pe),
        .out_acc(out_ch1), .valid_out(pe_valid[1])
    );

    conv_pe pe2 (
        .clk(clk), .reset(reset),
        .load_weight(load_wt_sig), .weight_in(w2),
        .mac_en(mac_en_sig), .clr_acc(clr_acc_sig),
        .pixel_in(pixel_to_pe),
        .out_acc(out_ch2), .valid_out(pe_valid[2])
    );

    conv_pe pe3 (
        .clk(clk), .reset(reset),
        .load_weight(load_wt_sig), .weight_in(w3),
        .mac_en(mac_en_sig), .clr_acc(clr_acc_sig),
        .pixel_in(pixel_to_pe),
        .out_acc(out_ch3), .valid_out(pe_valid[3])
    );

    // Outputs
    assign valid_out = pe_valid[0]; // All 4 PEs are synchronized perfectly
    assign done = (state == ST_DONE);

    // Master FSM
    always @(posedge clk) begin
        if (reset) begin
            state <= ST_INIT;
            init_cnt <= 0;
            mac_cnt <= 0;
        end else begin
            case (state)
                ST_INIT: begin
                    if (init_cnt == 8) state <= ST_FETCH;
                    else init_cnt <= init_cnt + 1;
                end
                
                ST_ADVANCE: begin
                    state <= ST_FETCH;
                end
                
                ST_FETCH: begin
                    if (win_valid) state <= ST_MAC;
                end
                
                ST_MAC: begin
                    if (mac_cnt == 8) begin
                        state <= ST_WAIT_VALID;
                        mac_cnt <= 0;
                    end else begin
                        mac_cnt <= mac_cnt + 1;
                    end
                end
                
                ST_WAIT_VALID: begin
                    if (win_done) state <= ST_DONE;
                    else state <= ST_ADVANCE;
                end
                
                ST_DONE: begin
                    state <= ST_DONE;
                end
            endcase
        end
    end

endmodule
