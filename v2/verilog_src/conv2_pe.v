`timescale 1ns / 1ps

module conv2_pe (
    input wire clk,
    input wire reset,
    
    input wire clr_acc,
    input wire mac_en,
    
    input wire signed [15:0] pixel_in_0,
    input wire signed [15:0] pixel_in_1,
    input wire signed [15:0] pixel_in_2,
    input wire signed [15:0] pixel_in_3,
    
    input wire signed [15:0] weight_in_0,
    input wire signed [15:0] weight_in_1,
    input wire signed [15:0] weight_in_2,
    input wire signed [15:0] weight_in_3,
    
    output reg signed [15:0] out_acc,
    output reg valid_out
);

    wire signed [15:0] mac_out_0;
    wire signed [15:0] mac_out_1;
    wire signed [15:0] mac_out_2;
    wire signed [15:0] mac_out_3;

    mac_q7_8 mac0 (.weight(weight_in_0), .in_val(pixel_in_0), .acc_in(16'sd0), .acc_out(mac_out_0));
    mac_q7_8 mac1 (.weight(weight_in_1), .in_val(pixel_in_1), .acc_in(16'sd0), .acc_out(mac_out_1));
    mac_q7_8 mac2 (.weight(weight_in_2), .in_val(pixel_in_2), .acc_in(16'sd0), .acc_out(mac_out_2));
    mac_q7_8 mac3 (.weight(weight_in_3), .in_val(pixel_in_3), .acc_in(16'sd0), .acc_out(mac_out_3));

    wire signed [15:0] sum_01 = mac_out_0 + mac_out_1;
    wire signed [15:0] sum_23 = mac_out_2 + mac_out_3;
    wire signed [15:0] tree_sum = sum_01 + sum_23;

    reg [3:0] tap_idx;

    always @(posedge clk) begin
        if (reset) begin
            out_acc <= 16'sd0;
            valid_out <= 0;
            tap_idx <= 0;
        end else begin
            if (mac_en) begin
                if (clr_acc) begin
                    out_acc <= tree_sum;
                end else begin
                    out_acc <= out_acc + tree_sum;
                end
                
                if (tap_idx == 8) begin
                    tap_idx <= 0;
                    valid_out <= 1;
                end else begin
                    tap_idx <= tap_idx + 1;
                    valid_out <= 0;
                end
            end else begin
                valid_out <= 0;
            end
        end
    end

endmodule
