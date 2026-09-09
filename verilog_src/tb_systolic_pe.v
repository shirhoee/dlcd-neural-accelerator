`timescale 1ns / 1ps

module tb_systolic_pe;
    reg clk;
    reg rst;
    reg load_weight;
    reg signed [15:0] weight_in;
    reg signed [15:0] in_val_in;
    reg signed [15:0] acc_in;

    wire signed [15:0] weight_out;
    wire signed [15:0] in_val_out;
    wire signed [15:0] acc_out;

    reg signed [15:0] test_weights [0:99];
    reg signed [15:0] test_in_vals [0:99];
    reg signed [15:0] expected_outs [0:99];

    integer i;
    integer errors = 0;

    // Instantiate PE
    systolic_pe u_pe (
        .clk(clk),
        .rst(rst),
        .load_weight(load_weight),
        .weight_in(weight_in),
        .in_val_in(in_val_in),
        .acc_in(acc_in),
        .weight_out(weight_out),
        .in_val_out(in_val_out),
        .acc_out(acc_out)
    );

    // Clock generation (10ns period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        // Waveform dump for debugging
        $dumpfile("tb_pe.vcd");
        $dumpvars(0, tb_systolic_pe);

        // Load vectors
        $readmemh("pe_weights.hex", test_weights);
        $readmemh("pe_in_vals.hex", test_in_vals);
        $readmemh("pe_expected_outs.hex", expected_outs);

        // Initialize inputs
        rst = 1;
        load_weight = 0;
        weight_in = 0;
        in_val_in = 0;
        acc_in = 0;

        $display("----------------------------------------");
        $display("Starting Cycle-Accurate PE Test...");
        $display("----------------------------------------");

        // Cycle 0: Reset pulse
        @(negedge clk);
        rst = 0;

        for (i = 0; i < 100; i = i + 1) begin
            // Progress marker
            if (i % 20 == 0) $display("  ...vector %0d", i);

            // Cycle 1: Load Phase
            @(negedge clk);
            load_weight = 1;
            weight_in = test_weights[i];
            in_val_in = 16'hDEAD; // Drive garbage to prove load flush works
            acc_in = 16'hBEEF;    // Drive garbage

            // Cycle 2: Compute Phase (Inputs presented)
            @(negedge clk);
            load_weight = 0;
            weight_in = 16'h0000;
            in_val_in = test_in_vals[i];
            acc_in = 16'd0; // Standalone PE, no accumulation

            // Cycle 3: Check Result (after rising edge has latched it)
            @(negedge clk);
            if (acc_out !== expected_outs[i]) begin
                $display("FAIL at vector %0d: W=%h, X=%h", i, test_weights[i], test_in_vals[i]);
                $display("  Expected %h, Got %h", expected_outs[i], acc_out);
                errors = errors + 1;
            end
        end

        $display("----------------------------------------");
        if (errors == 0)
            $display("PASS: PE Timing and Math verified for 100 cycles!");
        else
            $display("FAIL: %0d errors found.", errors);
        $display("----------------------------------------");

        $finish;
    end
endmodule