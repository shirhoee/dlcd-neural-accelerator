`timescale 1ns / 1ps

module tb_systolic_array_l2;
    parameter ROWS = 6;
    parameter COLS = 16;
    parameter LOAD_CYCLES = COLS;      // 16 cycles to shift weights across the row

    reg clk;
    reg rst;
    reg load_weight;
    reg [(ROWS*16)-1:0] weight_in_left;
    reg [(COLS*16)-1:0] in_val_top;
    wire [(ROWS*16)-1:0] acc_out_right;

    reg signed [15:0] weight_mem [0:(ROWS*COLS)-1]; // row-major, 96 values
    reg signed [15:0] input_vec  [0:COLS-1];
    reg signed [15:0] expected_outs [0:ROWS-1];

    integer i, r, c;
    integer errors = 0;
    integer wait_cycles;
    integer elapsed;

    systolic_array #(.ROWS(ROWS), .COLS(COLS)) u_array (
        .clk(clk),
        .rst(rst),
        .load_weight(load_weight),
        .weight_in_left(weight_in_left),
        .in_val_top(in_val_top),
        .acc_out_right(acc_out_right)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        $dumpfile("tb_array_l2.vcd");
        $dumpvars(0, tb_systolic_array_l2);

        $readmemh("layer2_weights.hex", weight_mem);
        $readmemh("layer2_input.hex", input_vec);
        $readmemh("layer2_expected_outs.hex", expected_outs);

        rst = 1;
        load_weight = 0;
        weight_in_left = 0;
        in_val_top = 0;

        $display("----------------------------------------");
        $display("Starting Layer 2 Systolic Array Test (%0dx%0d)...", ROWS, COLS);
        $display("----------------------------------------");

        @(negedge clk);
        rst = 0;

        // --- LOAD PHASE ---
        // Reversed order (COLS-1 down to 0) per the weight-loading fix from M3:
        // shift-register loading means the last-presented value ends up leftmost.
        load_weight = 1;
        for (c = LOAD_CYCLES - 1; c >= 0; c = c - 1) begin
            for (r = 0; r < ROWS; r = r + 1) begin
                weight_in_left[(r*16) +: 16] = weight_mem[r*COLS + c];
            end
            @(negedge clk);
        end
        load_weight = 0;
        weight_in_left = 0;

        $display("Load phase complete at cycle count matching LOAD_CYCLES=%0d", LOAD_CYCLES);

        // --- COMPUTE PHASE ---
        for (c = 0; c < COLS; c = c + 1) begin
            in_val_top[(c*16) +: 16] = input_vec[c];
        end
        @(negedge clk);

        // --- STAGGERED CHECK PER ROW ---
        // Same formula as M3: first valid cycle for row r = r + COLS + 1,
        // measured from the moment inputs are presented (right after load ends).
        elapsed = 0;
        for (r = 0; r < ROWS; r = r + 1) begin
            wait_cycles = (r + COLS + 1) - elapsed;
            if (wait_cycles > 0) begin
                repeat (wait_cycles) @(negedge clk);
            end
            elapsed = elapsed + (wait_cycles > 0 ? wait_cycles : 0);
            if (acc_out_right[(r*16) +: 16] !== expected_outs[r]) begin
                $display("FAIL row %0d: Expected %h, Got %h", r, expected_outs[r], acc_out_right[(r*16) +: 16]);
                errors = errors + 1;
            end else begin
                $display("PASS row %0d: %h", r, acc_out_right[(r*16) +: 16]);
            end
        end

        $display("----------------------------------------");
        if (errors == 0)
            $display("PASS: All %0d rows matched expected output!", ROWS);
        else
            $display("FAIL: %0d row(s) mismatched.", errors);
        $display("----------------------------------------");

        $finish;
    end
endmodule