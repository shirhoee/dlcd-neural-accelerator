`timescale 1ns / 1ps

module tb_v2_top_fixed;
    reg clk;
    reg reset;
    reg start;
    
    wire [8:0] pixel_addr;
    wire signed [15:0] pixel_in;
    wire [3:0] prediction;
    wire done;
    
    // Cycle counting
    integer start_cycle = 0;
    integer end_cycle = 0;
    integer cycle_count = 0;
    integer layer_cycles [0:5]; 
    integer mp1_start = 0, mp1_end = 0;
    integer mp2_start = 0, mp2_end = 0;
    integer dense_start = 0, dense_end = 0;

    always @(posedge clk) begin
        cycle_count = cycle_count + 1;
        
        if (dut.mp1_valid && mp1_start == 0) mp1_start = cycle_count;
        if (dut.mp1_valid) mp1_end = cycle_count;
        
        if (dut.mp2_valid && mp2_start == 0) mp2_start = cycle_count;
        if (dut.mp2_valid) mp2_end = cycle_count;
        
        if (dut.d_valid && dense_start == 0) dense_start = cycle_count;
        if (dut.d_valid) dense_end = cycle_count;
    end
    
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
    
    // File path injected via macro
    initial begin
        $readmemh(`TEST_IMAGE_FILE, image_rom);
    end
    
    assign pixel_in = image_rom[pixel_addr];
    
    initial begin
        clk = 0; forever #5 clk = ~clk;
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
        
        #10 start = 1; start_cycle = cycle_count;
        #10 start = 0;
        
        wait(done == 1);
        end_cycle = cycle_count;
        
        $display("RTL_PRED:%0d", prediction);
        $display("RTL_LOGITS:%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d", 
            $signed(tb_logits_cap[0]), $signed(tb_logits_cap[1]), $signed(tb_logits_cap[2]), $signed(tb_logits_cap[3]), $signed(tb_logits_cap[4]),
            $signed(tb_logits_cap[5]), $signed(tb_logits_cap[6]), $signed(tb_logits_cap[7]), $signed(tb_logits_cap[8]), $signed(tb_logits_cap[9]));
        $display("RTL_CYCLES:%0d", end_cycle - start_cycle);
        $display("MP1_CYCLES:%0d", mp1_end - start_cycle);
        $display("MP2_CYCLES:%0d", mp2_end - mp2_start);
        $display("DENSE_CYCLES:%0d", dense_end - dense_start);
        
        #20 $finish;
    end
    
    initial begin
        #(50000000);
        $display("TIMEOUT");
        $finish;
    end

endmodule
