`timescale 1ns / 1ps

module mlp_head (
    input wire clk,
    input wire reset,
    input wire valid_in,
    
    input wire signed [15:0] in_ch0,
    input wire signed [15:0] in_ch1,
    input wire signed [15:0] in_ch2,
    input wire signed [15:0] in_ch3,
    input wire signed [15:0] in_ch4,
    input wire signed [15:0] in_ch5,
    input wire signed [15:0] in_ch6,
    input wire signed [15:0] in_ch7,
    
    output wire signed [15:0] out_digit_0,
    output wire signed [15:0] out_digit_1,
    output wire signed [15:0] out_digit_2,
    output wire signed [15:0] out_digit_3,
    output wire signed [15:0] out_digit_4,
    output wire signed [15:0] out_digit_5,
    output wire signed [15:0] out_digit_6,
    output wire signed [15:0] out_digit_7,
    output wire signed [15:0] out_digit_8,
    output wire signed [15:0] out_digit_9,
    
    output reg valid_out
);

    // Feature Rams
    reg signed [15:0] ram_A [0:207];
    reg signed [15:0] ram_B [0:63];
    reg [7:0] write_ptr;

    // ROM
    reg [255:0] weight_rom [0:991];
    initial begin
        $readmemh("../python_golden_model/mlp_rom.txt", weight_rom);
    end

    // FSM State
    reg [2:0] state;
    localparam IDLE = 0, LOAD_WEIGHT = 1, COMPUTE = 2, DONE = 3;

    reg [1:0] layer; // 1, 2, 3
    reg [2:0] r_idx; // up to 4 for L1
    reg [3:0] c_idx; // up to 12 for L1
    reg [9:0] rom_addr;
    reg [5:0] timer;

    // Feature Selection
    wire [7:0] feat_base = c_idx * 16;
    wire signed [15:0] feat0  = (layer==2) ? ram_B[feat_base + 0]  : ram_A[feat_base + 0];
    wire signed [15:0] feat1  = (layer==2) ? ram_B[feat_base + 1]  : ram_A[feat_base + 1];
    wire signed [15:0] feat2  = (layer==2) ? ram_B[feat_base + 2]  : ram_A[feat_base + 2];
    wire signed [15:0] feat3  = (layer==2) ? ram_B[feat_base + 3]  : ram_A[feat_base + 3];
    wire signed [15:0] feat4  = (layer==2) ? ram_B[feat_base + 4]  : ram_A[feat_base + 4];
    wire signed [15:0] feat5  = (layer==2) ? ram_B[feat_base + 5]  : ram_A[feat_base + 5];
    wire signed [15:0] feat6  = (layer==2) ? ram_B[feat_base + 6]  : ram_A[feat_base + 6];
    wire signed [15:0] feat7  = (layer==2) ? ram_B[feat_base + 7]  : ram_A[feat_base + 7];
    wire signed [15:0] feat8  = (layer==2) ? ram_B[feat_base + 8]  : ram_A[feat_base + 8];
    wire signed [15:0] feat9  = (layer==2) ? ram_B[feat_base + 9]  : ram_A[feat_base + 9];
    wire signed [15:0] feat10 = (layer==2) ? ram_B[feat_base + 10] : ram_A[feat_base + 10];
    wire signed [15:0] feat11 = (layer==2) ? ram_B[feat_base + 11] : ram_A[feat_base + 11];
    wire signed [15:0] feat12 = (layer==2) ? ram_B[feat_base + 12] : ram_A[feat_base + 12];
    wire signed [15:0] feat13 = (layer==2) ? ram_B[feat_base + 13] : ram_A[feat_base + 13];
    wire signed [15:0] feat14 = (layer==2) ? ram_B[feat_base + 14] : ram_A[feat_base + 14];
    wire signed [15:0] feat15 = (layer==2) ? ram_B[feat_base + 15] : ram_A[feat_base + 15];

    wire [255:0] in_val_top = {
        feat15, feat14, feat13, feat12, feat11, feat10, feat9, feat8,
        feat7,  feat6,  feat5,  feat4,  feat3,  feat2,  feat1,  feat0
    };

    // Systolic Array Instance
    wire load_weight = (state == LOAD_WEIGHT);
    wire [255:0] weight_in_left = weight_rom[rom_addr];
    wire [255:0] acc_out_right;

    systolic_array #(.ROWS(16), .COLS(16)) sys_arr (
        .clk(clk),
        .rst(reset),
        .load_weight(load_weight),
        .weight_in_left(weight_in_left),
        .in_val_top(in_val_top),
        .acc_out_right(acc_out_right)
    );

    // External Accumulation Logic
    wire signed [15:0] acc_out_arr [0:15];
    genvar i;
    generate
        for (i=0; i<16; i=i+1) begin : gen_acc
            assign acc_out_arr[i] = acc_out_right[i*16 +: 16];
        end
    endgenerate

    wire [3:0] r = timer - 16;
    wire [5:0] dest_idx = r_idx * 16 + r;
    wire signed [15:0] sys_out = acc_out_arr[r];

    reg signed [15:0] old_val;
    always @(*) begin
        if (c_idx == 0) old_val = 16'd0;
        else if (layer == 1) old_val = ram_B[dest_idx];
        else if (layer == 2) old_val = ram_A[dest_idx];
        else old_val = ram_B[dest_idx];
    end

    wire signed [15:0] final_sum = old_val + sys_out;
    
    wire is_last_col = (layer == 1 && c_idx == 12) || 
                       (layer == 2 && c_idx == 3) || 
                       (layer == 3 && c_idx == 1);
                       
    wire apply_relu = (layer != 3);
    wire signed [15:0] relu_sum = (final_sum[15] == 1) ? 16'd0 : final_sum;
    wire signed [15:0] write_sum = (is_last_col && apply_relu) ? relu_sum : final_sum;

    integer j;
    always @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            write_ptr <= 0;
            valid_out <= 0;
            layer <= 0;
            r_idx <= 0;
            c_idx <= 0;
            rom_addr <= 0;
            timer <= 0;
            for(j=0; j<208; j=j+1) ram_A[j] <= 0;
            for(j=0; j<64; j=j+1) ram_B[j] <= 0;
        end else begin
            case (state)
                IDLE: begin
                    valid_out <= 0;
                    if (valid_in) begin
                        ram_A[write_ptr + 0] <= in_ch0;
                        ram_A[write_ptr + 1] <= in_ch1;
                        ram_A[write_ptr + 2] <= in_ch2;
                        ram_A[write_ptr + 3] <= in_ch3;
                        ram_A[write_ptr + 4] <= in_ch4;
                        ram_A[write_ptr + 5] <= in_ch5;
                        ram_A[write_ptr + 6] <= in_ch6;
                        ram_A[write_ptr + 7] <= in_ch7;
                        write_ptr <= write_ptr + 8;
                        
                        if (write_ptr == 192) begin
                            state <= LOAD_WEIGHT;
                            layer <= 1;
                            r_idx <= 0;
                            c_idx <= 0;
                            rom_addr <= 0;
                            timer <= 0;
                            write_ptr <= 0; // reset
                        end
                    end
                end
                LOAD_WEIGHT: begin
                    if (timer == 15) begin
                        state <= COMPUTE;
                        timer <= 0;
                    end else begin
                        timer <= timer + 1;
                    end
                    // rom_addr pre-increments for the next cycle
                    // The very first cycle of LOAD_WEIGHT uses rom_addr=0, then it becomes 1 for cycle 1.
                    rom_addr <= rom_addr + 1;
                end
                COMPUTE: begin
                    if (timer >= 16 && timer <= 31) begin
                        if (layer == 1) ram_B[dest_idx] <= write_sum;
                        else if (layer == 2) ram_A[dest_idx] <= write_sum;
                        else ram_B[dest_idx] <= write_sum;
                    end
                    
                    if (timer == 31) begin
                        timer <= 0;
                        if (layer == 1) begin
                            if (c_idx == 12) begin
                                c_idx <= 0;
                                if (r_idx == 3) begin
                                    layer <= 2;
                                    r_idx <= 0;
                                end else begin
                                    r_idx <= r_idx + 1;
                                end
                            end else begin
                                c_idx <= c_idx + 1;
                            end
                            state <= LOAD_WEIGHT;
                        end else if (layer == 2) begin
                            if (c_idx == 3) begin
                                c_idx <= 0;
                                if (r_idx == 1) begin
                                    layer <= 3;
                                    r_idx <= 0;
                                end else begin
                                    r_idx <= r_idx + 1;
                                end
                            end else begin
                                c_idx <= c_idx + 1;
                            end
                            state <= LOAD_WEIGHT;
                        end else if (layer == 3) begin
                            if (c_idx == 1) begin
                                state <= DONE;
                            end else begin
                                c_idx <= c_idx + 1;
                                state <= LOAD_WEIGHT;
                            end
                        end
                    end else begin
                        timer <= timer + 1;
                    end
                end
                DONE: begin
                    valid_out <= 1;
                    state <= IDLE;
                end
            endcase
        end
    end

    assign out_digit_0 = ram_B[0];
    assign out_digit_1 = ram_B[1];
    assign out_digit_2 = ram_B[2];
    assign out_digit_3 = ram_B[3];
    assign out_digit_4 = ram_B[4];
    assign out_digit_5 = ram_B[5];
    assign out_digit_6 = ram_B[6];
    assign out_digit_7 = ram_B[7];
    assign out_digit_8 = ram_B[8];
    assign out_digit_9 = ram_B[9];

endmodule
