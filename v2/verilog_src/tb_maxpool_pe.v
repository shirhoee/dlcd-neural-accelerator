`timescale 1ns / 1ps

module tb_maxpool_pe;

    reg signed [15:0] in_val_0;
    reg signed [15:0] in_val_1;
    reg signed [15:0] in_val_2;
    reg signed [15:0] in_val_3;
    wire signed [15:0] out_max;

    maxpool_pe uut (
        .in_val_0(in_val_0),
        .in_val_1(in_val_1),
        .in_val_2(in_val_2),
        .in_val_3(in_val_3),
        .out_max(out_max)
    );

    reg failed = 0;

    initial begin
        $dumpfile("tb_maxpool_pe.vcd");
        $dumpvars(0, tb_maxpool_pe);

        // Wait a little before starting tests
        #10;

        // === TEST CASE 1: All Positive ===
        // Inputs (Q): [26, 128, 51, 230] -> Expected Max: 230
        in_val_0 = 16'd26;
        in_val_1 = 16'd128;
        in_val_2 = 16'd51;
        in_val_3 = 16'd230;
        #10;
        if (out_max !== 16'sd230) begin
            $display("FAIL: Test Case 1 expected 230, got %d", out_max);
            failed = 1;
        end else begin
            $display("PASS: Test Case 1 (All Positive)");
        end

        // === TEST CASE 2: All Negative ===
        // Inputs (Q): [65408, 65510, 65306, 65485] -> Expected Max: 65510
        in_val_0 = 16'd65408; // -128
        in_val_1 = 16'd65510; // -26
        in_val_2 = 16'd65306; // -230
        in_val_3 = 16'd65485; // -51
        #10;
        if (out_max !== 16'sd65510) begin
            $display("FAIL: Test Case 2 expected 65510 (-26), got %d", out_max);
            failed = 1;
        end else begin
            $display("PASS: Test Case 2 (All Negative)");
        end

        // === TEST CASE 3: Mixed Positive/Negative ===
        // Inputs (Q): [65306, 26, 65408, 13] -> Expected Max: 26
        // Unsigned max would fail this and pick 65408 or 65306
        in_val_0 = 16'd65306; // -230
        in_val_1 = 16'd26;    // 26
        in_val_2 = 16'd65408; // -128
        in_val_3 = 16'd13;    // 13
        #10;
        if (out_max !== 16'sd26) begin
            $display("FAIL: Test Case 3 expected 26, got %d", out_max);
            failed = 1;
        end else begin
            $display("PASS: Test Case 3 (Mixed Positive/Negative)");
        end

        // === TEST CASE 4: Tie ===
        // Inputs (Q): [102, 102, 26, 65408] -> Expected Max: 102
        in_val_0 = 16'd102;
        in_val_1 = 16'd102;
        in_val_2 = 16'd26;
        in_val_3 = 16'd65408; // -128
        #10;
        if (out_max !== 16'sd102) begin
            $display("FAIL: Test Case 4 expected 102, got %d", out_max);
            failed = 1;
        end else begin
            $display("PASS: Test Case 4 (Tie)");
        end

        if (failed == 0) begin
            $display("ALL TESTS PASSED.");
        end

        $finish;
    end

endmodule
