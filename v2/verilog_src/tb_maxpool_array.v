`timescale 1ns / 1ps

module tb_maxpool_array;

    reg clk;
    reg reset;
    
    reg valid_in;
    reg signed [15:0] in_ch0;
    reg signed [15:0] in_ch1;
    reg signed [15:0] in_ch2;
    reg signed [15:0] in_ch3;
    
    wire signed [15:0] out_ch0;
    wire signed [15:0] out_ch1;
    wire signed [15:0] out_ch2;
    wire signed [15:0] out_ch3;
    wire valid_out;
    
    maxpool_array dut (
        .clk(clk), .reset(reset),
        .valid_in(valid_in),
        .in_ch0(in_ch0), .in_ch1(in_ch1), .in_ch2(in_ch2), .in_ch3(in_ch3),
        .out_ch0(out_ch0), .out_ch1(out_ch1), .out_ch2(out_ch2), .out_ch3(out_ch3),
        .valid_out(valid_out)
    );
    
    // 4 frames x 400 inputs = 1600 lines
    reg [15:0] inputs_flat [0:6399]; // 1600 x 4
    
    // 4 frames x 100 outputs = 400 lines
    reg [15:0] expected_out_flat [0:1599]; // 400 x 4
    
    integer in_idx;
    integer out_idx;
    integer match_count;
    
    integer seed;
    
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    initial begin
        $readmemh("../python_golden_model/standalone_maxpool_in.txt", inputs_flat);
        $readmemh("../python_golden_model/standalone_maxpool_out.txt", expected_out_flat);
        
        in_idx = 0;
        out_idx = 0;
        match_count = 0;
        seed = 42;
        
        valid_in = 0;
        reset = 1;
        #20 reset = 0;
        
        // Feed 1600 inputs
        while (in_idx < 1600) begin
            @(posedge clk);
            
            // Random gaps
            if (($random(seed) % 100) < 30) begin
                valid_in <= 0;
            end else begin
                valid_in <= 1;
                in_ch0 <= inputs_flat[in_idx * 4 + 0];
                in_ch1 <= inputs_flat[in_idx * 4 + 1];
                in_ch2 <= inputs_flat[in_idx * 4 + 2];
                in_ch3 <= inputs_flat[in_idx * 4 + 3];
                in_idx = in_idx + 1;
            end
        end
        
        @(posedge clk);
        valid_in <= 0;
        
        #100;
        $display("T2/T3 Standalone: %0d/1600 matches.", match_count);
        $finish;
    end
    
    always @(posedge clk) begin
        if (valid_out) begin
            if (out_ch0 !== expected_out_flat[out_idx * 4 + 0]) begin
                $display("FAIL at idx %0d ch0: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 0], out_ch0);
            end else match_count = match_count + 1;
            
            if (out_ch1 !== expected_out_flat[out_idx * 4 + 1]) begin
                $display("FAIL at idx %0d ch1: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 1], out_ch1);
            end else match_count = match_count + 1;
            
            if (out_ch2 !== expected_out_flat[out_idx * 4 + 2]) begin
                $display("FAIL at idx %0d ch2: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 2], out_ch2);
            end else match_count = match_count + 1;
            
            if (out_ch3 !== expected_out_flat[out_idx * 4 + 3]) begin
                $display("FAIL at idx %0d ch3: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 3], out_ch3);
            end else match_count = match_count + 1;
            
            out_idx = out_idx + 1;
        end
    end
    
endmodule
