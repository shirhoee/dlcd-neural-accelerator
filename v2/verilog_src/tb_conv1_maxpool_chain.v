`timescale 1ns / 1ps

module tb_conv1_maxpool_chain;

    reg clk;
    reg reset;
    
    // Weight delivery
    reg [575:0] conv1_weights;
    
    // Testbench ROMs
    reg [15:0] image_rom [0:399];
    reg [15:0] weights_flat [0:35];
    
    // Expected Output ROM: 100 positions x 4 channels = 400 expected values
    reg [15:0] expected_out_flat [0:399];
    
    wire [8:0] pixel_addr;
    reg signed [15:0] pixel_in;
    
    // Conv1 array outputs
    wire signed [15:0] conv_ch0;
    wire signed [15:0] conv_ch1;
    wire signed [15:0] conv_ch2;
    wire signed [15:0] conv_ch3;
    wire conv_valid_out;
    wire conv_done;

    // Maxpool array outputs
    wire signed [15:0] pool_ch0;
    wire signed [15:0] pool_ch1;
    wire signed [15:0] pool_ch2;
    wire signed [15:0] pool_ch3;
    wire pool_valid_out;

    always @(*) begin
        if (pixel_addr < 400) begin
            pixel_in = image_rom[pixel_addr];
        end else begin
            pixel_in = 16'd0;
        end
    end

    conv1_array dut_conv (
        .clk(clk), .reset(reset),
        .pixel_addr(pixel_addr), .pixel_in(pixel_in),
        .conv1_weights(conv1_weights),
        .out_ch0(conv_ch0), .out_ch1(conv_ch1),
        .out_ch2(conv_ch2), .out_ch3(conv_ch3),
        .valid_out(conv_valid_out), .done(conv_done)
    );

    maxpool_array dut_pool (
        .clk(clk), .reset(reset),
        .valid_in(conv_valid_out),
        .in_ch0(conv_ch0), .in_ch1(conv_ch1),
        .in_ch2(conv_ch2), .in_ch3(conv_ch3),
        .out_ch0(pool_ch0), .out_ch1(pool_ch1),
        .out_ch2(pool_ch2), .out_ch3(pool_ch3),
        .valid_out(pool_valid_out)
    );

    integer i, j, k;
    integer match_count;
    
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    initial begin
        $readmemh("../python_golden_model/test_image_q7_8.txt", image_rom);
        $readmemh("../python_golden_model/weights_q7_8.txt", weights_flat);
        
        // Pack weights into the flat 576-bit bus
        for (i = 0; i < 36; i = i + 1) begin
            conv1_weights[(i * 16) +: 16] = weights_flat[i];
        end
        
        // Load expected maxpool out (100 rows x 4 cols = 400 values)
        // Format of expected_maxpool_out.txt is: CH0 CH1 CH2 CH3 (100 lines)
        $readmemh("../python_golden_model/expected_maxpool_out.txt", expected_out_flat);
        
        match_count = 0;
        reset = 1;
        #20 reset = 0;
        
        // Wait for all 100 outputs
        // (Conv is 400 outputs, maxpool filters it down to 100)
    end
    
    integer out_idx = 0;
    always @(posedge clk) begin
        if (pool_valid_out) begin
            if (pool_ch0 !== expected_out_flat[out_idx * 4 + 0]) begin
                $display("FAIL at idx %0d ch0: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 0], pool_ch0);
            end else match_count = match_count + 1;
            
            if (pool_ch1 !== expected_out_flat[out_idx * 4 + 1]) begin
                $display("FAIL at idx %0d ch1: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 1], pool_ch1);
            end else match_count = match_count + 1;
            
            if (pool_ch2 !== expected_out_flat[out_idx * 4 + 2]) begin
                $display("FAIL at idx %0d ch2: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 2], pool_ch2);
            end else match_count = match_count + 1;
            
            if (pool_ch3 !== expected_out_flat[out_idx * 4 + 3]) begin
                $display("FAIL at idx %0d ch3: exp %h, got %h", out_idx, expected_out_flat[out_idx * 4 + 3], pool_ch3);
            end else match_count = match_count + 1;
            
            out_idx = out_idx + 1;
        end
        
        if (conv_done && out_idx == 100) begin
            $display("T1 Chain: %0d/400 matches.", match_count);
            $finish;
        end
    end
    
endmodule
