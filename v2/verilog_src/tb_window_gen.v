`timescale 1ns / 1ps

module tb_window_gen;

    reg clk;
    reg reset;
    reg advance;
    
    wire [8:0] pixel_addr;
    reg signed [15:0] pixel_in;
    
    wire signed [15:0] out [0:8];
    wire window_valid;
    wire done;

    window_gen uut (
        .clk(clk),
        .reset(reset),
        .advance(advance),
        .pixel_addr(pixel_addr),
        .pixel_in(pixel_in),
        .out_0(out[0]),
        .out_1(out[1]),
        .out_2(out[2]),
        .out_3(out[3]),
        .out_4(out[4]),
        .out_5(out[5]),
        .out_6(out[6]),
        .out_7(out[7]),
        .out_8(out[8]),
        .window_valid(window_valid),
        .done(done)
    );

    // Simulated 20x20 Image ROM (400 pixels)
    reg signed [15:0] image_rom [0:399];
    
    // Expected windows: 400 windows, 9 values each
    reg signed [15:0] expected_windows [0:399][0:8];
    
    // Flat array to read from $readmemh/$readmemd (since 2D reads can be tricky)
    reg signed [15:0] expected_flat [0:3599]; // 400 * 9 = 3600

    integer i, j;
    integer valid_count = 0;
    integer match_count = 0;
    integer failed = 0;

    // Combinational RAM read
    always @(*) begin
        if (pixel_addr < 400) begin
            pixel_in = image_rom[pixel_addr];
        end else begin
            pixel_in = 0;
        end
    end

    // Clock generation
    always #5 clk = ~clk;

    initial begin
        $dumpfile("tb_window_gen.vcd");
        $dumpvars(0, tb_window_gen);

        // Load expected windows from text file (flattened read)
        $readmemh("../python_golden_model/expected_windows.txt", expected_flat);
        
        // Unflatten expected data
        for (i = 0; i < 400; i = i + 1) begin
            for (j = 0; j < 9; j = j + 1) begin
                expected_windows[i][j] = expected_flat[i*9 + j];
            end
        end

        // Initialize Image ROM with predictable pattern: value = row*20 + col + 1
        for (i = 0; i < 400; i = i + 1) begin
            image_rom[i] = i + 1;
        end

        clk = 0;
        reset = 1;
        advance = 0;
        
        #20;
        reset = 0;
        advance = 1;

        // Run until done
        wait(done == 1'b1);
        
        // Let it run a few more cycles to ensure it stays done and doesn't output garbage
        #30;
        advance = 0;
        
        if (valid_count == 400 && match_count == 400 && failed == 0) begin
            $display("ALL TESTS PASSED: %0d/400 windows matched.", match_count);
        end else begin
            $display("FAILED: Expected 400 valid, got %0d. Expected 400 matches, got %0d. Total failures: %0d", valid_count, match_count, failed);
        end

        $finish;
    end

    // Check outputs on every clock cycle where window_valid is high
    always @(posedge clk) begin
        if (window_valid && !reset) begin
            // Check all 9 taps against expected
            for (j = 0; j < 9; j = j + 1) begin
                if (out[j] !== expected_windows[valid_count][j]) begin
                    $display("FAIL at window %0d (r=%0d, c=%0d), tap %0d: Expected %0d, Got %0d", 
                        valid_count, valid_count/20, valid_count%20, j, expected_windows[valid_count][j], out[j]);
                    failed = failed + 1;
                end
            end
            
            // If all 9 taps matched, increment match count
            if (failed == 0) begin
                // Just to avoid false increment if it failed previously, 
                // wait, we want to count completely correct windows:
            end
            
            // To properly count matches per window:
            begin : check_window
                integer tap_err;
                tap_err = 0;
                for (j = 0; j < 9; j = j + 1) begin
                    if (out[j] !== expected_windows[valid_count][j]) tap_err = 1;
                end
                if (tap_err == 0) match_count = match_count + 1;
            end

            valid_count = valid_count + 1;
        end
    end

endmodule
