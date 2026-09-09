`timescale 1ns / 1ps

module tb_systolic_array_l1;
    parameter ROWS = 16;
    parameter COLS = 100;
    parameter LOAD_CYCLES = COLS;      // 100 cycles to shift weights across the row

    reg clk;
    reg rst;
    reg load_weight;
    reg [(ROWS*16)-1:0] weight_in_left;
    reg [(COLS*16)-1:0] in_val_top;
    wire [(ROWS*16)-1:0] acc_out_right;

    reg signed [15:0] weight_mem [0:(ROWS*COLS)-1]; // row-major, 1600 values
    reg signed [15:0] input_vec  [0:COLS-1];
    reg signed [15:0] expected_outs [0:ROWS-1];

    integer i, r, c;
    integer errors = 0;
    integer wait_cycles;

    systolic_array_l1 #(.ROWS(ROWS), .COLS(COLS)) u_array (
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
        $dumpfile("tb_array.vcd");
        $dumpvars(0, tb_systolic_array_l1);

        $readmemh("array_weights.hex", weight_mem);
        $readmemh("array_input.hex", input_vec);
        $readmemh("array_expected_outs.hex", expected_outs);

        rst = 1;
        load_weight = 0;
        weight_in_left = 0;
        in_val_top = 0;

        $display("----------------------------------------");
        $display("Starting Systolic Array Test (%0dx%0d)...", ROWS, COLS);
        $display("----------------------------------------");

        @(negedge clk);
        rst = 0;

        // --- LOAD PHASE ---
        // Each row's weights shift in from the left, one column position per cycle.
        // At cycle k of the load phase, present column-k weights for every row
        // on weight_in_left; the array's internal shift registers carry each
        // row's weight sequence rightward one PE per cycle.
        // IMPORTANT: Present columns in REVERSE order (99..0) so that column 0
        // ends up at the leftmost PE (index 0) and column 99 at the rightmost (index 99).
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
        // Present the single input vector across the top edge and hold it;
        // the vector streams down through the rows over ROWS cycles, then
        // each row's accumulator ripples across COLS cycles to the right edge.
        for (c = 0; c < COLS; c = c + 1) begin
            in_val_top[(c*16) +: 16] = input_vec[c];
        end
        @(negedge clk);

        // --- INSTRUMENTATION WINDOW ---
        // Watch acc_out_right[0] (row 0) across the predicted arrival window
        // to confirm the exact edge-alignment offset before trusting the
        // general formula for all 16 rows.
        for (i = 0; i < 25; i = i + 1) begin
            @(negedge clk);
            if (i >= 15 && i <= 22) begin
                $display("  watch cycle offset %0d: acc_out_right[row0] = %h (expected %h)",
                          i, acc_out_right[15:0], expected_outs[0]);
            end
        end

        // --- STAGGERED CHECK PER ROW ---
        // Using derived formula: first valid cycle for row r (measured from
        // end of load phase) = r + COLS + 1. We've already advanced ~26
        // cycles past load-end in the instrumentation loop above, so wait
        // any remaining delta per row before checking.
        for (r = 0; r < ROWS; r = r + 1) begin
            wait_cycles = (r + COLS + 1) - 26; // subtract cycles already elapsed
            if (wait_cycles > 0) begin
                repeat (wait_cycles) @(negedge clk);
            end
            if (acc_out_right[(r*16) +: 16] !== expected_outs[r]) begin
                $display("FAIL row %0d: Expected %h, Got %h", r, expected_outs[r], acc_out_right[(r*16) +: 16]);
                errors = errors + 1;
            end else begin
                $display("PASS row %0d: %h", r, acc_out_right[(r*16) +: 16]);
            end

            if (r == 0) begin
                for (i = 0; i < 3; i = i + 1) begin
                    @(negedge clk);
                    $display("  post-check cycle %0d: acc_out_right[row0] = %h", i, acc_out_right[15:0]);
                end
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