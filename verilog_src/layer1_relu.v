`timescale 1ns / 1ps

module layer1_relu #(
    parameter ROWS = 16
)(
    input  wire [(ROWS*16)-1:0] acc_in,
    output wire [(ROWS*16)-1:0] relu_out
);

    genvar r;
    generate
        for (r = 0; r < ROWS; r = r + 1) begin : gen_relu
            relu_q7_8 relu_inst (
                .in_val(acc_in[(r*16) +: 16]),
                .out_val(relu_out[(r*16) +: 16])
            );
        end
    endgenerate

endmodule