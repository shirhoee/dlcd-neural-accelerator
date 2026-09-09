module relu_q4_12 (
    input wire signed [15:0] in_val,
    output reg signed [15:0] out_val
);

    always @(*) begin
        out_val = in_val[15] ? 16'sd0 : in_val;
    end

endmodule