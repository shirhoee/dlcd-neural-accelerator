`timescale 1ns / 1ps

module tb_conv2_array;

    reg clk;
    reg reset;
    
    // Weight memory (288 * 16 bits = 4608 bits)
    reg [15:0] weights_flat [0:287];
    reg [4607:0] conv2_weights;
    
    // Input memory (100 pixels * 4 channels = 400 words)
    reg [15:0] maxpool_out [0:399];
    
    // Expected output memory (100 pixels * 8 channels = 800 words)
    reg [15:0] expected_conv2_out [0:799];
    
    reg valid_in;
    reg signed [15:0] in_ch0, in_ch1, in_ch2, in_ch3;
    
    wire valid_out;
    wire signed [15:0] out_ch0, out_ch1, out_ch2, out_ch3;
    wire signed [15:0] out_ch4, out_ch5, out_ch6, out_ch7;
    wire done;
    
    conv2_array dut (
        .clk(clk), .reset(reset),
        .conv2_weights(conv2_weights),
        .valid_in(valid_in),
        .in_ch0(in_ch0), .in_ch1(in_ch1), .in_ch2(in_ch2), .in_ch3(in_ch3),
        .valid_out(valid_out),
        .out_ch0(out_ch0), .out_ch1(out_ch1), .out_ch2(out_ch2), .out_ch3(out_ch3),
        .out_ch4(out_ch4), .out_ch5(out_ch5), .out_ch6(out_ch6), .out_ch7(out_ch7),
        .done(done)
    );
    
    integer i;
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    integer in_idx;
    integer out_idx;
    integer match_count;
    
    initial begin
        $readmemh("../python_golden_model/conv2_weights_q7_8.txt", weights_flat);
        $readmemh("../python_golden_model/expected_maxpool_out.txt", maxpool_out);
        $readmemh("../python_golden_model/expected_conv2_out.txt", expected_conv2_out);
        
        // Pack weights
        for (i = 0; i < 288; i = i + 1) begin
            conv2_weights[(i * 16) +: 16] = weights_flat[i];
        end
        
        in_idx = 0;
        out_idx = 0;
        match_count = 0;
        valid_in = 0;
        
        reset = 1;
        #20 reset = 0;
        
        // Stream the 100 pixels
        while (in_idx < 100) begin
            @(posedge clk);
            valid_in <= 1;
            in_ch0 <= maxpool_out[in_idx * 4 + 0];
            in_ch1 <= maxpool_out[in_idx * 4 + 1];
            in_ch2 <= maxpool_out[in_idx * 4 + 2];
            in_ch3 <= maxpool_out[in_idx * 4 + 3];
            in_idx = in_idx + 1;
        end
        @(posedge clk);
        valid_in <= 0;
        
        // Wait for done
        wait(done);
        #20;
        $display("T1 Conv2: %0d/800 matches.", match_count);
        $finish;
    end
    
    always @(posedge clk) begin
        if (valid_out) begin
            if (out_ch0 !== expected_conv2_out[out_idx * 8 + 0]) $display("FAIL idx %0d ch0: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+0], out_ch0); else match_count = match_count + 1;
            if (out_ch1 !== expected_conv2_out[out_idx * 8 + 1]) $display("FAIL idx %0d ch1: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+1], out_ch1); else match_count = match_count + 1;
            if (out_ch2 !== expected_conv2_out[out_idx * 8 + 2]) $display("FAIL idx %0d ch2: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+2], out_ch2); else match_count = match_count + 1;
            if (out_ch3 !== expected_conv2_out[out_idx * 8 + 3]) $display("FAIL idx %0d ch3: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+3], out_ch3); else match_count = match_count + 1;
            if (out_ch4 !== expected_conv2_out[out_idx * 8 + 4]) $display("FAIL idx %0d ch4: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+4], out_ch4); else match_count = match_count + 1;
            if (out_ch5 !== expected_conv2_out[out_idx * 8 + 5]) $display("FAIL idx %0d ch5: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+5], out_ch5); else match_count = match_count + 1;
            if (out_ch6 !== expected_conv2_out[out_idx * 8 + 6]) $display("FAIL idx %0d ch6: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+6], out_ch6); else match_count = match_count + 1;
            if (out_ch7 !== expected_conv2_out[out_idx * 8 + 7]) $display("FAIL idx %0d ch7: exp %h got %h", out_idx, expected_conv2_out[out_idx*8+7], out_ch7); else match_count = match_count + 1;
            out_idx = out_idx + 1;
        end
    end
    
    // Timeout
    initial begin
        #50000;
        $display("TIMEOUT");
        $finish;
    end
endmodule
