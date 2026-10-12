import os
from playwright.sync_api import sync_playwright

doc_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(doc_dir, "conv_pe_circuit_diagram.png").replace("\\", "/")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mini Project Submission - DLCD Neural Accelerator</title>
<style>
  @page {{
    size: A4;
    margin: 14mm 14mm 14mm 14mm;
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      color: #718096;
    }}
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1a202c;
    line-height: 1.45;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }}
  .header-block {{
    border-bottom: 2px solid #1a365d;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }}
  h1 {{
    color: #1a365d;
    font-size: 15pt;
    margin-top: 0;
    margin-bottom: 6px;
    line-height: 1.2;
    text-align: center;
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 20px;
    font-size: 9pt;
    color: #4a5568;
    margin-top: 6px;
    background: #f7fafc;
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}
  .meta-grid strong {{
    color: #2d3748;
  }}
  h2 {{
    color: #2b6cb0;
    font-size: 11.5pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3px;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}
  h3 {{
    color: #2d3748;
    font-size: 9.5pt;
    margin-top: 8px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }}
  p, ul, ol {{
    margin-top: 3px;
    margin-bottom: 6px;
  }}
  li {{
    margin-bottom: 2px;
  }}
  ul {{
    padding-left: 18px;
  }}
  ol {{
    padding-left: 18px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 10px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }}
  th, td {{
    border: 1px solid #cbd5e0;
    padding: 4px 6px;
    text-align: left;
  }}
  th {{
    background-color: #ebf8ff;
    color: #2b6cb0;
    font-weight: 600;
  }}
  tr:nth-child(even) td {{
    background-color: #f7fafc;
  }}
  .schematic-container {{
    text-align: center;
    margin: 6px 0 8px 0;
    page-break-inside: avoid;
  }}
  .schematic-container img {{
    max-width: 92%;
    max-height: 230px;
    object-fit: contain;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
  }}
  .caption {{
    font-size: 8pt;
    color: #4a5568;
    margin-top: 4px;
    font-style: italic;
  }}
  pre, code {{
    font-family: "Consolas", "Courier New", monospace;
  }}
  code {{
    background-color: #edf2f7;
    padding: 1px 3px;
    border-radius: 2px;
    font-size: 8.5pt;
    color: #2b6cb0;
  }}
  pre {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3182ce;
    padding: 6px 8px;
    font-size: 7.8pt;
    line-height: 1.3;
    overflow-x: auto;
    border-radius: 3px;
    page-break-inside: avoid;
    margin: 4px 0 8px 0;
  }}
  .math-block {{
    background-color: #f7fafc;
    border-left: 3px solid #4299e1;
    padding: 4px 8px;
    margin: 4px 0;
    font-family: "Georgia", serif;
    font-size: 9.5pt;
  }}
  .code-columns {{
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 10px;
    margin-top: 4px;
  }}
  .code-columns pre {{
    font-size: 7.2pt;
    line-height: 1.25;
  }}
  .page-break {{
    page-break-before: always;
  }}
</style>
</head>
<body>

<div class="header-block">
  <h1>Mini Project Submission: Digital Circuit Design Specification &amp; Datapath Schematic</h1>
  <div class="meta-grid">
    <div><strong>Course:</strong> Digital Logic &amp; Computer Design (DLCD)</div>
    <div><strong>Student Name:</strong> Shreyansh Raj</div>
    <div><strong>Project Title:</strong> Hardware Neural Network Accelerator</div>
    <div><strong>SRN / Roll Number:</strong> [SRN / Roll Number]</div>
    <div><strong>Selected Module:</strong> Conv PE (<code>conv_pe.v</code>) with Q7.8 MAC (<code>mac_q7_8.v</code>)</div>
    <div><strong>Date:</strong> October 2026</div>
  </div>
</div>

<h2>1. Executive Summary &amp; Module Purpose</h2>
<p>
In the custom digital neural network accelerator, the <strong>Convolutional Processing Element (<code>conv_pe.v</code>)</strong> executes the 2D spatial convolution for the frontend convolutional layer (Conv1).
</p>
<p>
A fully unrolled 2D convolution requires 9 parallel hardware multipliers per output channel, which demands substantial FPGA DSP and logic resources. To minimize area and routing complexity, this design implements a <strong>9-tap time-multiplexed, weight-stationary sequential Multiply-Accumulate (MAC) processing element</strong>.
</p>

<h3>Key Architectural Characteristics:</h3>
<ul>
  <li><strong>Arithmetic Precision:</strong> Signed Q7.8 Fixed-Point (16-bit signed two's complement: 1 sign bit, 7 integer bits, 8 fractional bits; scale factor <em>S = 2<sup>8</sup> = 256</em>, dynamic range [-128.0, +127.996]).</li>
  <li><strong>Dataflow:</strong> Weight-Stationary. The 9 filter weights for the 3 &times; 3 kernel are shifted into internal registers during configuration and held stationary while incoming streaming pixels are evaluated sequentially.</li>
  <li><strong>Cycle Budget &amp; Throughput:</strong> Exactly 9 clock cycles per 3 &times; 3 receptive field window; produces 1 valid output feature every 9 cycles with continuous streaming support.</li>
  <li><strong>Hardware Component Footprint (<code>conv_pe</code>):</strong>
    1 Signed 16 &times; 16 Multiplier (<code>mac_q7_8.v</code>), 
    1 Signed 16-bit Adder (<code>mac_q7_8.v</code>), 
    9 16-bit Weight Shift Registers (<code>weights[0:8]</code>; intentionally unreset), 
    1 16-bit Accumulator Register (<code>out_acc</code>), 
    1 16-bit 2-to-1 Feedback Multiplexer (<code>clr_acc</code> selector), 
    1 16-bit 9-to-1 Weight Multiplexer (addressed by <code>tap_idx</code>), 
    1 4-bit Modulo-9 Ring Counter with Comparator (<code>tap_idx</code>, 0 to 8), and 
    1 1-bit Output Valid Flip-Flop (<code>valid_out</code>).
    <em>(Note: The Conv1 layer in <code>conv1_array.v</code> instantiates 4 of these <code>conv_pe</code> elements in parallel, one per output channel).</em>
  </li>
</ul>

<h2>2. Port Interface &amp; Signal Contract</h2>
<table>
  <thead>
    <tr>
      <th style="width: 14%;">Signal Name</th>
      <th style="width: 9%;">Direction</th>
      <th style="width: 10%;">Bit Width</th>
      <th style="width: 9%;">Type</th>
      <th style="width: 11%;">Active Level</th>
      <th>Functional Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>clk</code></td>
      <td>Input</td>
      <td>1</td>
      <td>Clock</td>
      <td>Rising Edge</td>
      <td>Primary system clock (synchronous domain).</td>
    </tr>
    <tr>
      <td><code>reset</code></td>
      <td>Input</td>
      <td>1</td>
      <td>Control</td>
      <td>High (1)</td>
      <td>Synchronous reset. Resets <code>tap_idx</code>, <code>out_acc</code>, and <code>valid_out</code> to 0. <em>(Weight registers are intentionally not reset to conserve routing resources).</em></td>
    </tr>
    <tr>
      <td><code>load_weight</code></td>
      <td>Input</td>
      <td>1</td>
      <td>Control</td>
      <td>High (1)</td>
      <td>Active-high shift enable for serial weight loading. Shift order requires reverse sequence (W<sub>8</sub> first down to W<sub>0</sub> last) so that W<sub>0</sub> resides in <code>weights[0]</code>.</td>
    </tr>
    <tr>
      <td><code>weight_in</code></td>
      <td>Input</td>
      <td>[15:0]</td>
      <td>Data (Q7.8)</td>
      <td>—</td>
      <td>Serial 16-bit signed weight stream fed during offline configuration.</td>
    </tr>
    <tr>
      <td><code>mac_en</code></td>
      <td>Input</td>
      <td>1</td>
      <td>Control</td>
      <td>High (1)</td>
      <td>Clock-enable for MAC computation and tap counter advance. When low, <code>tap_idx</code> and <code>out_acc</code> freeze their states.</td>
    </tr>
    <tr>
      <td><code>clr_acc</code></td>
      <td>Input</td>
      <td>1</td>
      <td>Control</td>
      <td>High (1)</td>
      <td>Asserted during Tap 0 to clear accumulator feedback to <code>16'sd0</code> for starting a new convolution window.</td>
    </tr>
    <tr>
      <td><code>pixel_in</code></td>
      <td>Input</td>
      <td>[15:0]</td>
      <td>Data (Q7.8)</td>
      <td>—</td>
      <td>16-bit signed streaming pixel value from sliding-window line buffers.</td>
    </tr>
    <tr>
      <td><code>out_acc</code></td>
      <td>Output</td>
      <td>[15:0]</td>
      <td>Data (Q7.8)</td>
      <td>—</td>
      <td>16-bit signed accumulated convolution sum. Valid when <code>valid_out</code> is asserted.</td>
    </tr>
    <tr>
      <td><code>valid_out</code></td>
      <td>Output</td>
      <td>1</td>
      <td>Status</td>
      <td>High (1)</td>
      <td>1-cycle active-high pulse registered on the clock cycle following Tap 8, indicating that the completed 9-tap sum is valid on <code>out_acc</code>.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>3. Register Transfer Level (RTL) Datapath Schematic</h2>
<div class="schematic-container">
  <img src="file:///{img_path}" alt="Conv1 Processing Element Circuit Diagram">
  <div class="caption">Figure 1: Complete Register-Transfer Level (RTL) Datapath Schematic of the Convolutional Processing Element (<code>conv_pe.v</code>) with Q7.8 MAC Core (<code>mac_q7_8.v</code>).</div>
</div>

<h3>Datapath Breakdown:</h3>
<ol>
  <li><strong>Weight Storage &amp; Selection:</strong> The 9 kernel coefficients (W<sub>0</sub> to W<sub>8</sub>) reside in a 9 &times; 16-bit shift register. A 9-to-1 multiplexer driven by <code>tap_idx[3:0]</code> routes <code>weights[tap_idx]</code> to the multiplier.</li>
  <li><strong>Signed Multiplier (<code>mac_q7_8</code>):</strong> Multiplies selected 16-bit signed weight and streaming 16-bit signed <code>pixel_in</code>, producing a 32-bit signed product in <strong>Q15.16</strong> format.</li>
  <li><strong>Truncation Slice:</strong> Combinational extraction of <code>product[23:8]</code>. Bits <code>[31:24]</code> are dropped based on verified headroom, and bits <code>[7:0]</code> are truncated (floor), aligning the result back to Q7.8 format at zero logic gate cost.</li>
  <li><strong>Accumulator Feedback &amp; MUX:</strong> A 2-to-1 multiplexer selects <code>16'sd0</code> (when <code>clr_acc = 1</code> during Tap 0) or <code>out_acc</code> (when <code>clr_acc = 0</code>). The 16-bit signed adder sums the truncated product with this accumulator base.</li>
  <li><strong>Output Registers:</strong> When <code>mac_en = 1</code>, <code>out_acc</code> registers the adder sum on each clock edge. On <code>tap_idx == 8</code>, <code>valid_out</code> registers high for the subsequent clock cycle and <code>tap_idx</code> rolls over to 0.</li>
</ol>

<h2>4. Control Unit &amp; Tap Sequencer</h2>
<p>
The module avoids complex FSM control overhead by employing a synchronous 4-bit modulo-9 ring counter (<code>tap_idx</code>, counting 0 to 8) enabled by <code>mac_en</code>. When <code>mac_en = 0</code>, the counter freezes in place; it does not jump to an idle state. Weight loading is orthogonal via <code>load_weight</code>.
</p>

<h3>Modulo-9 Ring Counter Sequence &amp; Truth Table:</h3>
<table>
  <thead>
    <tr>
      <th>Cycle Phase</th>
      <th><code>mac_en</code></th>
      <th><code>clr_acc</code></th>
      <th><code>tap_idx</code></th>
      <th>Feedback MUX (<code>acc_in</code>)</th>
      <th>Multiplier Operation (P<sub>i</sub>)</th>
      <th><code>valid_out</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Tap 0</strong></td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td><code>16'sd0</code></td>
      <td>P<sub>0</sub> = pixel<sub>0</sub> &times; W<sub>0</sub></td>
      <td>0</td>
    </tr>
    <tr>
      <td><strong>Tap 1</strong></td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td><code>out_acc</code> (P<sub>0</sub>)</td>
      <td>P<sub>1</sub> = pixel<sub>1</sub> &times; W<sub>1</sub></td>
      <td>0</td>
    </tr>
    <tr>
      <td><strong>Tap 2</strong></td>
      <td>1</td>
      <td>0</td>
      <td>2</td>
      <td><code>out_acc</code> (P<sub>0</sub> + P<sub>1</sub>)</td>
      <td>P<sub>2</sub> = pixel<sub>2</sub> &times; W<sub>2</sub></td>
      <td>0</td>
    </tr>
    <tr>
      <td><strong>Tap 3..7</strong></td>
      <td>1</td>
      <td>0</td>
      <td>3..7</td>
      <td><code>out_acc</code> (&sum;<sub>k=0..i-1</sub> P<sub>k</sub>)</td>
      <td>P<sub>i</sub> = pixel<sub>i</sub> &times; W<sub>i</sub></td>
      <td>0</td>
    </tr>
    <tr>
      <td><strong>Tap 8</strong></td>
      <td>1</td>
      <td>0</td>
      <td>8</td>
      <td><code>out_acc</code> (&sum;<sub>k=0..7</sub> P<sub>k</sub>)</td>
      <td>P<sub>8</sub> = pixel<sub>8</sub> &times; W<sub>8</sub></td>
      <td>0</td>
    </tr>
    <tr>
      <td><strong>Handoff (Next Tap 0)</strong></td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td><code>16'sd0</code></td>
      <td>P<sub>0</sub>' = pixel<sub>0</sub>' &times; W<sub>0</sub></td>
      <td><strong>1</strong> (Asserted for completed window)</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>5. Q7.8 Fixed-Point Mathematical Formulation</h2>
<p>
Fixed-point arithmetic maps real values to signed integers using uniform scaling factor <em>S = 2<sup>B</sup></em> (where <em>B = 8</em>):
<em>X</em><sub>fixed</sub> = round(<em>X</em><sub>real</sub> &times; 2<sup>8</sup>).
</p>

<h3>Multiplication &amp; Bit Format:</h3>
<p>
Multiplying two 16-bit signed Q7.8 numbers (each having 1 sign bit, 7 integer bits, 8 fractional bits) produces a 32-bit signed product in <strong>Q15.16</strong> format:
</p>
<div class="math-block">
  Product = <em>A</em> &times; <em>B</em> &nbsp;&nbsp;&rArr;&nbsp;&nbsp; 1 sign bit + 15 integer bits + 16 fractional bits = 32 bits (Scale 2<sup>16</sup>)
</div>
<p>
To rescale to 16-bit Q7.8, the product is scaled by 2<sup>-8</sup> via bit-slicing: 
<strong>Product<sub>Q7.8</sub> = &lfloor; (<em>A</em> &times; <em>B</em>) / 2<sup>8</sup> &rfloor; = Product[23:8]</strong>.
</p>

<h3>Bit-Level Slice of <code>product[31:0]</code>:</h3>
<pre>
Product [31:0]:
  [31:24] (8 bits) : Extended integer bits (discarded; headroom bounded to prevent overflow)
  [23:16] (8 bits) : Q7.8 Integer part (1 sign bit + 7 integer bits)
  [15:8]  (8 bits) : Q7.8 Fractional part
  [7:0]   (8 bits) : Lower sub-fractional bits (truncated floor; dropped)
</pre>

<h3>Headroom &amp; Overflow Behavior:</h3>
<p>
The RTL adder and accumulator implement standard two's complement 16-bit arithmetic without saturation logic; if a value exceeds [-128.0, +127.996], it wraps around. To prevent overflow in hardware, the neural network training pipeline incorporates an upstream Headroom Gate during weight export:
</p>
<ul>
  <li>Maximum model output logit observed across the test set is 72.5, safely below the Q7.8 ceiling of +127.996.</li>
  <li>Input pixels are normalized within [0.0, 1.0] (0 to 255 in Q7.8), and kernel weights are bounded, ensuring intermediate 9-tap sums remain strictly within the 16-bit dynamic range.</li>
</ul>

<h2>6. Cycle-Accurate Timing Diagram</h2>
<pre>
Clock Cycle :  0    1    2    3   ...   7    8    9   10   11   ...
clk         : _/ \\_/ \\_/ \\_/ \\_/ ... \\_/ \\_/ \\_/ \\_/ \\_/ \\_/ \\_
mac_en      : _____/==============================================
clr_acc     : _____/=====\\___________________________/=====\\______
pixel_in    : -----&lt; p0 &gt;&lt; p1 &gt;&lt; p2 &gt; ... &lt; p7 &gt;&lt; p8 &gt;&lt; q0 &gt;&lt; q1 &gt;-
tap_idx     : -----&lt;  0 &gt;&lt;  1 &gt;&lt;  2 &gt; ... &lt;  7 &gt;&lt;  8 &gt;&lt;  0 &gt;&lt;  1 &gt;-
weights[idx]: -----&lt; w0 &gt;&lt; w1 &gt;&lt; w2 &gt; ... &lt; w7 &gt;&lt; w8 &gt;&lt; w0 &gt;&lt; w1 &gt;-
mac_result  : -----&lt; Acc0&gt;&lt; Acc1&gt;&lt; Acc2&gt; ...&lt;Acc7&gt;&lt;Acc8&gt;&lt;New0&gt;&lt;New1&gt;
out_acc     : ----------&lt;Acc0&gt;&lt;Acc1&gt; ... ... &lt;Acc7&gt;&lt;Acc8&gt;&lt;New0&gt;---
valid_out   : _______________________________________/=====\\______
                                                          ^
                                                Window 1 Result Valid
</pre>

<div class="page-break"></div>

<h2>7. Verilog Code Implementation</h2>

<div class="code-columns">
  <div>
    <h3>Core MAC Module (<code>mac_q7_8.v</code>):</h3>
<pre>
module mac_q7_8 (
    input  wire signed [15:0] weight,
    input  wire signed [15:0] in_val,
    input  wire signed [15:0] acc_in,
    output reg  signed [15:0] acc_out
);
    wire signed [31:0] product;

    assign product = weight * in_val;
    always @(*) begin
        acc_out = acc_in + product[23:8];
    end
endmodule
</pre>
  </div>
  <div>
    <h3>Processing Element Module (<code>conv_pe.v</code>):</h3>
<pre>
module conv_pe (
    input  wire clk,
    input  wire reset,
    input  wire load_weight,
    input  wire signed [15:0] weight_in,
    input  wire mac_en,
    input  wire clr_acc,
    input  wire signed [15:0] pixel_in,
    output reg  signed [15:0] out_acc,
    output reg  valid_out
);
    reg signed [15:0] weights [0:8];
    reg [3:0] tap_idx;
    wire signed [15:0] mac_result;
    wire signed [15:0] current_weight = weights[tap_idx];
    wire signed [15:0] acc_in = clr_acc ? 16'sd0 : out_acc;

    mac_q7_8 mac_inst (
        .in_val(pixel_in),
        .weight(current_weight),
        .acc_in(acc_in),
        .acc_out(mac_result)
    );

    always @(posedge clk) begin
        if (reset) begin
            tap_idx   &lt;= 0;
            out_acc   &lt;= 0;
            valid_out &lt;= 0;
        end else begin
            if (load_weight) begin
                weights[8] &lt;= weights[7];
                weights[7] &lt;= weights[6];
                weights[6] &lt;= weights[5];
                weights[5] &lt;= weights[4];
                weights[4] &lt;= weights[3];
                weights[3] &lt;= weights[2];
                weights[2] &lt;= weights[1];
                weights[1] &lt;= weights[0];
                weights[0] &lt;= weight_in;
            end
            if (mac_en) begin
                out_acc &lt;= mac_result;
                if (tap_idx == 8) begin
                    tap_idx   &lt;= 0;
                    valid_out &lt;= 1;
                end else begin
                    tap_idx   &lt;= tap_idx + 1;
                    valid_out &lt;= 0;
                end
            end else begin
                valid_out &lt;= 0;
            end
        end
    end
endmodule
</pre>
  </div>
</div>

<h2>8. Verification Results &amp; Hardware Resource Analysis</h2>

<h3>1. Directed Testbench Verification (<code>tb_conv_pe.v</code>):</h3>
<p>
The module was verified using the self-checking testbench <code>v2/verilog_src/tb_conv_pe.v</code> compiled with Icarus Verilog against Python golden values:
</p>
<ul>
  <li><strong>Test Case 1 (Interior 3 &times; 3 Window):</strong> Evaluated 9 non-zero pixel inputs (P<sub>1</sub> = [0.10, 0.20, ..., 0.90]) against signed kernel weights. Expected Q7.8 golden result: <code>104</code> (0.40625). RTL simulation output produced <code>104</code> (<code>PASS</code>).</li>
  <li><strong>Test Case 2 (Edge 3 &times; 3 Window with Zero-Padding):</strong> Evaluated boundary pixels with zero-padded corner and border positions (P<sub>2</sub> = [0, 0, 0, 0, 0.50, 0.60, 0, 0.80, 0.90]). Expected Q7.8 golden result: <code>19</code> (0.0742). RTL simulation output produced <code>19</code> (<code>PASS</code>).</li>
  <li><strong>Summary:</strong> Zero mismatches detected across directed test cases (<code>ALL TESTS PASSED.</code>).</li>
</ul>

<h3>2. Critical Path Analysis (Estimated Design Analysis, Unsynthesized):</h3>
<ul>
  <li><strong>Combinational Critical Path:</strong> <code>pixel_in</code> / <code>current_weight</code> &rarr; 16 &times; 16 Multiplier &rarr; <code>product[23:8]</code> Truncation Wiring &rarr; 16-bit Signed Adder &rarr; <code>out_acc</code> flip-flop setup time.</li>
  <li><strong>Timing Estimate:</strong> When targeted to typical FPGA fabrics (such as Xilinx Artix-7), the multiplier and adder map directly into a single DSP48E1 slice or equivalent LUT logic. The single-cycle combinational delay is estimated to support operating clock frequencies in the range of 100 to 150 MHz without requiring multi-stage pipeline registers.</li>
</ul>

<h3>3. Hardware Resource Trade-Off Arithmetic:</h3>
<p>
Compared to a fully unrolled parallel 2D convolution engine that instantiates 9 multipliers per channel:
</p>
<div class="math-block">
  Multiplier Reduction Ratio = (9 - 1) / 9 = 8 / 9 &approx; 88.89%
</div>
<p>
By time-multiplexing a single hardware multiplier across 9 clock cycles, the design reduces multiplier resource requirements by 88.89% per convolutional channel while maintaining deterministic 9-cycle throughput for real-time inference.
</p>

</body>
</html>
"""

temp_html = os.path.join(doc_dir, "module_specification.html")
pdf_out = os.path.join(doc_dir, "module_specification.pdf")

with open(temp_html, "w", encoding="utf-8") as f:
    f.write(html_content)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{temp_html.replace(chr(92), '/')}")
    page.pdf(
        path=pdf_out,
        format="A4",
        margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
        print_background=True
    )
    browser.close()

print(f"Generated PDF successfully: {os.path.exists(pdf_out)}, Size: {os.path.getsize(pdf_out)} bytes")
