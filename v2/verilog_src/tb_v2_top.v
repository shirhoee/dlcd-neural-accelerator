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
    
    // Snooping Logic
    integer mp1_idx = 0;
    reg [15:0] tb_mp1_cap [0:399];
    always @(posedge clk) begin
        if (dut.mp1_valid) begin
            tb_mp1_cap[mp1_idx*4 + 0] = dut.mp1_to_c2_ch0;
            tb_mp1_cap[mp1_idx*4 + 1] = dut.mp1_to_c2_ch1;
            tb_mp1_cap[mp1_idx*4 + 2] = dut.mp1_to_c2_ch2;
            tb_mp1_cap[mp1_idx*4 + 3] = dut.mp1_to_c2_ch3;
            mp1_idx = mp1_idx + 1;
        end
    end
    
    integer mp2_idx = 0;
    reg [15:0] tb_mp2_cap [0:199];
    always @(posedge clk) begin
        if (dut.mp2_valid) begin
            tb_mp2_cap[mp2_idx*8 + 0] = dut.mp2_to_d_ch0;
            tb_mp2_cap[mp2_idx*8 + 1] = dut.mp2_to_d_ch1;
            tb_mp2_cap[mp2_idx*8 + 2] = dut.mp2_to_d_ch2;
            tb_mp2_cap[mp2_idx*8 + 3] = dut.mp2_to_d_ch3;
            tb_mp2_cap[mp2_idx*8 + 4] = dut.mp2_to_d_ch4;
            tb_mp2_cap[mp2_idx*8 + 5] = dut.mp2_to_d_ch5;
            tb_mp2_cap[mp2_idx*8 + 6] = dut.mp2_to_d_ch6;
            tb_mp2_cap[mp2_idx*8 + 7] = dut.mp2_to_d_ch7;
            mp2_idx = mp2_idx + 1;
        end
    end
    
    reg [15:0] tb_logits_cap [0:9];
    always @(posedge clk) begin
        if (dut.d_valid) begin
            tb_logits_cap[0] = dut.d_to_am_0;
            tb_logits_cap[1] = dut.d_to_am_1;
            tb_logits_cap[2] = dut.d_to_am_2;
            tb_logits_cap[3] = dut.d_to_am_3;
            tb_logits_cap[4] = dut.d_to_am_4;
            tb_logits_cap[5] = dut.d_to_am_5;
            tb_logits_cap[6] = dut.d_to_am_6;
            tb_logits_cap[7] = dut.d_to_am_7;
            tb_logits_cap[8] = dut.d_to_am_8;
            tb_logits_cap[9] = dut.d_to_am_9;
        end
    end

    initial begin
        reset = 1; start = 0;
        #20 reset = 0;
        
        #10 start = 1;
        #10 start = 0;
        
        wait(done == 1);
        
        // Dump logic analyzer
        $writememh("../v2_ui/backend/logs/mp1_cap.txt", tb_mp1_cap);
        $writememh("../v2_ui/backend/logs/mp2_cap.txt", tb_mp2_cap);
        $writememh("../v2_ui/backend/logs/logits_cap.txt", tb_logits_cap);
        
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
