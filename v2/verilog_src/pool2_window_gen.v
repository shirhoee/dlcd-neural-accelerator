`timescale 1ns / 1ps

module pool2_window_gen (
    input wire clk,
    input wire reset,
    input wire valid_in,
    input wire signed [15:0] pixel_in,
    
    output wire signed [15:0] window_0, // TL
    output wire signed [15:0] window_1, // TR
    output wire signed [15:0] window_2, // BL
    output wire signed [15:0] window_3, // BR
    output wire window_valid
);

    reg signed [15:0] sr [0:10];
    reg [3:0] row;
    reg [3:0] col;
    integer i;

    assign window_0 = sr[10];   // TL
    assign window_1 = sr[9];    // TR
    assign window_2 = sr[0];    // BL
    assign window_3 = pixel_in; // BR
    
    assign window_valid = valid_in && (row[0] == 1'b1) && (col[0] == 1'b1);

    always @(posedge clk) begin
        if (reset) begin
            row <= 0;
            col <= 0;
            for (i = 0; i < 11; i = i + 1) begin
                sr[i] <= 0;
            end
        end else if (valid_in) begin
            for (i = 10; i > 0; i = i - 1) begin
                sr[i] <= sr[i-1];
            end
            sr[0] <= pixel_in;
            
            if (col == 9) begin
                col <= 0;
                if (row == 9) begin
                    row <= 0;
                end else begin
                    row <= row + 1;
                end
            end else begin
                col <= col + 1;
            end
        end
    end
endmodule
