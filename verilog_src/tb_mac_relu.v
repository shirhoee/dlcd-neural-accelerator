`timescale 1ns / 1ps

module tb_mac_relu;
    // Inputs
    reg signed [15:0] weight;
    reg signed [15:0] in_val;
    reg signed [15:0] acc_in;
    
    // Outputs
    wire signed [15:0] mac_out;
    wire signed [15:0] relu_out;

    // Expected Output (for self-checking)
    reg signed [15:0] expected_mac;
    reg signed [15:0] expected_relu;

    // Test Vector Arrays (100 test cases)
    reg [15:0] test_weights [0:99];
    reg [15:0] test_in_vals [0:99];
    reg [15:0] test_acc_ins [0:99];
    reg [15:0] expected_macs [0:99];
    reg [15:0] expected_relus [0:99];

    integer i;
    integer errors = 0;

    // Instantiate MAC
    mac_q7_8 u_mac (
        .weight(weight),
        .in_val(in_val),
        .acc_in(acc_in),
        .acc_out(mac_out)
    );

    // Instantiate ReLU connected to MAC output
    relu_q7_8 u_relu (
        .in_val(mac_out),
        .out_val(relu_out)
    );

    initial begin
        // Load Python-generated test vectors
        $readmemh("mac_weights.hex", test_weights);
        $readmemh("mac_in_vals.hex", test_in_vals);
        $readmemh("mac_acc_ins.hex", test_acc_ins);
        $readmemh("mac_expected_mac.hex", expected_macs);
        $readmemh("mac_expected_relu.hex", expected_relus);

        $display("----------------------------------------");
        $display("Starting MAC+ReLU Self-Checking Test...");
        $display("----------------------------------------");

        for (i = 0; i < 100; i = i + 1) begin
            weight = test_weights[i];
            in_val = test_in_vals[i];
            acc_in = test_acc_ins[i];
            expected_mac = expected_macs[i];
            expected_relu = expected_relus[i];

            #10; // Wait for combinational logic to settle

            if (mac_out !== expected_mac || relu_out !== expected_relu) begin
                $display("FAIL at vector %0d: W=%h, In=%h, AccIn=%h", i, weight, in_val, acc_in);
                $display("  MAC: Expected %h, Got %h", expected_mac, mac_out);
                $display("  ReLU: Expected %h, Got %h", expected_relu, relu_out);
                errors = errors + 1;
            end
        end

        $display("----------------------------------------");
        if (errors == 0)
            $display("PASS: All 100 MAC+ReLU tests match Python golden model!");
        else
            $display("FAIL: %0d errors found.", errors);
        $display("----------------------------------------");
        
        $finish;
    end
endmodule