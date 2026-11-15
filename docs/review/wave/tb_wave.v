`timescale 1ns / 1ps
`default_nettype none

//
// tb_wave.v — WAVEFORM ARTIFACT (Phase 1 review)
// ===============================================
// Derived from v2/verilog_src/tb_v2_top_fixed.v with VCD dumping added.
// The ORIGINAL testbench was NOT edited.
// Instantiates v2_top directly as `dut` (same hierarchy as tb_v2_top_fixed's
// snooping targets: dut.conv1_inst, dut.conv1_inst.pe0, dut.dense_inst,
// dut.mp1_valid/mp2_valid/d_valid/done/prediction).
//
// Image: hardcoded $readmemh of v2/verilog_src/test_image_tmp.txt
//   (relative to the simulation cwd; run from repo root).
//
// Compile (from repo root):
//   iverilog -g2001 -Wall -o docs/review/build/tb_wave.vvp
//       docs/review/wave/tb_wave.v
//       v2/verilog_src/v2_top.v v2/verilog_src/conv1_array.v
//       v2/verilog_src/window_gen.v v2/verilog_src/conv_pe.v v2/verilog_src/mac_q7_8.v
//       v2/verilog_src/maxpool_array.v v2/verilog_src/pool_window_gen.v
//       v2/verilog_src/maxpool_pe.v v2/verilog_src/relu_q7_8.v
//       v2/verilog_src/conv2_array.v v2/verilog_src/conv2_window_gen.v
//       v2/verilog_src/conv2_pe.v v2/verilog_src/maxpool2_array.v
//       v2/verilog_src/pool2_window_gen.v v2/verilog_src/mlp_head.v
//       v2/verilog_src/systolic_array.v v2/verilog_src/systolic_pe.v
//       v2/verilog_src/layer_relu.v v2/verilog_src/argmax.v
//   vvp docs/review/build/tb_wave.vvp   (cwd = repo root)
//      -> writes docs/review/wave/wave.vcd
//
// Open:
//   gtkwave docs\review\wave\wave.vcd docs\review\wave\wave.gtkw
//

module tb_wave;
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
    integer mp1_start = 0, mp1_end = 0;
    integer mp2_start = 0, mp2_end = 0;
    integer dense_start = 0, dense_end = 0;
    
    // DUT — v2_top exposes the same hierarchy snooped by tb_v2_top_fixed
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
    
    // Image memory (same golden test image used by tb_v2_top / tb_v2_top_fixed)
    // test_image_tmp.txt is expected in the sim cwd (v2/verilog_src).
    initial begin
        $readmemh("test_image_tmp.txt", image_rom);
    end
    
    assign pixel_in = image_rom[pixel_addr];
    
    initial begin
        clk = 0; forever #5 clk = ~clk;
    end

    // Cycle/progress snooping (dut.mp1_valid etc. are internal wires of v2_top)
    always @(posedge clk) begin
        cycle_count = cycle_count + 1;
        
        if (dut.mp1_valid && mp1_start == 0) mp1_start = cycle_count;
        if (dut.mp1_valid) mp1_end = cycle_count;
        
        if (dut.mp2_valid && mp2_start == 0) mp2_start = cycle_count;
        if (dut.mp2_valid) mp2_end = cycle_count;
        
        if (dut.d_valid && dense_start == 0) dense_start = cycle_count;
        if (dut.d_valid) dense_end = cycle_count;
    end
    
    // VCD dump — required signal set for the review waveform
    initial begin
        // cwd at run time is v2/verilog_src (RTL $readmemh paths are relative
        // to that directory), so the VCD lands back at docs/review/wave/:
        $dumpfile("../../docs/review/wave/wave.vcd");
        // $dumpvars(0) captures top-level regs (clk, reset, start) plus the
        // full hierarchy, covering every signal for the GTK save file:
        // clk, reset, start, pixel_addr, c1_valid (=dut.conv1_inst.valid_out),
        // mp1_valid (=dut.maxpool1_inst.valid_out),
        // c2_valid (=dut.conv2_inst.valid_out),
        // mp2_valid (=dut.maxpool2_inst.valid_out),
        // d_valid (=dut.d_valid), done, prediction, conv1_inst/pe0/
        // dense_inst/argmax_inst internals.
        $dumpvars(0);
    end
    
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
    
    reg [1:0] prev_layer;
    reg [15:0] tb_dense1_cap [0:63];
    reg [15:0] tb_dense2_cap [0:31];
    always @(posedge clk) begin
        prev_layer <= dut.dense_inst.layer;
        if (prev_layer == 1 && dut.dense_inst.layer == 2) begin
            tb_dense1_cap[0] = dut.dense_inst.ram_B[0];
            tb_dense1_cap[1] = dut.dense_inst.ram_B[1];
            tb_dense1_cap[2] = dut.dense_inst.ram_B[2];
            tb_dense1_cap[3] = dut.dense_inst.ram_B[3];
            tb_dense1_cap[4] = dut.dense_inst.ram_B[4];
            tb_dense1_cap[5] = dut.dense_inst.ram_B[5];
            tb_dense1_cap[6] = dut.dense_inst.ram_B[6];
            tb_dense1_cap[7] = dut.dense_inst.ram_B[7];
            tb_dense1_cap[8] = dut.dense_inst.ram_B[8];
            tb_dense1_cap[9] = dut.dense_inst.ram_B[9];
            tb_dense1_cap[10] = dut.dense_inst.ram_B[10];
            tb_dense1_cap[11] = dut.dense_inst.ram_B[11];
            tb_dense1_cap[12] = dut.dense_inst.ram_B[12];
            tb_dense1_cap[13] = dut.dense_inst.ram_B[13];
            tb_dense1_cap[14] = dut.dense_inst.ram_B[14];
            tb_dense1_cap[15] = dut.dense_inst.ram_B[15];
            tb_dense1_cap[16] = dut.dense_inst.ram_B[16];
            tb_dense1_cap[17] = dut.dense_inst.ram_B[17];
            tb_dense1_cap[18] = dut.dense_inst.ram_B[18];
            tb_dense1_cap[19] = dut.dense_inst.ram_B[19];
            tb_dense1_cap[20] = dut.dense_inst.ram_B[20];
            tb_dense1_cap[21] = dut.dense_inst.ram_B[21];
            tb_dense1_cap[22] = dut.dense_inst.ram_B[22];
            tb_dense1_cap[23] = dut.dense_inst.ram_B[23];
            tb_dense1_cap[24] = dut.dense_inst.ram_B[24];
            tb_dense1_cap[25] = dut.dense_inst.ram_B[25];
            tb_dense1_cap[26] = dut.dense_inst.ram_B[26];
            tb_dense1_cap[27] = dut.dense_inst.ram_B[27];
            tb_dense1_cap[28] = dut.dense_inst.ram_B[28];
            tb_dense1_cap[29] = dut.dense_inst.ram_B[29];
            tb_dense1_cap[30] = dut.dense_inst.ram_B[30];
            tb_dense1_cap[31] = dut.dense_inst.ram_B[31];
            tb_dense1_cap[32] = dut.dense_inst.ram_B[32];
            tb_dense1_cap[33] = dut.dense_inst.ram_B[33];
            tb_dense1_cap[34] = dut.dense_inst.ram_B[34];
            tb_dense1_cap[35] = dut.dense_inst.ram_B[35];
            tb_dense1_cap[36] = dut.dense_inst.ram_B[36];
            tb_dense1_cap[37] = dut.dense_inst.ram_B[37];
            tb_dense1_cap[38] = dut.dense_inst.ram_B[38];
            tb_dense1_cap[39] = dut.dense_inst.ram_B[39];
            tb_dense1_cap[40] = dut.dense_inst.ram_B[40];
            tb_dense1_cap[41] = dut.dense_inst.ram_B[41];
            tb_dense1_cap[42] = dut.dense_inst.ram_B[42];
            tb_dense1_cap[43] = dut.dense_inst.ram_B[43];
            tb_dense1_cap[44] = dut.dense_inst.ram_B[44];
            tb_dense1_cap[45] = dut.dense_inst.ram_B[45];
            tb_dense1_cap[46] = dut.dense_inst.ram_B[46];
            tb_dense1_cap[47] = dut.dense_inst.ram_B[47];
            tb_dense1_cap[48] = dut.dense_inst.ram_B[48];
            tb_dense1_cap[49] = dut.dense_inst.ram_B[49];
            tb_dense1_cap[50] = dut.dense_inst.ram_B[50];
            tb_dense1_cap[51] = dut.dense_inst.ram_B[51];
            tb_dense1_cap[52] = dut.dense_inst.ram_B[52];
            tb_dense1_cap[53] = dut.dense_inst.ram_B[53];
            tb_dense1_cap[54] = dut.dense_inst.ram_B[54];
            tb_dense1_cap[55] = dut.dense_inst.ram_B[55];
            tb_dense1_cap[56] = dut.dense_inst.ram_B[56];
            tb_dense1_cap[57] = dut.dense_inst.ram_B[57];
            tb_dense1_cap[58] = dut.dense_inst.ram_B[58];
            tb_dense1_cap[59] = dut.dense_inst.ram_B[59];
            tb_dense1_cap[60] = dut.dense_inst.ram_B[60];
            tb_dense1_cap[61] = dut.dense_inst.ram_B[61];
            tb_dense1_cap[62] = dut.dense_inst.ram_B[62];
            tb_dense1_cap[63] = dut.dense_inst.ram_B[63];
        end
        if (prev_layer == 2 && dut.dense_inst.layer == 3) begin
            tb_dense2_cap[0] = dut.dense_inst.ram_A[0];
            tb_dense2_cap[1] = dut.dense_inst.ram_A[1];
            tb_dense2_cap[2] = dut.dense_inst.ram_A[2];
            tb_dense2_cap[3] = dut.dense_inst.ram_A[3];
            tb_dense2_cap[4] = dut.dense_inst.ram_A[4];
            tb_dense2_cap[5] = dut.dense_inst.ram_A[5];
            tb_dense2_cap[6] = dut.dense_inst.ram_A[6];
            tb_dense2_cap[7] = dut.dense_inst.ram_A[7];
            tb_dense2_cap[8] = dut.dense_inst.ram_A[8];
            tb_dense2_cap[9] = dut.dense_inst.ram_A[9];
            tb_dense2_cap[10] = dut.dense_inst.ram_A[10];
            tb_dense2_cap[11] = dut.dense_inst.ram_A[11];
            tb_dense2_cap[12] = dut.dense_inst.ram_A[12];
            tb_dense2_cap[13] = dut.dense_inst.ram_A[13];
            tb_dense2_cap[14] = dut.dense_inst.ram_A[14];
            tb_dense2_cap[15] = dut.dense_inst.ram_A[15];
            tb_dense2_cap[16] = dut.dense_inst.ram_A[16];
            tb_dense2_cap[17] = dut.dense_inst.ram_A[17];
            tb_dense2_cap[18] = dut.dense_inst.ram_A[18];
            tb_dense2_cap[19] = dut.dense_inst.ram_A[19];
            tb_dense2_cap[20] = dut.dense_inst.ram_A[20];
            tb_dense2_cap[21] = dut.dense_inst.ram_A[21];
            tb_dense2_cap[22] = dut.dense_inst.ram_A[22];
            tb_dense2_cap[23] = dut.dense_inst.ram_A[23];
            tb_dense2_cap[24] = dut.dense_inst.ram_A[24];
            tb_dense2_cap[25] = dut.dense_inst.ram_A[25];
            tb_dense2_cap[26] = dut.dense_inst.ram_A[26];
            tb_dense2_cap[27] = dut.dense_inst.ram_A[27];
            tb_dense2_cap[28] = dut.dense_inst.ram_A[28];
            tb_dense2_cap[29] = dut.dense_inst.ram_A[29];
            tb_dense2_cap[30] = dut.dense_inst.ram_A[30];
            tb_dense2_cap[31] = dut.dense_inst.ram_A[31];
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
            
        $write("RTL_MP1:");
        for(integer i=0; i<400; i=i+1) $write("%0d,", $signed(tb_mp1_cap[i]));
        $display("");
        
        $write("RTL_MP2:");
        for(integer i=0; i<200; i=i+1) $write("%0d,", $signed(tb_mp2_cap[i]));
        $display("");
        
        $write("RTL_DENSE1:");
        for(integer i=0; i<64; i=i+1) $write("%0d,", $signed(tb_dense1_cap[i]));
        $display("");
        
        $write("RTL_DENSE2:");
        for(integer i=0; i<32; i=i+1) $write("%0d,", $signed(tb_dense2_cap[i]));
        $display("");
        
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
`default_nettype wire
