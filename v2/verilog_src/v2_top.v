`timescale 1ns / 1ps

module v2_top (
    input wire clk,
    input wire reset,
    input wire start,
    
    output wire [8:0] pixel_addr,
    input wire signed [15:0] pixel_in,
    
    output wire [3:0] prediction,
    output wire done
);

    reg run_latch;
    always @(posedge clk) begin
        if (reset) begin
            run_latch <= 1'b0;
        end else if (start) begin
            run_latch <= 1'b1;
        end
    end
    
    wire internal_reset = reset | ~run_latch;
    
    // Weight ROMs
    reg [15:0] conv1_rom [0:35];
    reg [15:0] conv2_rom [0:287];
    
    initial begin
        $readmemh("../python_golden_model/weights_q7_8.txt", conv1_rom);
        $readmemh("../python_golden_model/conv2_weights_q7_8.txt", conv2_rom);
    end
    
    wire [575:0] conv1_weights_flat;
    wire [4607:0] conv2_weights_flat;
    
    genvar oc, ic, tap;
    generate
        for (oc = 0; oc < 4; oc = oc + 1) begin : gen_c1_oc
            for (tap = 0; tap < 9; tap = tap + 1) begin : gen_c1_tap
                assign conv1_weights_flat[(oc * 144) + (tap * 16) +: 16] = conv1_rom[oc * 9 + tap];
            end
        end
        
        for (oc = 0; oc < 8; oc = oc + 1) begin : gen_c2_oc
            for (ic = 0; ic < 4; ic = ic + 1) begin : gen_c2_ic
                for (tap = 0; tap < 9; tap = tap + 1) begin : gen_c2_tap
                    assign conv2_weights_flat[(oc * 576) + (ic * 144) + (tap * 16) +: 16] = conv2_rom[oc * 36 + ic * 9 + tap];
                end
            end
        end
    endgenerate

    // Interconnect wires
    // Conv1 -> MaxPool1
    wire c1_valid;
    wire signed [15:0] c1_to_mp1_ch0, c1_to_mp1_ch1, c1_to_mp1_ch2, c1_to_mp1_ch3;
    
    // MaxPool1 -> Conv2
    wire mp1_valid;
    wire signed [15:0] mp1_to_c2_ch0, mp1_to_c2_ch1, mp1_to_c2_ch2, mp1_to_c2_ch3;
    
    // Conv2 -> MaxPool2
    wire c2_valid;
    wire signed [15:0] c2_to_mp2_ch0, c2_to_mp2_ch1, c2_to_mp2_ch2, c2_to_mp2_ch3, c2_to_mp2_ch4, c2_to_mp2_ch5, c2_to_mp2_ch6, c2_to_mp2_ch7;
    
    // MaxPool2 -> Dense
    wire mp2_valid;
    wire signed [15:0] mp2_to_d_ch0, mp2_to_d_ch1, mp2_to_d_ch2, mp2_to_d_ch3, mp2_to_d_ch4, mp2_to_d_ch5, mp2_to_d_ch6, mp2_to_d_ch7;
    
    // Dense -> Argmax
    wire d_valid;
    wire signed [15:0] d_to_am_0, d_to_am_1, d_to_am_2, d_to_am_3, d_to_am_4, d_to_am_5, d_to_am_6, d_to_am_7, d_to_am_8, d_to_am_9;
    
    // Modules
    conv1_array conv1_inst (
        .clk(clk),
        .reset(internal_reset),
        .pixel_in(pixel_in),
        .conv1_weights(conv1_weights_flat),
        .pixel_addr(pixel_addr),
        .valid_out(c1_valid),
        .out_ch0(c1_to_mp1_ch0),
        .out_ch1(c1_to_mp1_ch1),
        .out_ch2(c1_to_mp1_ch2),
        .out_ch3(c1_to_mp1_ch3)
    );
    
    maxpool_array maxpool1_inst (
        .clk(clk),
        .reset(internal_reset),
        .valid_in(c1_valid),
        .in_ch0(c1_to_mp1_ch0),
        .in_ch1(c1_to_mp1_ch1),
        .in_ch2(c1_to_mp1_ch2),
        .in_ch3(c1_to_mp1_ch3),
        .valid_out(mp1_valid),
        .out_ch0(mp1_to_c2_ch0),
        .out_ch1(mp1_to_c2_ch1),
        .out_ch2(mp1_to_c2_ch2),
        .out_ch3(mp1_to_c2_ch3)
    );
    
    conv2_array conv2_inst (
        .clk(clk),
        .reset(internal_reset),
        .valid_in(mp1_valid),
        .in_ch0(mp1_to_c2_ch0),
        .in_ch1(mp1_to_c2_ch1),
        .in_ch2(mp1_to_c2_ch2),
        .in_ch3(mp1_to_c2_ch3),
        .conv2_weights(conv2_weights_flat),
        .valid_out(c2_valid),
        .out_ch0(c2_to_mp2_ch0),
        .out_ch1(c2_to_mp2_ch1),
        .out_ch2(c2_to_mp2_ch2),
        .out_ch3(c2_to_mp2_ch3),
        .out_ch4(c2_to_mp2_ch4),
        .out_ch5(c2_to_mp2_ch5),
        .out_ch6(c2_to_mp2_ch6),
        .out_ch7(c2_to_mp2_ch7)
    );
    
    maxpool2_array maxpool2_inst (
        .clk(clk),
        .reset(internal_reset),
        .valid_in(c2_valid),
        .in_ch0(c2_to_mp2_ch0),
        .in_ch1(c2_to_mp2_ch1),
        .in_ch2(c2_to_mp2_ch2),
        .in_ch3(c2_to_mp2_ch3),
        .in_ch4(c2_to_mp2_ch4),
        .in_ch5(c2_to_mp2_ch5),
        .in_ch6(c2_to_mp2_ch6),
        .in_ch7(c2_to_mp2_ch7),
        .valid_out(mp2_valid),
        .out_ch0(mp2_to_d_ch0),
        .out_ch1(mp2_to_d_ch1),
        .out_ch2(mp2_to_d_ch2),
        .out_ch3(mp2_to_d_ch3),
        .out_ch4(mp2_to_d_ch4),
        .out_ch5(mp2_to_d_ch5),
        .out_ch6(mp2_to_d_ch6),
        .out_ch7(mp2_to_d_ch7)
    );
    
    mlp_head dense_inst (
        .clk(clk),
        .reset(internal_reset),
        .valid_in(mp2_valid),
        .in_ch0(mp2_to_d_ch0),
        .in_ch1(mp2_to_d_ch1),
        .in_ch2(mp2_to_d_ch2),
        .in_ch3(mp2_to_d_ch3),
        .in_ch4(mp2_to_d_ch4),
        .in_ch5(mp2_to_d_ch5),
        .in_ch6(mp2_to_d_ch6),
        .in_ch7(mp2_to_d_ch7),
        .out_digit_0(d_to_am_0),
        .out_digit_1(d_to_am_1),
        .out_digit_2(d_to_am_2),
        .out_digit_3(d_to_am_3),
        .out_digit_4(d_to_am_4),
        .out_digit_5(d_to_am_5),
        .out_digit_6(d_to_am_6),
        .out_digit_7(d_to_am_7),
        .out_digit_8(d_to_am_8),
        .out_digit_9(d_to_am_9),
        .valid_out(d_valid)
    );
    
    argmax argmax_inst (
        .clk(clk),
        .reset(internal_reset),
        .valid_in(d_valid),
        .in_0(d_to_am_0),
        .in_1(d_to_am_1),
        .in_2(d_to_am_2),
        .in_3(d_to_am_3),
        .in_4(d_to_am_4),
        .in_5(d_to_am_5),
        .in_6(d_to_am_6),
        .in_7(d_to_am_7),
        .in_8(d_to_am_8),
        .in_9(d_to_am_9),
        .prediction(prediction),
        .valid_out(done)
    );

endmodule
