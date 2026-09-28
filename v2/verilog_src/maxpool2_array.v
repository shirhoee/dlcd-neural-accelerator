`timescale 1ns / 1ps

module maxpool2_array (
    input wire clk,
    input wire reset,
    input wire valid_in,
    
    input wire signed [15:0] in_ch0,
    input wire signed [15:0] in_ch1,
    input wire signed [15:0] in_ch2,
    input wire signed [15:0] in_ch3,
    input wire signed [15:0] in_ch4,
    input wire signed [15:0] in_ch5,
    input wire signed [15:0] in_ch6,
    input wire signed [15:0] in_ch7,
    
    output wire valid_out,
    output wire signed [15:0] out_ch0,
    output wire signed [15:0] out_ch1,
    output wire signed [15:0] out_ch2,
    output wire signed [15:0] out_ch3,
    output wire signed [15:0] out_ch4,
    output wire signed [15:0] out_ch5,
    output wire signed [15:0] out_ch6,
    output wire signed [15:0] out_ch7
);

    wire w_valid_0;
    
    wire signed [15:0] in_ch [0:7];
    assign in_ch[0] = in_ch0; assign in_ch[1] = in_ch1;
    assign in_ch[2] = in_ch2; assign in_ch[3] = in_ch3;
    assign in_ch[4] = in_ch4; assign in_ch[5] = in_ch5;
    assign in_ch[6] = in_ch6; assign in_ch[7] = in_ch7;
    
    wire signed [15:0] out_ch_arr [0:7];
    
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : gen_pool
            wire signed [15:0] w0, w1, w2, w3;
            wire wv;
            
            pool2_window_gen p_wg (
                .clk(clk), .reset(reset), .valid_in(valid_in), .pixel_in(in_ch[i]),
                .window_0(w0), .window_1(w1), .window_2(w2), .window_3(w3),
                .window_valid(wv)
            );
            
            wire signed [15:0] max_out;
            maxpool_pe m_pe (
                .in_val_0(w0), .in_val_1(w1), .in_val_2(w2), .in_val_3(w3),
                .out_max(max_out)
            );
            
            relu_q7_8 relu (
                .in_val(max_out),
                .out_val(out_ch_arr[i])
            );
            
            if (i == 0) begin : gen_valid
                assign w_valid_0 = wv;
            end
        end
    endgenerate
    
    assign out_ch0 = out_ch_arr[0];
    assign out_ch1 = out_ch_arr[1];
    assign out_ch2 = out_ch_arr[2];
    assign out_ch3 = out_ch_arr[3];
    assign out_ch4 = out_ch_arr[4];
    assign out_ch5 = out_ch_arr[5];
    assign out_ch6 = out_ch_arr[6];
    assign out_ch7 = out_ch_arr[7];
    
    assign valid_out = w_valid_0;

endmodule
