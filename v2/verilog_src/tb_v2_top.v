`timescale 1ns / 1ps

module tb_v2_top;
    reg clk;
    reg reset;
    reg start;
    
    wire [8:0] pixel_addr;
    wire signed [15:0] pixel_in;
    wire [3:0] prediction;
    wire done;
    
    v2_top dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .pixel_addr(pixel_addr),
        .pixel_in(pixel_in),
        .prediction(prediction),
        .done(done)
    );
    
    reg signed [15:0] image_rom [0:399];
    
    initial begin
        $readmemh("../python_golden_model/test_image_q7_8.txt", image_rom);
    end
    
    assign pixel_in = image_rom[pixel_addr];
    
    initial begin
        clk = 0; forever #5 clk = ~clk;
    end
    
    initial begin
        reset = 1; start = 0;
        #20 reset = 0;
        
        #10 start = 1;
        #10 start = 0;
        
        wait(done == 1);
        $display("End-to-End Prediction: %0d", prediction);
        if (prediction === 4'd7) begin
            $display("PASS: Output = 7.");
        end else begin
            $display("FAIL: Expected 7, got %0d.", prediction);
        end
        
        #20 $finish;
    end
    
    initial begin
        #(5000000);
        $display("TIMEOUT");
        $finish;
    end

endmodule
