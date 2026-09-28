`timescale 1ns / 1ps

/*
 * V2 - N5: Conv2 Array
 * 
 * ==========================================
 * INTERFACE CONTRACT: BIT-SLICING CONVENTION
 * ==========================================
 * Flat 4,608-bit bus for weights:
 * weight_out = conv2_weights[ (oc * 576) + (ic * 144) + (tap_idx * 16) +: 16 ]
 * oc: 0 to 7
 * ic: 0 to 3
 * tap_idx: 0 to 8
 */

module conv2_array (
    input wire clk,
    input wire reset,
    
    // Weight Delivery
    input wire [4607:0] conv2_weights,
    
    // Input Stream
    input wire valid_in,
    input wire signed [15:0] in_ch0,
    input wire signed [15:0] in_ch1,
    input wire signed [15:0] in_ch2,
    input wire signed [15:0] in_ch3,
    
    // Output Stream
    output wire valid_out,
    output wire signed [15:0] out_ch0,
    output wire signed [15:0] out_ch1,
    output wire signed [15:0] out_ch2,
    output wire signed [15:0] out_ch3,
    output wire signed [15:0] out_ch4,
    output wire signed [15:0] out_ch5,
    output wire signed [15:0] out_ch6,
    output wire signed [15:0] out_ch7,
    output wire done
);

    // 100-word deep buffers
    reg signed [15:0] buf_ch0 [0:99];
    reg signed [15:0] buf_ch1 [0:99];
    reg signed [15:0] buf_ch2 [0:99];
    reg signed [15:0] buf_ch3 [0:99];
    
    reg [6:0] write_addr;

    localparam ST_LOAD       = 3'd0;
    localparam ST_FETCH      = 3'd1;
    localparam ST_MAC        = 3'd2;
    localparam ST_WAIT_VALID = 3'd3;
    localparam ST_ADVANCE    = 3'd4;
    localparam ST_DONE       = 3'd5;

    reg [2:0] state;
    reg [3:0] mac_cnt;
    
    wire advance;
    wire [6:0] p_addr;
    wire w_valid;
    wire w_done;
    
    wire signed [15:0] p_in0 = buf_ch0[p_addr];
    wire signed [15:0] p_in1 = buf_ch1[p_addr];
    wire signed [15:0] p_in2 = buf_ch2[p_addr];
    wire signed [15:0] p_in3 = buf_ch3[p_addr];
    
    wire signed [15:0] t0_0, t0_1, t0_2, t0_3, t0_4, t0_5, t0_6, t0_7, t0_8;
    conv2_window_gen wg0 (.clk(clk), .reset(reset), .advance(advance), .pixel_addr(p_addr), .pixel_in(p_in0), .out_0(t0_0), .out_1(t0_1), .out_2(t0_2), .out_3(t0_3), .out_4(t0_4), .out_5(t0_5), .out_6(t0_6), .out_7(t0_7), .out_8(t0_8), .window_valid(w_valid), .done(w_done));

    wire signed [15:0] t1_0, t1_1, t1_2, t1_3, t1_4, t1_5, t1_6, t1_7, t1_8;
    conv2_window_gen wg1 (.clk(clk), .reset(reset), .advance(advance), .pixel_addr(), .pixel_in(p_in1), .out_0(t1_0), .out_1(t1_1), .out_2(t1_2), .out_3(t1_3), .out_4(t1_4), .out_5(t1_5), .out_6(t1_6), .out_7(t1_7), .out_8(t1_8), .window_valid(), .done());

    wire signed [15:0] t2_0, t2_1, t2_2, t2_3, t2_4, t2_5, t2_6, t2_7, t2_8;
    conv2_window_gen wg2 (.clk(clk), .reset(reset), .advance(advance), .pixel_addr(), .pixel_in(p_in2), .out_0(t2_0), .out_1(t2_1), .out_2(t2_2), .out_3(t2_3), .out_4(t2_4), .out_5(t2_5), .out_6(t2_6), .out_7(t2_7), .out_8(t2_8), .window_valid(), .done());

    wire signed [15:0] t3_0, t3_1, t3_2, t3_3, t3_4, t3_5, t3_6, t3_7, t3_8;
    conv2_window_gen wg3 (.clk(clk), .reset(reset), .advance(advance), .pixel_addr(), .pixel_in(p_in3), .out_0(t3_0), .out_1(t3_1), .out_2(t3_2), .out_3(t3_3), .out_4(t3_4), .out_5(t3_5), .out_6(t3_6), .out_7(t3_7), .out_8(t3_8), .window_valid(), .done());

    reg signed [15:0] mux_p0, mux_p1, mux_p2, mux_p3;
    always @(*) begin
        case (mac_cnt)
            0: begin mux_p0 = t0_0; mux_p1 = t1_0; mux_p2 = t2_0; mux_p3 = t3_0; end
            1: begin mux_p0 = t0_1; mux_p1 = t1_1; mux_p2 = t2_1; mux_p3 = t3_1; end
            2: begin mux_p0 = t0_2; mux_p1 = t1_2; mux_p2 = t2_2; mux_p3 = t3_2; end
            3: begin mux_p0 = t0_3; mux_p1 = t1_3; mux_p2 = t2_3; mux_p3 = t3_3; end
            4: begin mux_p0 = t0_4; mux_p1 = t1_4; mux_p2 = t2_4; mux_p3 = t3_4; end
            5: begin mux_p0 = t0_5; mux_p1 = t1_5; mux_p2 = t2_5; mux_p3 = t3_5; end
            6: begin mux_p0 = t0_6; mux_p1 = t1_6; mux_p2 = t2_6; mux_p3 = t3_6; end
            7: begin mux_p0 = t0_7; mux_p1 = t1_7; mux_p2 = t2_7; mux_p3 = t3_7; end
            8: begin mux_p0 = t0_8; mux_p1 = t1_8; mux_p2 = t2_8; mux_p3 = t3_8; end
            default: begin mux_p0 = 16'd0; mux_p1 = 16'd0; mux_p2 = 16'd0; mux_p3 = 16'd0; end
        endcase
    end

    wire signed [15:0] w_in [0:7][0:3];
    genvar oc, ic;
    generate
        for (oc = 0; oc < 8; oc = oc + 1) begin : gen_oc
            for (ic = 0; ic < 4; ic = ic + 1) begin : gen_ic
                assign w_in[oc][ic] = conv2_weights[(oc * 576) + (ic * 144) + (mac_cnt * 16) +: 16];
            end
        end
    endgenerate

    wire clr_acc = (state == ST_MAC && mac_cnt == 0);
    wire mac_en = (state == ST_MAC);
    wire [7:0] pe_valid;
    
    wire signed [15:0] pe_out [0:7];

    generate
        for (oc = 0; oc < 8; oc = oc + 1) begin : gen_pe
            conv2_pe pe (
                .clk(clk), .reset(reset),
                .clr_acc(clr_acc), .mac_en(mac_en),
                .pixel_in_0(mux_p0), .pixel_in_1(mux_p1), .pixel_in_2(mux_p2), .pixel_in_3(mux_p3),
                .weight_in_0(w_in[oc][0]), .weight_in_1(w_in[oc][1]), .weight_in_2(w_in[oc][2]), .weight_in_3(w_in[oc][3]),
                .out_acc(pe_out[oc]), .valid_out(pe_valid[oc])
            );
        end
    endgenerate

    assign out_ch0 = pe_out[0];
    assign out_ch1 = pe_out[1];
    assign out_ch2 = pe_out[2];
    assign out_ch3 = pe_out[3];
    assign out_ch4 = pe_out[4];
    assign out_ch5 = pe_out[5];
    assign out_ch6 = pe_out[6];
    assign out_ch7 = pe_out[7];
    assign valid_out = pe_valid[0];
    assign done = (state == ST_DONE);

    assign advance = (state == ST_ADVANCE) || (state == ST_FETCH && !w_valid);
    
    always @(posedge clk) begin
        if (reset) begin
            state <= ST_LOAD;
            write_addr <= 0;
            mac_cnt <= 0;
        end else begin
            case (state)
                ST_LOAD: begin
                    if (valid_in) begin
                        buf_ch0[write_addr] <= in_ch0;
                        buf_ch1[write_addr] <= in_ch1;
                        buf_ch2[write_addr] <= in_ch2;
                        buf_ch3[write_addr] <= in_ch3;
                        if (write_addr == 99) begin
                            state <= ST_FETCH;
                        end else begin
                            write_addr <= write_addr + 1;
                        end
                    end
                end
                ST_FETCH: begin
                    if (w_valid) begin
                        state <= ST_MAC;
                        mac_cnt <= 0;
                    end
                end
                ST_MAC: begin
                    if (mac_cnt == 8) begin
                        state <= ST_WAIT_VALID;
                    end else begin
                        mac_cnt <= mac_cnt + 1;
                    end
                end
                ST_WAIT_VALID: begin
                    if (w_done) begin
                        state <= ST_DONE;
                    end else begin
                        state <= ST_ADVANCE;
                    end
                end
                ST_ADVANCE: begin
                    state <= ST_FETCH;
                end
                ST_DONE: begin
                    // Idle
                end
            endcase
        end
    end

endmodule
