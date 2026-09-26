`timescale 1ns / 1ps

module argmax (
    input wire [159:0] in_bus,
    output reg [3:0] out_digit
);
    integer i;
    reg signed [15:0] current_val;
    reg signed [15:0] max_val;

    always @(*) begin
        max_val = in_bus[15:0]; // Initialize with digit 0's value
        out_digit = 0;
        
        for (i = 1; i < 10; i = i + 1) begin
            current_val = in_bus[(i*16) +: 16];
            // Explicitly signed comparison
            if (current_val > max_val) begin
                max_val = current_val;
                out_digit = i[3:0];
            end
        end
    end
endmodule