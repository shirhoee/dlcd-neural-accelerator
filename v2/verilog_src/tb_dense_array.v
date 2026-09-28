`timescale 1ns / 1ps

module tb_dense_array;

    reg clk;
    reg reset;
    reg valid_in;
    reg signed [15:0] in_ch [0:7];
    
    wire valid_out;
    wire signed [15:0] out_digit [0:9];
    
    dense_array dut (
        .clk(clk), .reset(reset), .valid_in(valid_in),
        .in_ch0(in_ch[0]), .in_ch1(in_ch[1]), .in_ch2(in_ch[2]), .in_ch3(in_ch[3]),
        .in_ch4(in_ch[4]), .in_ch5(in_ch[5]), .in_ch6(in_ch[6]), .in_ch7(in_ch[7]),
        .out_digit_0(out_digit[0]), .out_digit_1(out_digit[1]), .out_digit_2(out_digit[2]), .out_digit_3(out_digit[3]),
        .out_digit_4(out_digit[4]), .out_digit_5(out_digit[5]), .out_digit_6(out_digit[6]), .out_digit_7(out_digit[7]),
        .out_digit_8(out_digit[8]), .out_digit_9(out_digit[9]),
        .valid_out(valid_out)
    );
    
    reg [15:0] maxpool2_out [0:199];
    reg [15:0] expected_out [0:9];
    
    integer in_idx;
    integer match_count;
    integer r;
    
    initial begin
        clk = 0; forever #5 clk = ~clk;
    end
    
    initial begin
        $readmemh("../python_golden_model/expected_maxpool2_out.txt", maxpool2_out);
        $readmemh("../python_golden_model/expected_dense_out.txt", expected_out);
        
        in_idx = 0; match_count = 0; valid_in = 0;
        
        reset = 1; #20 reset = 0;
        
        while (in_idx < 25) begin
            r = $random % 11;
            if (r < 0) r = -r;
            if (r > 0) begin
                valid_in <= 0;
                repeat (r) @(posedge clk);
            end
            
            valid_in <= 1;
            in_ch[0] <= maxpool2_out[in_idx*8 + 0];
            in_ch[1] <= maxpool2_out[in_idx*8 + 1];
            in_ch[2] <= maxpool2_out[in_idx*8 + 2];
            in_ch[3] <= maxpool2_out[in_idx*8 + 3];
            in_ch[4] <= maxpool2_out[in_idx*8 + 4];
            in_ch[5] <= maxpool2_out[in_idx*8 + 5];
            in_ch[6] <= maxpool2_out[in_idx*8 + 6];
            in_ch[7] <= maxpool2_out[in_idx*8 + 7];
            @(posedge clk);
            in_idx = in_idx + 1;
        end
        valid_in <= 0;
        
        repeat (20) @(posedge clk);
        $display("T1 Dense: %0d/10 matches.", match_count);
        $finish;
    end
    
    always @(negedge clk) begin
        if (valid_out) begin
            if (out_digit[0] !== expected_out[0]) $display("FAIL d0: exp %h got %h", expected_out[0], out_digit[0]); else match_count = match_count + 1;
            if (out_digit[1] !== expected_out[1]) $display("FAIL d1: exp %h got %h", expected_out[1], out_digit[1]); else match_count = match_count + 1;
            if (out_digit[2] !== expected_out[2]) $display("FAIL d2: exp %h got %h", expected_out[2], out_digit[2]); else match_count = match_count + 1;
            if (out_digit[3] !== expected_out[3]) $display("FAIL d3: exp %h got %h", expected_out[3], out_digit[3]); else match_count = match_count + 1;
            if (out_digit[4] !== expected_out[4]) $display("FAIL d4: exp %h got %h", expected_out[4], out_digit[4]); else match_count = match_count + 1;
            if (out_digit[5] !== expected_out[5]) $display("FAIL d5: exp %h got %h", expected_out[5], out_digit[5]); else match_count = match_count + 1;
            if (out_digit[6] !== expected_out[6]) $display("FAIL d6: exp %h got %h", expected_out[6], out_digit[6]); else match_count = match_count + 1;
            if (out_digit[7] !== expected_out[7]) $display("FAIL d7: exp %h got %h", expected_out[7], out_digit[7]); else match_count = match_count + 1;
            if (out_digit[8] !== expected_out[8]) $display("FAIL d8: exp %h got %h", expected_out[8], out_digit[8]); else match_count = match_count + 1;
            if (out_digit[9] !== expected_out[9]) $display("FAIL d9: exp %h got %h", expected_out[9], out_digit[9]); else match_count = match_count + 1;
        end
    end
endmodule
