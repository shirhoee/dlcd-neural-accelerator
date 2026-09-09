`timescale 1ns / 1ps

module accelerator_top (
    input wire clk,
    input wire rst,
    input wire start,

    input wire load_weight_l1,
    input wire [255:0] weight_in_l1,
    input wire load_weight_l2,
    input wire [95:0]  weight_in_l2,
    input wire load_weight_l3,
    input wire [159:0] weight_in_l3,

    input wire [1599:0] in_pixels,

    output wire [3:0] predicted_digit,
    output reg valid_out
);

    wire [255:0] l1_array_out, l1_relu_out;
    wire [95:0]  l2_array_out, l2_relu_out;
    wire [159:0] l3_array_out;

    reg [255:0] l1_buffer;
    reg [95:0]  l2_buffer;
    reg [159:0] l3_buffer;

    reg [15:0] cycle;
    always @(posedge clk) begin
        if (rst) cycle <= 0;
        else if (start) cycle <= 1;
        else if (cycle > 0) cycle <= cycle + 1;
    end

    systolic_array #(.ROWS(16), .COLS(100)) layer1 (
        .clk(clk), .rst(rst), .load_weight(load_weight_l1),
        .weight_in_left(weight_in_l1), .in_val_top(in_pixels),
        .acc_out_right(l1_array_out)
    );
    layer_relu #(.ROWS(16)) relu1 (.acc_in(l1_array_out), .relu_out(l1_relu_out));

    genvar r1;
    generate
        for (r1 = 0; r1 < 16; r1 = r1 + 1) begin : gen_l1_capture
            always @(posedge clk) begin
                if (rst) l1_buffer[(r1*16) +: 16] <= 0;
                else if (cycle == r1 + 102) l1_buffer[(r1*16) +: 16] <= l1_relu_out[(r1*16) +: 16];
            end
        end
    endgenerate

    systolic_array #(.ROWS(6), .COLS(16)) layer2 (
        .clk(clk), .rst(rst), .load_weight(load_weight_l2),
        .weight_in_left(weight_in_l2), .in_val_top(l1_buffer),
        .acc_out_right(l2_array_out)
    );
    layer_relu #(.ROWS(6)) relu2 (.acc_in(l2_array_out), .relu_out(l2_relu_out));

    genvar r2;
    generate
        for (r2 = 0; r2 < 6; r2 = r2 + 1) begin : gen_l2_capture
            always @(posedge clk) begin
                if (rst) l2_buffer[(r2*16) +: 16] <= 0;
                else if (cycle == r2 + 135) l2_buffer[(r2*16) +: 16] <= l2_relu_out[(r2*16) +: 16];
            end
        end
    endgenerate

    systolic_array #(.ROWS(10), .COLS(6)) layer3 (
        .clk(clk), .rst(rst), .load_weight(load_weight_l3),
        .weight_in_left(weight_in_l3), .in_val_top(l2_buffer),
        .acc_out_right(l3_array_out)
    );

    genvar r3;
    generate
        for (r3 = 0; r3 < 10; r3 = r3 + 1) begin : gen_l3_capture
            always @(posedge clk) begin
                if (rst) l3_buffer[(r3*16) +: 16] <= 0;
                else if (cycle == r3 + 148) l3_buffer[(r3*16) +: 16] <= l3_array_out[(r3*16) +: 16];
            end
        end
    endgenerate

    argmax argmax_inst (
        .in_bus(l3_buffer),
        .out_digit(predicted_digit)
    );

    always @(posedge clk) begin
        if (rst) valid_out <= 0;
        else if (cycle == 159) valid_out <= 1;
        else valid_out <= 0;
    end

endmodule