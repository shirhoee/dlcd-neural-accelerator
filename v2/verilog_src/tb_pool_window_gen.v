`timescale 1ns / 1ps

module tb_pool_window_gen;

    reg clk;
    reg reset;
    
    reg valid_in;
    reg signed [15:0] pixel_in;
    
    wire signed [15:0] window_0;
    wire signed [15:0] window_1;
    wire signed [15:0] window_2;
    wire signed [15:0] window_3;
    wire window_valid;

    pool_window_gen uut (
        .clk(clk),
        .reset(reset),
        .valid_in(valid_in),
        .pixel_in(pixel_in),
        .window_0(window_0),
        .window_1(window_1),
        .window_2(window_2),
        .window_3(window_3),
        .window_valid(window_valid)
    );

    // Expected Memory: 100 windows x 4 values = 400 elements
    reg [15:0] expected_mem [0:399];
    
    always #5 clk = ~clk;

    integer i;
    integer match_count = 0;
    integer failed = 0;
    integer window_idx = 0;

    initial begin
        $dumpfile("tb_pool_window_gen.vcd");
        $dumpvars(0, tb_pool_window_gen);
        
        $readmemh("../python_golden_model/expected_pool_windows.hex", expected_mem);
        
        clk = 0;
        reset = 1;
        valid_in = 0;
        pixel_in = 0;
        
        #20;
        reset = 0;
        #10;
        
        // Feed 400 pixels sequentially, simulating sporadic valid_in pulses
        for (i = 0; i < 400; i = i + 1) begin
            valid_in = 1;
            pixel_in = i; // Input value matches its index 0 to 399
            
            // Wait 1 clock cycle for the push
            #10;
            
            // Randomly insert bubble cycles to prove it doesn't rely on solid bursts
            valid_in = 0;
            #10;
            #10;
        end
        
        #50;
        
        if (window_idx == 100 && failed == 0) begin
            $display("ALL TESTS PASSED: %0d/100 windows matched.", window_idx);
        end else begin
            $display("FAILED: Expected 100 windows, got %0d. Failures: %0d", window_idx, failed);
        end
        
        $finish;
    end

    // Monitor output
    always @(posedge clk) begin
        if (window_valid && !reset) begin
            begin : check_block
                reg signed [15:0] exp0, exp1, exp2, exp3;
                exp0 = expected_mem[window_idx * 4 + 0];
                exp1 = expected_mem[window_idx * 4 + 1];
                exp2 = expected_mem[window_idx * 4 + 2];
                exp3 = expected_mem[window_idx * 4 + 3];
                
                if (window_0 !== exp0 || window_1 !== exp1 || window_2 !== exp2 || window_3 !== exp3) begin
                    $display("FAIL at window %0d: Expected [%d, %d, %d, %d], Got [%d, %d, %d, %d]", 
                        window_idx, exp0, exp1, exp2, exp3, window_0, window_1, window_2, window_3);
                    failed = failed + 1;
                end
            end
            window_idx = window_idx + 1;
        end
    end

endmodule
