`timescale 1ns / 1ps

module tb_mlp_head;

    reg clk;
    reg reset;
    reg valid_in;
    
    reg signed [15:0] in_ch0;
    reg signed [15:0] in_ch1;
    reg signed [15:0] in_ch2;
    reg signed [15:0] in_ch3;
    reg signed [15:0] in_ch4;
    reg signed [15:0] in_ch5;
    reg signed [15:0] in_ch6;
    reg signed [15:0] in_ch7;
    
    wire signed [15:0] out_digit_0;
    wire signed [15:0] out_digit_1;
    wire signed [15:0] out_digit_2;
    wire signed [15:0] out_digit_3;
    wire signed [15:0] out_digit_4;
    wire signed [15:0] out_digit_5;
    wire signed [15:0] out_digit_6;
    wire signed [15:0] out_digit_7;
    wire signed [15:0] out_digit_8;
    wire signed [15:0] out_digit_9;
    wire valid_out;
    
    mlp_head dut (
        .clk(clk),
        .reset(reset),
        .valid_in(valid_in),
        .in_ch0(in_ch0),
        .in_ch1(in_ch1),
        .in_ch2(in_ch2),
        .in_ch3(in_ch3),
        .in_ch4(in_ch4),
        .in_ch5(in_ch5),
        .in_ch6(in_ch6),
        .in_ch7(in_ch7),
        .out_digit_0(out_digit_0),
        .out_digit_1(out_digit_1),
        .out_digit_2(out_digit_2),
        .out_digit_3(out_digit_3),
        .out_digit_4(out_digit_4),
        .out_digit_5(out_digit_5),
        .out_digit_6(out_digit_6),
        .out_digit_7(out_digit_7),
        .out_digit_8(out_digit_8),
        .out_digit_9(out_digit_9),
        .valid_out(valid_out)
    );

    // Test vectors: 200 input features, 10 expected logits
    reg [15:0] input_features [0:199];
    reg [15:0] expected_logits [0:9];
    
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    integer step;
    integer match_count;
    integer cycle_count;
    
    initial begin
        $dumpfile("tb_mlp_head.vcd");
        $dumpvars(0, tb_mlp_head);
        
        $readmemh("../python_golden_model/expected_mp2_relu_flat.txt", input_features);
        $readmemh("../python_golden_model/expected_logits.txt", expected_logits);
        
        reset = 1;
        valid_in = 0;
        in_ch0 = 0; in_ch1 = 0; in_ch2 = 0; in_ch3 = 0;
        in_ch4 = 0; in_ch5 = 0; in_ch6 = 0; in_ch7 = 0;
        match_count = 0;
        cycle_count = 0;
        
        #20 reset = 0;
        #10;
        
        // Stream the 200 features in 25 cycles (8 channels per cycle)
        for (step = 0; step < 25; step = step + 1) begin
            @(posedge clk);
            valid_in <= 1'b1;
            in_ch0 <= input_features[step * 8 + 0];
            in_ch1 <= input_features[step * 8 + 1];
            in_ch2 <= input_features[step * 8 + 2];
            in_ch3 <= input_features[step * 8 + 3];
            in_ch4 <= input_features[step * 8 + 4];
            in_ch5 <= input_features[step * 8 + 5];
            in_ch6 <= input_features[step * 8 + 6];
            in_ch7 <= input_features[step * 8 + 7];
        end
        
        @(posedge clk);
        valid_in <= 1'b0;
        
        // Wait for computation across all 3 dense layers
        while (!valid_out) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end
        
        // Check logits
        if (out_digit_0 === expected_logits[0]) match_count = match_count + 1; else $display("Logit 0 mismatch: exp %h got %h", expected_logits[0], out_digit_0);
        if (out_digit_1 === expected_logits[1]) match_count = match_count + 1; else $display("Logit 1 mismatch: exp %h got %h", expected_logits[1], out_digit_1);
        if (out_digit_2 === expected_logits[2]) match_count = match_count + 1; else $display("Logit 2 mismatch: exp %h got %h", expected_logits[2], out_digit_2);
        if (out_digit_3 === expected_logits[3]) match_count = match_count + 1; else $display("Logit 3 mismatch: exp %h got %h", expected_logits[3], out_digit_3);
        if (out_digit_4 === expected_logits[4]) match_count = match_count + 1; else $display("Logit 4 mismatch: exp %h got %h", expected_logits[4], out_digit_4);
        if (out_digit_5 === expected_logits[5]) match_count = match_count + 1; else $display("Logit 5 mismatch: exp %h got %h", expected_logits[5], out_digit_5);
        if (out_digit_6 === expected_logits[6]) match_count = match_count + 1; else $display("Logit 6 mismatch: exp %h got %h", expected_logits[6], out_digit_6);
        if (out_digit_7 === expected_logits[7]) match_count = match_count + 1; else $display("Logit 7 mismatch: exp %h got %h", expected_logits[7], out_digit_7);
        if (out_digit_8 === expected_logits[8]) match_count = match_count + 1; else $display("Logit 8 mismatch: exp %h got %h", expected_logits[8], out_digit_8);
        if (out_digit_9 === expected_logits[9]) match_count = match_count + 1; else $display("Logit 9 mismatch: exp %h got %h", expected_logits[9], out_digit_9);
        
        if (match_count == 10) begin
            $display("ALL TESTS PASSED: 10/10 MLP Head output logits matched in %0d cycles.", cycle_count);
        end else begin
            $display("FAILED: Only %0d/10 logits matched.", match_count);
        end
        
        #20 $finish;
    end

    initial begin
        #(200000);
        $display("TIMEOUT in tb_mlp_head");
        $finish;
    end

endmodule
