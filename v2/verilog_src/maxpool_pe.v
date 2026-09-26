`timescale 1ns / 1ps

module maxpool_pe (
    input wire signed [15:0] in_val_0,
    input wire signed [15:0] in_val_1,
    input wire signed [15:0] in_val_2,
    input wire signed [15:0] in_val_3,
    output reg signed [15:0] out_max
);

    // Explicitly declared signed internal variables matching V1's argmax.v pattern
    reg signed [15:0] max_01;
    reg signed [15:0] max_23;

    always @(*) begin
        // First stage comparators (parallel)
        if (in_val_0 > in_val_1) begin
            max_01 = in_val_0;
        end else begin
            max_01 = in_val_1;
        end
        
        if (in_val_2 > in_val_3) begin
            max_23 = in_val_2;
        end else begin
            max_23 = in_val_3;
        end
        
        // Second stage comparator
        if (max_01 > max_23) begin
            out_max = max_01;
        end else begin
            out_max = max_23;
        end
    end

endmodule
