`timescale 1ns / 1ps

module tb_submission;

    reg clk;
    reg reset;
    reg start;
    
    wire [8:0] pixel_addr;
    wire signed [15:0] pixel_in;
    wire [3:0] prediction;
    wire done;
    
    // Top-Level Accelerator Instance
    v2_top dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .pixel_addr(pixel_addr),
        .pixel_in(pixel_in),
        .prediction(prediction),
        .done(done)
    );

    // 10 test images (400 words each = 4000 words total)
    reg signed [15:0] test_vectors [0:3999];
    reg [3:0] test_labels [0:9];
    
    integer test_idx;
    integer passed_count;
    integer latency_cycles;
    
    assign pixel_in = test_vectors[test_idx * 400 + pixel_addr];
    
    // Clock generation: 100 MHz (10ns period, 5ns half-period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    initial begin
        $dumpfile("tb_submission.vcd");
        $dumpvars(0, tb_submission);
        
        $readmemh("submission_test_vectors.hex", test_vectors);
        $readmemh("submission_labels.hex", test_labels);
        
        passed_count = 0;
        reset = 1;
        start = 0;
        
        $display("");
        $display("========================================================================================");
        $display("         PES UNIVERSITY - UE25CS251A DLCD LABORATORY END SEMESTER ASSESSMENT");
        $display("         V2 CNN NEURAL ACCELERATOR: 10-DIGIT HARDWARE VERIFICATION SUITE");
        $display("========================================================================================");
        
        #30;
        
        // Loop sequentially through all 10 digits (0 through 9)
        for (test_idx = 0; test_idx < 10; test_idx = test_idx + 1) begin
            // Synchronous reset pulse for this test run
            @(posedge clk);
            reset <= 1'b1;
            start <= 1'b0;
            
            @(posedge clk);
            @(posedge clk);
            reset <= 1'b0;
            
            @(posedge clk);
            start <= 1'b1;
            latency_cycles = 0;
            
            @(posedge clk);
            start <= 1'b0;
            
            // Measure latency until accelerator asserts done
            while (!done) begin
                @(posedge clk);
                latency_cycles = latency_cycles + 1;
            end
            
            // Check prediction against golden ground-truth label
            if (prediction === test_labels[test_idx]) begin
                passed_count = passed_count + 1;
                $display(" [TEST %2d] True Digit: %0d | Predicted: %0d | Latency: %0d cycles | Result: PASS", 
                         test_idx + 1, test_labels[test_idx], prediction, latency_cycles);
            end else begin
                $display(" [TEST %2d] True Digit: %0d | Predicted: %0d | Latency: %0d cycles | Result: FAIL (Expected %0d)", 
                         test_idx + 1, test_labels[test_idx], prediction, latency_cycles, test_labels[test_idx]);
            end
            
            // Small inter-test spacing
            #50;
        end
        
        $display("----------------------------------------------------------------------------------------");
        if (passed_count == 10) begin
            $display(" FINAL SCORECARD: 10/10 PASSED (100.0%% Hardware Accuracy) | ALL TESTS PASSED");
        end else begin
            $display(" FINAL SCORECARD: %0d/10 PASSED | HARDWARE MISMATCH DETECTED", passed_count);
        end
        $display("========================================================================================");
        $display("");
        
        #100;
        $finish;
    end

    initial begin
        #(20000000); // 20ms safety timeout
        $display("TIMEOUT: Simulation exceeded maximum allowed time.");
        $finish;
    end

endmodule
