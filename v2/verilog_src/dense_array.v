`timescale 1ns / 1ps

module dense_array (
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
    
    output wire signed [15:0] out_digit_0,
    output wire signed [15:0] out_digit_1,
    output wire signed [15:0] out_digit_2,
    output wire signed [15:0] out_digit_3,
    output wire signed [15:0] out_digit_4,
    output wire signed [15:0] out_digit_5,
    output wire signed [15:0] out_digit_6,
    output wire signed [15:0] out_digit_7,
    output wire signed [15:0] out_digit_8,
    output wire signed [15:0] out_digit_9,
    
    output reg valid_out
);

    reg [15:0] dense_weights [0:1999];
    initial begin
        $readmemh("../python_golden_model/dense_weights_q7_8.txt", dense_weights);
    end
    
    reg [4:0] counter;
    wire clr_acc = (counter == 0);
    wire mac_en = valid_in;
    
    wire signed [15:0] out_val [0:9];
    
    genvar d;
    generate
        for (d = 0; d < 10; d = d + 1) begin : gen_pe
            wire signed [15:0] w0 = dense_weights[d * 200 + counter * 8 + 0];
            wire signed [15:0] w1 = dense_weights[d * 200 + counter * 8 + 1];
            wire signed [15:0] w2 = dense_weights[d * 200 + counter * 8 + 2];
            wire signed [15:0] w3 = dense_weights[d * 200 + counter * 8 + 3];
            wire signed [15:0] w4 = dense_weights[d * 200 + counter * 8 + 4];
            wire signed [15:0] w5 = dense_weights[d * 200 + counter * 8 + 5];
            wire signed [15:0] w6 = dense_weights[d * 200 + counter * 8 + 6];
            wire signed [15:0] w7 = dense_weights[d * 200 + counter * 8 + 7];
            
            dense_pe pe (
                .clk(clk), .reset(reset), .clr_acc(clr_acc), .mac_en(mac_en),
                .pixel_in_0(in_ch0), .pixel_in_1(in_ch1), .pixel_in_2(in_ch2), .pixel_in_3(in_ch3),
                .pixel_in_4(in_ch4), .pixel_in_5(in_ch5), .pixel_in_6(in_ch6), .pixel_in_7(in_ch7),
                .weight_in_0(w0), .weight_in_1(w1), .weight_in_2(w2), .weight_in_3(w3),
                .weight_in_4(w4), .weight_in_5(w5), .weight_in_6(w6), .weight_in_7(w7),
                .out_val(out_val[d])
            );
        end
    endgenerate
    
    assign out_digit_0 = out_val[0];
    assign out_digit_1 = out_val[1];
    assign out_digit_2 = out_val[2];
    assign out_digit_3 = out_val[3];
    assign out_digit_4 = out_val[4];
    assign out_digit_5 = out_val[5];
    assign out_digit_6 = out_val[6];
    assign out_digit_7 = out_val[7];
    assign out_digit_8 = out_val[8];
    assign out_digit_9 = out_val[9];
    
    always @(posedge clk) begin
        if (reset) begin
            counter <= 0;
            valid_out <= 0;
        end else begin
            if (valid_in) begin
                if (counter == 24) begin
                    counter <= 0;
                    valid_out <= 1;
                end else begin
                    counter <= counter + 1;
                    valid_out <= 0;
                end
            end else begin
                valid_out <= 0;
            end
        end
    end

endmodule
