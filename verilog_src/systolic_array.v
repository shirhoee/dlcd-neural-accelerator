`timescale 1ns / 1ps

module systolic_array #(
    parameter ROWS = 16,  // Number of Neurons
    parameter COLS = 100  // Number of Input Features
)(
    input  wire clk,
    input  wire rst,
    input  wire load_weight,

    input  wire [(ROWS*16)-1:0] weight_in_left,
    input  wire [(COLS*16)-1:0] in_val_top,
    output wire [(ROWS*16)-1:0] acc_out_right
);

    wire signed [15:0] w_wire [0:ROWS-1][0:COLS];
    wire signed [15:0] x_wire [0:ROWS][0:COLS-1];
    wire signed [15:0] y_wire [0:ROWS-1][0:COLS];

    genvar r, c;
    generate
        for (r = 0; r < ROWS; r = r + 1) begin : gen_row
            assign w_wire[r][0] = weight_in_left[(r*16) +: 16];
            assign y_wire[r][0] = 16'd0;
            assign acc_out_right[(r*16) +: 16] = y_wire[r][COLS];

            for (c = 0; c < COLS; c = c + 1) begin : gen_col
                if (r == 0) begin
                    assign x_wire[0][c] = in_val_top[(c*16) +: 16];
                end

                systolic_pe pe_inst (
                    .clk(clk),
                    .rst(rst),
                    .load_weight(load_weight),
                    .weight_in (w_wire[r][c]),
                    .weight_out(w_wire[r][c+1]),
                    .in_val_in (x_wire[r][c]),
                    .in_val_out(x_wire[r+1][c]),
                    .acc_in    (y_wire[r][c]),
                    .acc_out   (y_wire[r][c+1])
                );
            end
        end
    endgenerate

endmodule