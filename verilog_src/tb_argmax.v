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
        
        // From our manual check of M7:
        // Neuron 1 has 174f (+5967), Neuron 4 has 0d7a (+3450), Neuron 7 has 0fcc (+4044).
        // All others are negative (MSB=1). 
        // Therefore, Argmax MUST pick digit 1.
        if (out_digit === 4'd1) begin
            $display("PASS: Argmax correctly selected digit %0d!", out_digit);
        end else begin
            $display("FAIL: Argmax selected digit %0d, expected 1", out_digit);
        end
        $display("----------------------------------------");
        $finish;
    end
endmodule