`timescale 1ns / 1ps

module tb_accelerator_top;
    reg clk, rst, start;
    reg load_weight_l1, load_weight_l2, load_weight_l3;
    reg [255:0] weight_in_l1;
    reg [95:0]  weight_in_l2;
    reg [159:0] weight_in_l3;
    reg [1599:0] in_pixels;
    
    wire [3:0] predicted_digit;
    wire valid_out;

    reg [15:0] w1_mem [0:1599];
    reg [15:0] w2_mem [0:95];  
    reg [15:0] w3_mem [0:59];  
    reg [15:0] in_mem [0:99];  

    accelerator_top uut (
        .clk(clk), .rst(rst), .start(start),
        .load_weight_l1(load_weight_l1), .weight_in_l1(weight_in_l1),
        .load_weight_l2(load_weight_l2), .weight_in_l2(weight_in_l2),
        .load_weight_l3(load_weight_l3), .weight_in_l3(weight_in_l3),
        .in_pixels(in_pixels), .predicted_digit(predicted_digit), .valid_out(valid_out)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    integer i, r, c;
    reg timeout_flag;
    initial begin
        $dumpfile("tb_top.vcd"); $dumpvars(0, tb_accelerator_top);
        $readmemh("e2e_input.hex", in_mem);
        $readmemh("e2e_w1.hex", w1_mem);
        $readmemh("e2e_w2.hex", w2_mem);
        $readmemh("e2e_w3.hex", w3_mem);

        rst = 1; start = 0;
        load_weight_l1 = 0; load_weight_l2 = 0; load_weight_l3 = 0;
        weight_in_l1 = 0; weight_in_l2 = 0; weight_in_l3 = 0; in_pixels = 0;
        
        @(negedge clk); rst = 0;

        $display("Loading ALL Weights in parallel (100 cycles)...");
        load_weight_l1 = 1; load_weight_l2 = 1; load_weight_l3 = 1;
        c = 99;
        while (c >= 0) begin
            r = 0;
            while (r < 16) begin
                weight_in_l1[(r*16) +: 16] = w1_mem[r*100 + c];
                r = r + 1;
            end
            if (c < 16) begin
                r = 0;
                while (r < 6) begin
                    weight_in_l2[(r*16) +: 16] = w2_mem[r*16 + c];
                    r = r + 1;
                end
            end
            if (c < 6) begin
                r = 0;
                while (r < 10) begin
                    weight_in_l3[(r*16) +: 16] = w3_mem[r*6 + c];
                    r = r + 1;
                end
            end
            @(negedge clk);
            c = c - 1;
        end
        load_weight_l1 = 0; load_weight_l2 = 0; load_weight_l3 = 0;

        $display("Applying 100-pixel image to input...");
        c = 0;
        while (c < 100) begin
            in_pixels[(c*16) +: 16] = in_mem[c];
            c = c + 1;
        end
        
        start = 1; @(negedge clk); start = 0;

        $display("Waiting for valid_out flag (Expected ~159 cycles)...");
        
        timeout_flag = 0;
        i = 0;
        // Wait for valid_out with timeout
        while (!valid_out && !timeout_flag) begin
            @(negedge clk);
            i = i + 1;
            if (i > 200) timeout_flag = 1;
        end

        if (valid_out) begin
            $display("----------------------------------------");
            $display("PASS: valid_out triggered!");
            $display("Verilog Prediction: Digit %0d", predicted_digit);
            $display("L1 Buffer (post-ReLU):");
            for (i = 0; i < 16; i = i + 1) begin
                $display("  Neuron %0d: %h", i, uut.l1_buffer[(i*16) +: 16]);
            end
            $display("L2 Buffer (post-ReLU):");
            for (i = 0; i < 6; i = i + 1) begin
                $display("  Neuron %0d: %h", i, uut.l2_buffer[(i*16) +: 16]);
            end
            $display("L3 Buffer (logits):");
            for (i = 0; i < 10; i = i + 1) begin
                $display("  Digit %0d: %h", i, uut.l3_buffer[(i*16) +: 16]);
            end
            $display("----------------------------------------");
        end else begin
            $display("----------------------------------------");
            $display("FAIL: Simulation timed out waiting for valid_out.");
            $display("----------------------------------------");
        end
        
        #20 $finish;
    end
endmodule