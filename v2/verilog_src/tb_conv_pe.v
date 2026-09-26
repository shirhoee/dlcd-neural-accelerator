`timescale 1ns / 1ps

module tb_conv_pe;

    reg clk;
    reg reset;
    reg load_weight;
    reg signed [15:0] weight_in;
    reg mac_en;
    reg clr_acc;
    reg signed [15:0] pixel_in;
    
    wire signed [15:0] out_acc;
    wire valid_out;

    conv_pe uut (
        .clk(clk),
        .reset(reset),
        .load_weight(load_weight),
        .weight_in(weight_in),
        .mac_en(mac_en),
        .clr_acc(clr_acc),
        .pixel_in(pixel_in),
        .out_acc(out_acc),
        .valid_out(valid_out)
    );

    // 10ns period clock
    always #5 clk = ~clk;

    // Golden values from python script
    // Weights: [-0.5, 0.1, 0.8, -0.2, 0.9, -0.1, 0.3, 0.4, -0.7]
    reg signed [15:0] W [0:8];
    
    // Pixels for Interior (Test Case 1)
    reg signed [15:0] P1 [0:8];
    
    // Pixels for Edge (Test Case 2)
    reg signed [15:0] P2 [0:8];

    integer i;
    reg failed = 0;

    initial begin
        $dumpfile("tb_conv_pe.vcd");
        $dumpvars(0, tb_conv_pe);

        // Initialize golden arrays
        W[0] = 16'd65408; W[1] = 16'd26;    W[2] = 16'd205;
        W[3] = 16'd65485; W[4] = 16'd230;   W[5] = 16'd65510;
        W[6] = 16'd77;    W[7] = 16'd102;   W[8] = 16'd65357;

        P1[0] = 16'd26;   P1[1] = 16'd51;   P1[2] = 16'd77;
        P1[3] = 16'd102;  P1[4] = 16'd128;  P1[5] = 16'd154;
        P1[6] = 16'd179;  P1[7] = 16'd205;  P1[8] = 16'd230;

        P2[0] = 16'd0;    P2[1] = 16'd0;    P2[2] = 16'd0;
        P2[3] = 16'd0;    P2[4] = 16'd128;  P2[5] = 16'd154;
        P2[6] = 16'd0;    P2[7] = 16'd205;  P2[8] = 16'd230;

        clk = 0;
        reset = 1;
        load_weight = 0;
        weight_in = 0;
        mac_en = 0;
        clr_acc = 0;
        pixel_in = 0;

        #20;
        reset = 0;
        @(negedge clk);

        // Phase 1: Load Weights (Weight-Stationary)
        // Shift in reverse order so W[0] ends up at tap_idx=0
        for (i = 8; i >= 0; i = i - 1) begin
            load_weight = 1;
            weight_in = W[i];
            @(negedge clk);
        end
        load_weight = 0;
        @(negedge clk);
        @(negedge clk);

        // Phase 2: Test Case 1 (Interior Window)
        for (i = 0; i < 9; i = i + 1) begin
            mac_en = 1;
            clr_acc = (i == 0) ? 1 : 0;
            pixel_in = P1[i];
            @(negedge clk);
        end
        mac_en = 0;
        
        // Wait for result to be clocked
        @(negedge clk);
        if (out_acc !== 16'sd104) begin
            $display("FAIL: Test Case 1 expected 104, got %d", out_acc);
            failed = 1;
        end else begin
            $display("PASS: Test Case 1");
        end

        // Phase 3: Test Case 2 (Edge Window with padding)
        for (i = 0; i < 9; i = i + 1) begin
            mac_en = 1;
            clr_acc = (i == 0) ? 1 : 0;
            pixel_in = P2[i];
            @(negedge clk);
        end
        mac_en = 0;
        
        // Wait for result to be clocked
        @(negedge clk);
        if (out_acc !== 16'sd19) begin
            $display("FAIL: Test Case 2 expected 19, got %d", out_acc);
            failed = 1;
        end else begin
            $display("PASS: Test Case 2");
        end

        if (failed == 0) begin
            $display("ALL TESTS PASSED.");
        end
        
        $finish;
    end

endmodule
