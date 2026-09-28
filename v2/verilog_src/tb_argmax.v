`timescale 1ns / 1ps

module tb_argmax;
    reg clk, reset, valid_in;
    reg signed [15:0] in_0, in_1, in_2, in_3, in_4, in_5, in_6, in_7, in_8, in_9;
    wire [3:0] prediction;
    wire valid_out;
    
    integer matches;
    
    argmax dut (
        .clk(clk), .reset(reset), .valid_in(valid_in),
        .in_0(in_0), .in_1(in_1), .in_2(in_2), .in_3(in_3), .in_4(in_4),
        .in_5(in_5), .in_6(in_6), .in_7(in_7), .in_8(in_8), .in_9(in_9),
        .prediction(prediction), .valid_out(valid_out)
    );
    
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    task check_vector;
        input signed [15:0] v0, v1, v2, v3, v4, v5, v6, v7, v8, v9;
        input [3:0] exp_idx;
        begin
            @(posedge clk);
            in_0 <= v0; in_1 <= v1; in_2 <= v2; in_3 <= v3; in_4 <= v4;
            in_5 <= v5; in_6 <= v6; in_7 <= v7; in_8 <= v8; in_9 <= v9;
            valid_in <= 1;
            
            @(posedge clk);
            valid_in <= 0;
            
            // wait for valid_out on falling edge to safely sample prediction
            @(negedge clk);
            while (!valid_out) @(negedge clk);
            
            if (prediction === exp_idx) begin
                matches = matches + 1;
            end else begin
                $display("FAIL: expected %0d, got %0d", exp_idx, prediction);
            end
            
            @(posedge clk);
        end
    endtask

    initial begin
        reset = 1; valid_in = 0; matches = 0;
        #20 reset = 0;
        
        // 1. All Negative -> index 5
        check_vector(-16'sd10, -16'sd50, -16'sd20, -16'sd100, -16'sd30, -16'sd5, -16'sd40, -16'sd60, -16'sd70, -16'sd80, 4'd5);
        
        // 2. Tie (Low vs High) -> index 2
        check_vector(16'sd0, 16'sd0, 16'sd50, 16'sd0, 16'sd0, 16'sd0, 16'sd0, 16'sd50, 16'sd0, 16'sd0, 4'd2);
        
        // 3. Max at 0 -> index 0
        check_vector(16'sd100, 16'sd10, 16'sd20, 16'sd30, 16'sd40, 16'sd50, 16'sd60, 16'sd70, 16'sd80, 16'sd90, 4'd0);
        
        // 4. Max at 9 -> index 9
        check_vector(16'sd10, 16'sd20, 16'sd30, 16'sd40, 16'sd50, 16'sd60, 16'sd70, 16'sd80, 16'sd90, 16'sd100, 4'd9);
        
        // 5. Standard mixed -> index 4
        check_vector(-16'sd100, 16'sd50, 16'sd20, -16'sd10, 16'sd80, 16'sd10, 16'sd5, -16'sd5, 16'sd0, 16'sd75, 4'd4);
        
        if (matches == 5) begin
            $display("PASS");
        end else begin
            $display("FAIL: %0d/5 matches.", matches);
        end
        
        #20 $finish;
    end
endmodule
