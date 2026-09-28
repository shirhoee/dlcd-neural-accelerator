`timescale 1ns / 1ps

module argmax (
    input wire clk,
    input wire reset,
    input wire valid_in,
    input wire signed [15:0] in_0,
    input wire signed [15:0] in_1,
    input wire signed [15:0] in_2,
    input wire signed [15:0] in_3,
    input wire signed [15:0] in_4,
    input wire signed [15:0] in_5,
    input wire signed [15:0] in_6,
    input wire signed [15:0] in_7,
    input wire signed [15:0] in_8,
    input wire signed [15:0] in_9,
    output reg [3:0] prediction,
    output reg valid_out
);

    reg signed [15:0] m01, m23, m45, m67, m89;
    reg [3:0] i01, i23, i45, i67, i89;
    
    reg signed [15:0] m03, m47, m89_s2;
    reg [3:0] i03, i47, i89_s2;
    
    reg signed [15:0] m07, m89_s3;
    reg [3:0] i07, i89_s3;
    
    reg signed [15:0] final_val;
    reg [3:0] final_idx;

    always @(*) begin
        // Stage 1
        if (in_1 > in_0) begin m01 = in_1; i01 = 4'd1; end else begin m01 = in_0; i01 = 4'd0; end
        if (in_3 > in_2) begin m23 = in_3; i23 = 4'd3; end else begin m23 = in_2; i23 = 4'd2; end
        if (in_5 > in_4) begin m45 = in_5; i45 = 4'd5; end else begin m45 = in_4; i45 = 4'd4; end
        if (in_7 > in_6) begin m67 = in_7; i67 = 4'd7; end else begin m67 = in_6; i67 = 4'd6; end
        if (in_9 > in_8) begin m89 = in_9; i89 = 4'd9; end else begin m89 = in_8; i89 = 4'd8; end
        
        // Stage 2
        if (m23 > m01) begin m03 = m23; i03 = i23; end else begin m03 = m01; i03 = i01; end
        if (m67 > m45) begin m47 = m67; i47 = i67; end else begin m47 = m45; i47 = i45; end
        m89_s2 = m89; i89_s2 = i89;
        
        // Stage 3
        if (m47 > m03) begin m07 = m47; i07 = i47; end else begin m07 = m03; i07 = i03; end
        m89_s3 = m89_s2; i89_s3 = i89_s2;
        
        // Stage 4
        if (m89_s3 > m07) begin final_val = m89_s3; final_idx = i89_s3; end else begin final_val = m07; final_idx = i07; end
    end
    
    always @(posedge clk) begin
        if (reset) begin
            valid_out <= 0;
            prediction <= 0;
        end else begin
            valid_out <= valid_in;
            if (valid_in) begin
                prediction <= final_idx;
            end
        end
    end

endmodule
