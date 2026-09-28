`timescale 1ns / 1ps

module maxpool_array (
    input wire clk,
    input wire reset,
    
    input wire valid_in,
    input wire signed [15:0] in_ch0,
    input wire signed [15:0] in_ch1,
    input wire signed [15:0] in_ch2,
    input wire signed [15:0] in_ch3,
    
    output wire signed [15:0] out_ch0,
    output wire signed [15:0] out_ch1,
    output wire signed [15:0] out_ch2,
    output wire signed [15:0] out_ch3,
    output wire valid_out
);

    // CH0
    wire signed [15:0] w0_0, w0_1, w0_2, w0_3;
    wire valid_w0;
    pool_window_gen wg0 (
        .clk(clk), .reset(reset), .valid_in(valid_in), .pixel_in(in_ch0),
        .window_0(w0_0), .window_1(w0_1), .window_2(w0_2), .window_3(w0_3), .window_valid(valid_w0)
    );
    wire signed [15:0] pool0;
    maxpool_pe pe0 (
        .in_val_0(w0_0), .in_val_1(w0_1), .in_val_2(w0_2), .in_val_3(w0_3), .out_max(pool0)
    );
    relu_q7_8 relu0 (.in_val(pool0), .out_val(out_ch0));

    // CH1
    wire signed [15:0] w1_0, w1_1, w1_2, w1_3;
    wire valid_w1;
    pool_window_gen wg1 (
        .clk(clk), .reset(reset), .valid_in(valid_in), .pixel_in(in_ch1),
        .window_0(w1_0), .window_1(w1_1), .window_2(w1_2), .window_3(w1_3), .window_valid(valid_w1)
    );
    wire signed [15:0] pool1;
    maxpool_pe pe1 (
        .in_val_0(w1_0), .in_val_1(w1_1), .in_val_2(w1_2), .in_val_3(w1_3), .out_max(pool1)
    );
    relu_q7_8 relu1 (.in_val(pool1), .out_val(out_ch1));

    // CH2
    wire signed [15:0] w2_0, w2_1, w2_2, w2_3;
    wire valid_w2;
    pool_window_gen wg2 (
        .clk(clk), .reset(reset), .valid_in(valid_in), .pixel_in(in_ch2),
        .window_0(w2_0), .window_1(w2_1), .window_2(w2_2), .window_3(w2_3), .window_valid(valid_w2)
    );
    wire signed [15:0] pool2;
    maxpool_pe pe2 (
        .in_val_0(w2_0), .in_val_1(w2_1), .in_val_2(w2_2), .in_val_3(w2_3), .out_max(pool2)
    );
    relu_q7_8 relu2 (.in_val(pool2), .out_val(out_ch2));

    // CH3
    wire signed [15:0] w3_0, w3_1, w3_2, w3_3;
    wire valid_w3;
    pool_window_gen wg3 (
        .clk(clk), .reset(reset), .valid_in(valid_in), .pixel_in(in_ch3),
        .window_0(w3_0), .window_1(w3_1), .window_2(w3_2), .window_3(w3_3), .window_valid(valid_w3)
    );
    wire signed [15:0] pool3;
    maxpool_pe pe3 (
        .in_val_0(w3_0), .in_val_1(w3_1), .in_val_2(w3_2), .in_val_3(w3_3), .out_max(pool3)
    );
    relu_q7_8 relu3 (.in_val(pool3), .out_val(out_ch3));

    // Synchronized output valid
    assign valid_out = valid_w0;

endmodule
