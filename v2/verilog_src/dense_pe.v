`timescale 1ns / 1ps

module dense_pe (
    input wire clk,
    input wire reset,
    input wire clr_acc,
    input wire mac_en,
    
    input wire signed [15:0] pixel_in_0,
    input wire signed [15:0] pixel_in_1,
    input wire signed [15:0] pixel_in_2,
    input wire signed [15:0] pixel_in_3,
    input wire signed [15:0] pixel_in_4,
    input wire signed [15:0] pixel_in_5,
    input wire signed [15:0] pixel_in_6,
    input wire signed [15:0] pixel_in_7,
    
    input wire signed [15:0] weight_in_0,
    input wire signed [15:0] weight_in_1,
    input wire signed [15:0] weight_in_2,
    input wire signed [15:0] weight_in_3,
    input wire signed [15:0] weight_in_4,
    input wire signed [15:0] weight_in_5,
    input wire signed [15:0] weight_in_6,
    input wire signed [15:0] weight_in_7,
    
    output reg signed [15:0] out_val
);

    wire signed [15:0] m0, m1, m2, m3, m4, m5, m6, m7;
    
    mac_q7_8 mac0 (.in_val(pixel_in_0), .weight(weight_in_0), .acc_in(16'sd0), .acc_out(m0));
    mac_q7_8 mac1 (.in_val(pixel_in_1), .weight(weight_in_1), .acc_in(16'sd0), .acc_out(m1));
    mac_q7_8 mac2 (.in_val(pixel_in_2), .weight(weight_in_2), .acc_in(16'sd0), .acc_out(m2));
    mac_q7_8 mac3 (.in_val(pixel_in_3), .weight(weight_in_3), .acc_in(16'sd0), .acc_out(m3));
    mac_q7_8 mac4 (.in_val(pixel_in_4), .weight(weight_in_4), .acc_in(16'sd0), .acc_out(m4));
    mac_q7_8 mac5 (.in_val(pixel_in_5), .weight(weight_in_5), .acc_in(16'sd0), .acc_out(m5));
    mac_q7_8 mac6 (.in_val(pixel_in_6), .weight(weight_in_6), .acc_in(16'sd0), .acc_out(m6));
    mac_q7_8 mac7 (.in_val(pixel_in_7), .weight(weight_in_7), .acc_in(16'sd0), .acc_out(m7));
    
    wire signed [15:0] sum01 = m0 + m1;
    wire signed [15:0] sum23 = m2 + m3;
    wire signed [15:0] sum45 = m4 + m5;
    wire signed [15:0] sum67 = m6 + m7;
    
    wire signed [15:0] sum0123 = sum01 + sum23;
    wire signed [15:0] sum4567 = sum45 + sum67;
    
    wire signed [15:0] tree_sum = sum0123 + sum4567;
    
    always @(posedge clk) begin
        if (reset) begin
            out_val <= 16'sd0;
        end else if (mac_en) begin
            if (clr_acc) begin
                out_val <= tree_sum;
            end else begin
                out_val <= out_val + tree_sum;
            end
        end
    end

endmodule
