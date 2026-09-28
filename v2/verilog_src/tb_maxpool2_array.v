`timescale 1ns / 1ps

module tb_maxpool2_array;

    reg clk;
    reg reset;
    reg valid_in;
    reg signed [15:0] in_ch [0:7];
    
    wire valid_out;
    wire signed [15:0] out_ch0, out_ch1, out_ch2, out_ch3;
    wire signed [15:0] out_ch4, out_ch5, out_ch6, out_ch7;
    
    maxpool2_array dut (
        .clk(clk), .reset(reset), .valid_in(valid_in),
        .in_ch0(in_ch[0]), .in_ch1(in_ch[1]), .in_ch2(in_ch[2]), .in_ch3(in_ch[3]),
        .in_ch4(in_ch[4]), .in_ch5(in_ch[5]), .in_ch6(in_ch[6]), .in_ch7(in_ch[7]),
        .valid_out(valid_out),
        .out_ch0(out_ch0), .out_ch1(out_ch1), .out_ch2(out_ch2), .out_ch3(out_ch3),
        .out_ch4(out_ch4), .out_ch5(out_ch5), .out_ch6(out_ch6), .out_ch7(out_ch7)
    );
    
    reg [15:0] conv2_out [0:799];
    reg [15:0] expected_out [0:199];
    
    integer in_idx;
    integer out_idx;
    integer match_count;
    integer gap;
    integer r;
    
    initial begin
        clk = 0; forever #5 clk = ~clk;
    end
    
    initial begin
        $readmemh("../python_golden_model/expected_conv2_out.txt", conv2_out);
        $readmemh("../python_golden_model/expected_maxpool2_out.txt", expected_out);
        
        in_idx = 0; out_idx = 0; match_count = 0; valid_in = 0;
        
        reset = 1; #20 reset = 0;
        
        while (in_idx < 100) begin
            // Random gap 0 to 10
            r = $random % 11;
            if (r < 0) r = -r;
            if (r > 0) begin
                valid_in <= 0;
                repeat (r) @(posedge clk);
            end
            
            valid_in <= 1;
            in_ch[0] <= conv2_out[in_idx*8 + 0];
            in_ch[1] <= conv2_out[in_idx*8 + 1];
            in_ch[2] <= conv2_out[in_idx*8 + 2];
            in_ch[3] <= conv2_out[in_idx*8 + 3];
            in_ch[4] <= conv2_out[in_idx*8 + 4];
            in_ch[5] <= conv2_out[in_idx*8 + 5];
            in_ch[6] <= conv2_out[in_idx*8 + 6];
            in_ch[7] <= conv2_out[in_idx*8 + 7];
            @(posedge clk);
            in_idx = in_idx + 1;
        end
        valid_in <= 0;
        
        repeat (20) @(posedge clk);
        $display("T1 MaxPool2: %0d/200 matches.", match_count);
        $finish;
    end
    
    always @(negedge clk) begin
        if (valid_out) begin
            if (out_ch0 !== expected_out[out_idx*8 + 0]) $display("FAIL idx %0d ch0: exp %h got %h", out_idx, expected_out[out_idx*8+0], out_ch0); else match_count = match_count + 1;
            if (out_ch1 !== expected_out[out_idx*8 + 1]) $display("FAIL idx %0d ch1: exp %h got %h", out_idx, expected_out[out_idx*8+1], out_ch1); else match_count = match_count + 1;
            if (out_ch2 !== expected_out[out_idx*8 + 2]) $display("FAIL idx %0d ch2: exp %h got %h", out_idx, expected_out[out_idx*8+2], out_ch2); else match_count = match_count + 1;
            if (out_ch3 !== expected_out[out_idx*8 + 3]) $display("FAIL idx %0d ch3: exp %h got %h", out_idx, expected_out[out_idx*8+3], out_ch3); else match_count = match_count + 1;
            if (out_ch4 !== expected_out[out_idx*8 + 4]) $display("FAIL idx %0d ch4: exp %h got %h", out_idx, expected_out[out_idx*8+4], out_ch4); else match_count = match_count + 1;
            if (out_ch5 !== expected_out[out_idx*8 + 5]) $display("FAIL idx %0d ch5: exp %h got %h", out_idx, expected_out[out_idx*8+5], out_ch5); else match_count = match_count + 1;
            if (out_ch6 !== expected_out[out_idx*8 + 6]) $display("FAIL idx %0d ch6: exp %h got %h", out_idx, expected_out[out_idx*8+6], out_ch6); else match_count = match_count + 1;
            if (out_ch7 !== expected_out[out_idx*8 + 7]) $display("FAIL idx %0d ch7: exp %h got %h", out_idx, expected_out[out_idx*8+7], out_ch7); else match_count = match_count + 1;
            out_idx = out_idx + 1;
        end
    end
endmodule
