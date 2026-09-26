`timescale 1ns / 1ps

module conv_pe (
    input wire clk,
    input wire reset,
    
    // Weight loading interface
    input wire load_weight,       // Shift enable for weights
    input wire signed [15:0] weight_in,
    
    // Pixel input interface
    input wire mac_en,            // Enable MAC operation
    input wire clr_acc,           // When mac_en is high, ignores previous accumulator value (starts new 9-tap window)
    input wire signed [15:0] pixel_in,
    
    // Output
    output reg signed [15:0] out_acc,
    output reg valid_out          // Asserted high on the cycle the 9th tap finishes
);

    // 9 weight registers for a 3x3 kernel (Weight-Stationary)
    reg signed [15:0] weights [0:8];
    reg [3:0] tap_idx; // 0 to 8 counter
    
    wire signed [15:0] mac_result;
    wire signed [15:0] current_weight = weights[tap_idx];
    wire signed [15:0] acc_in = clr_acc ? 16'sd0 : out_acc;
    
    // Reusing V1's verified Q7.8 MAC
    mac_q7_8 mac_inst (
        .a(pixel_in),
        .b(current_weight),
        .c(acc_in),
        .out(mac_result)
    );

    always @(posedge clk) begin
        if (reset) begin
            tap_idx <= 0;
            out_acc <= 0;
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
