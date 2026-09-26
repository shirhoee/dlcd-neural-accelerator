`timescale 1ns / 1ps

module tb_argmax;
    reg [159:0] in_bus;
    wire [3:0] out_digit;
    
    reg [15:0] logits [0:9];
    integer i;

    argmax u_argmax (
        .in_bus(in_bus),
        .out_digit(out_digit)
    );

    initial begin
        $dumpfile("tb_argmax.vcd");
        $dumpvars(0, tb_argmax);
        
        // Load the 10 verified outputs from Layer 3
        $readmemh("layer3_expected_outs.hex", logits);
        
        // Flatten into the 160-bit bus
        for (i = 0; i < 10; i = i + 1) begin
            in_bus[(i*16) +: 16] = logits[i];
        end
        
        #10; // Wait for combinational logic to settle
        
        $display("----------------------------------------");
        $display("Argmax Test Results:");
        $display("----------------------------------------");
        for (i = 0; i < 10; i = i + 1) begin
            $display("Digit %0d logit: %h", i, logits[i]);
        end
        $display("----------------------------------------");
        
        // Compute expected argmax from the loaded logits (signed comparison)
        begin : expected_calc
            reg signed [15:0] exp_max_val;
            reg [3:0] exp_digit;
            integer j;
            exp_max_val = logits[0];
            exp_digit = 0;
            for (j = 1; j < 10; j = j + 1) begin
                if ($signed(logits[j]) > $signed(exp_max_val)) begin
                    exp_max_val = logits[j];
                    exp_digit = j[3:0];
                end
            end
            if (out_digit === exp_digit) begin
                $display("PASS: Argmax correctly selected digit %0d!", out_digit);
            end else begin
                $display("FAIL: Argmax selected digit %0d, expected %0d", out_digit, exp_digit);
            end
        end
        $display("----------------------------------------");
        $finish;
    end
endmodule