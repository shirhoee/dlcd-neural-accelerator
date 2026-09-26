`timescale 1ns / 1ps

module window_gen (
    input wire clk,
    input wire reset,
    input wire advance,           // Handshake: 1 to advance the sliding window pipeline
    
    // Interface to Image RAM (Combinational read)
    output wire [8:0] pixel_addr, // 0 to 399
    input wire signed [15:0] pixel_in,
    
    // Output 3x3 Window (Parallel, Q7.8)
    output wire signed [15:0] out_0, // Top-Left
    output wire signed [15:0] out_1, // Top-Mid
    output wire signed [15:0] out_2, // Top-Right
    output wire signed [15:0] out_3, // Mid-Left
    output wire signed [15:0] out_4, // Center
    output wire signed [15:0] out_5, // Mid-Right
    output wire signed [15:0] out_6, // Bottom-Left
    output wire signed [15:0] out_7, // Bottom-Mid
    output wire signed [15:0] out_8, // Bottom-Right
    
    output wire window_valid,     // High when out_0..8 contain a valid window
    output wire done              // High when all 400 windows have been generated
);

    // Coordinate generator for the padded 22x22 virtual grid
    reg [4:0] vx; // 0 to 21
    reg [4:0] vy; // 0 to 21
    reg is_done;

    // Track the coordinates of the pixel currently in SR[0]
    reg [4:0] sr_x;
    reg [4:0] sr_y;

    // Shift register: 2 full rows (22 each) + 3 pixels = 47 length
    reg signed [15:0] SR [0:46];
    integer i;

    // Combinational addressing for the 20x20 actual image (indices 0 to 399)
    wire is_inside = (vx >= 1 && vx <= 20 && vy >= 1 && vy <= 20);
    assign pixel_addr = is_inside ? ((vy - 1) * 20 + (vx - 1)) : 9'd0;
    
    // Inject literal zero if we are in the padding region
    wire signed [15:0] current_val = is_inside ? pixel_in : 16'sd0;

    // Fixed tap mapping for the 3x3 window
    assign out_0 = SR[46];
    assign out_1 = SR[45];
    assign out_2 = SR[44];
    assign out_3 = SR[24];
    assign out_4 = SR[23];
    assign out_5 = SR[22];
    assign out_6 = SR[2];
    assign out_7 = SR[1];
    assign out_8 = SR[0];

    // A valid window is fully formed when the bottom-right pixel (at least x=2, y=2 in the padded grid) is in SR[0]
    assign window_valid = (sr_x >= 2 && sr_y >= 2);
    assign done = is_done;

    always @(posedge clk) begin
        if (reset) begin
            vx <= 0;
            vy <= 0;
            sr_x <= 0;
            sr_y <= 0;
            is_done <= 0;
            for (i = 0; i < 47; i = i + 1) begin
                SR[i] <= 0;
            end
        end else if (advance && !is_done) begin
            // Shift pipeline
            for (i = 46; i > 0; i = i - 1) begin
                SR[i] <= SR[i-1];
            end
            SR[0] <= current_val;
            
            // Track what coordinate is now in SR[0]
            sr_x <= vx;
            sr_y <= vy;

            // Increment virtual grid coordinates
            if (vx == 21) begin
                vx <= 0;
                if (vy == 21) begin
                    is_done <= 1;
                end else begin
                    vy <= vy + 1;
                end
            end else begin
                vx <= vx + 1;
            end
        end else if (is_done) begin
            // Clear coordinates once done so window_valid pulses exactly once for the final window
            sr_x <= 0;
            sr_y <= 0;
        end
    end

endmodule
