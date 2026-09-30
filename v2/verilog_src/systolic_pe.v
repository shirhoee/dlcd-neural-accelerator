`timescale 1ns / 1ps

module systolic_pe (
    input wire clk,
    input wire rst,
    input wire load_weight,
    input wire signed [15:0] weight_in,
    input wire signed [15:0] in_val_in,
    input wire signed [15:0] acc_in,

    output reg signed [15:0] weight_out,
    output reg signed [15:0] in_val_out,
    output reg signed [15:0] acc_out
);

    reg signed [15:0] stationary_weight;
    wire signed [15:0] mac_result;

    mac_q7_8 core_mac (
        .weight(stationary_weight),
        .in_val(in_val_in),
        .acc_in(acc_in),
        .acc_out(mac_result)
    );

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            stationary_weight <= 16'd0;
            weight_out <= 16'd0;
            in_val_out <= 16'd0;
            acc_out    <= 16'd0;
        end else if (load_weight) begin
            stationary_weight <= weight_in;
            weight_out <= weight_in;
            in_val_out <= 16'd0;
            acc_out    <= 16'd0;
        end else begin
            in_val_out <= in_val_in;
            acc_out    <= mac_result;
        end
    end
endmodule