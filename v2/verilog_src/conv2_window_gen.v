`timescale 1ns / 1ps

module conv2_window_gen (
    input wire clk,
    input wire reset,
    input wire advance,
    
    // Interface to Image RAM (Combinational read)
    output wire [6:0] pixel_addr, // 0 to 99
    input wire signed [15:0] pixel_in,
    
    // Output 3x3 Window
    output wire signed [15:0] out_0,
    output wire signed [15:0] out_1,
    output wire signed [15:0] out_2,
    output wire signed [15:0] out_3,
    output wire signed [15:0] out_4,
    output wire signed [15:0] out_5,
    output wire signed [15:0] out_6,
    output wire signed [15:0] out_7,
    output wire signed [15:0] out_8,
    
    output wire window_valid,
    output wire done
);

    reg [3:0] vx; // 0 to 11
    reg [3:0] vy; // 0 to 11
    reg is_done;

    reg signed [15:0] SR [0:26];
    integer i;

    reg [3:0] sr_x;
    reg [3:0] sr_y;

    wire is_inside = (vx >= 1 && vx <= 10 && vy >= 1 && vy <= 10);
    assign pixel_addr = is_inside ? ((vy - 1) * 10 + (vx - 1)) : 7'd0;

    wire signed [15:0] current_val = is_inside ? pixel_in : 16'sd0;

    assign out_0 = SR[26];
    assign out_1 = SR[25];
    assign out_2 = SR[24];
    assign out_3 = SR[14];
    assign out_4 = SR[13];
    assign out_5 = SR[12];
    assign out_6 = SR[2];
    assign out_7 = SR[1];
    assign out_8 = SR[0];

    assign window_valid = (sr_x >= 2 && sr_y >= 2);
    assign done = is_done;

    always @(posedge clk) begin
        if (reset) begin
            vx <= 0;
            vy <= 0;
            sr_x <= 0;
            sr_y <= 0;
            is_done <= 0;
            for (i = 0; i < 27; i = i + 1) begin
                SR[i] <= 0;
            end
        end else if (advance && !is_done) begin
            for (i = 26; i > 0; i = i - 1) begin
                SR[i] <= SR[i-1];
            end
            SR[0] <= current_val;
            
            sr_x <= vx;
            sr_y <= vy;
            
            if (vx == 11) begin
                vx <= 0;
                if (vy == 11) begin
                    is_done <= 1;
                end else begin
                    vy <= vy + 1;
                end
            end else begin
                vx <= vx + 1;
            end
        end
    end

endmodule
