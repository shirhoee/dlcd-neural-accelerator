`timescale 1ns / 1ps

/*
 * V2 - N4a: MaxPool Window Generator
 * Memory router that takes a sequential pixel stream (20x20) and 
 * combinationally forms 2x2 windows with a stride of 2.
 *
 * Line Buffering & Taps:
 * To form a 2x2 window when the bottom-right pixel (p[r,c]) arrives at `pixel_in`:
 * - BR (Bottom-Right) = pixel_in
 * - BL (Bottom-Left)  = Delayed by 1 cycle
 * - TR (Top-Right)    = Delayed by 20 cycles (1 full row)
 * - TL (Top-Left)     = Delayed by 21 cycles (1 full row + 1 pixel)
 *
 * Therefore, we need a 21-stage shift register to hold the history. 
 * (Often called a 20-element line buffer because it buffers 1 full line between TR and BR).
 *
 * Row/Col Counting (Stride 2):
 * A valid 2x2 block is fully formed when the bottom-right pixel arrives.
 * In a stride-2 setup, the bottom-right pixels fall exclusively on odd rows and odd columns 
 * (e.g., [1,1], [1,3], [3,1], ... [19,19]). 
 * Thus, `window_valid` simply pulses high when valid_in is high AND row[0]==1 AND col[0]==1.
 */

module pool_window_gen (
    input wire clk,
    input wire reset,
    
    input wire valid_in,
    input wire signed [15:0] pixel_in,
    
    output wire signed [15:0] window_0, // Top-Left
    output wire signed [15:0] window_1, // Top-Right
    output wire signed [15:0] window_2, // Bottom-Left
    output wire signed [15:0] window_3, // Bottom-Right
    output wire window_valid
);

    // 21-stage shift register
    reg signed [15:0] sr [0:20];
    integer i;
    
    // Row/Col counters
    reg [4:0] col; // 0 to 19
    reg [4:0] row; // 0 to 19
    
    always @(posedge clk) begin
        if (reset) begin
            col <= 0;
            row <= 0;
            for (i = 0; i < 21; i = i + 1) begin
                sr[i] <= 16'd0;
            end
        end else if (valid_in) begin
            // Shift register
            sr[0] <= pixel_in;
            for (i = 1; i < 21; i = i + 1) begin
                sr[i] <= sr[i-1];
            end
            
            // Coordinate tracking
            if (col == 19) begin
                col <= 0;
                if (row == 19) begin
                    row <= 0;
                end else begin
                    row <= row + 1;
                end
            end else begin
                col <= col + 1;
            end
        end
    end

    // Combinational Output Assignments
    assign window_0 = sr[20];   // Top-Left (21 cycles old)
    assign window_1 = sr[19];   // Top-Right (20 cycles old)
    assign window_2 = sr[0];    // Bottom-Left (1 cycle old)
    assign window_3 = pixel_in; // Bottom-Right (Current pixel)
    
    // Stride 2 logic: valid ONLY on odd columns and odd rows
    assign window_valid = valid_in && (col[0] == 1'b1) && (row[0] == 1'b1);

endmodule
