module mac_q6_9 (
    input wire signed [15:0] weight,
    input wire signed [15:0] in_val,
    input wire signed [15:0] acc_in,
    output reg signed [15:0] acc_out
);

    wire signed [31:0] product;

    assign product = weight * in_val;
    always @(*) begin
        acc_out = acc_in + product[24:9];
    end

endmodule