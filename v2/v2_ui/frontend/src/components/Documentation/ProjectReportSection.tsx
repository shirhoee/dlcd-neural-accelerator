import React from 'react';
import styles from './ProjectReportSection.module.css';
import { Printer, CheckCircle2, Cpu, ShieldCheck } from 'lucide-react';

export const ProjectReportSection: React.FC = () => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className={styles.reportContainer}>
      {/* Action Bar */}
      <div className={styles.actionBar}>
        <div className={styles.docBadge}>
          <span>PES UNIVERSITY &bull; UE25CS251A LAB REPORT SPECIFICATION</span>
        </div>
        <button className={styles.printBtn} onClick={handlePrint} title="Print or Save as PDF">
          <Printer size={15} />
          <span>Print / Save Report (PDF)</span>
        </button>
      </div>

      {/* Report Document Sheet */}
      <article className={styles.reportSheet}>
        {/* Title Header */}
        <header className={styles.sheetHeader}>
          <div className={styles.univName}>PES UNIVERSITY</div>
          <div className={styles.campusName}>RING ROAD CAMPUS, 100 FEET RING ROAD, BSK III STAGE, BENGALURU – 560085</div>
          <div className={styles.deptName}>DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING</div>
          <div className={styles.courseTitle}>UE25CS251A DIGITAL LOGIC AND COMPUTER DESIGN LABORATORY</div>
          <div className={styles.subTitle}>END SEMESTER ASSESSMENT (ESA) &bull; MINI PROJECT REPORT</div>

          <hr className={styles.sheetDivider} />

          <h1 className={styles.reportTitle}>
            DESIGN AND IMPLEMENTATION OF A Q7.8 FIXED-POINT CONVOLUTIONAL NEURAL NETWORK HARDWARE ACCELERATOR
          </h1>

          {/* Team Roster Grid */}
          <div className={styles.rosterBox}>
            <div className={styles.rosterHeading}>SUBMITTED BY:</div>
            <div className={styles.rosterGrid}>
              <div className={styles.rosterItem}>
                <strong>Shreyansh Raj</strong>
                <span>PES2UG25CS516</span>
              </div>
              <div className={styles.rosterItem}>
                <strong>Sarthak Bhowmik</strong>
                <span>PES2UG25CS493</span>
              </div>
              <div className={styles.rosterItem}>
                <strong>Shaurya Singh</strong>
                <span>PES2UG25CS508</span>
              </div>
              <div className={styles.rosterItem}>
                <strong>Shreya Anand</strong>
                <span>PES2UG25CS515</span>
              </div>
            </div>
          </div>
        </header>

        {/* Section 1: Abstract */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>1. ABSTRACT</h2>
          <p>
            Edge machine learning demands high-throughput, low-latency, and deterministic classification without the silicon area and power consumption of 32-bit Floating-Point Units (FPUs). In this work, we design, synthesize, and verify an end-to-end, bit-exact Convolutional Neural Network (CNN) hardware accelerator implemented in Verilog-2001 (IEEE 1364-2001). 
          </p>
          <p>
            The accelerator operates entirely within a signed 16-bit Q7.8 fixed-point arithmetic domain (1 sign bit, 7 integer bits, 8 fractional bits; scale factor of 256.0). The datapath incorporates 2D spatial line buffers for continuous streaming 3×3 convolutions, fused MaxPool+ReLU logic eliminating 75% of non-linear activation operations, and a time-multiplexed 16×16 systolic array core with dual ping-pong SRAMs (<code>ram_A</code> and <code>ram_B</code>) computing the dense classification head (200 &rarr; 64 &rarr; 32 &rarr; 10). 
          </p>
          <p>
            Evaluated on the full 10,000-image MNIST test dataset, the accelerator achieves <strong>98.83% accuracy</strong> (9,883 / 10,000 correct) with an invariant, deterministic latency of exactly <strong>9,116 clock cycles</strong> (91.16 µs at 100 MHz). Compared to the Version 1 baseline Multi-Layer Perceptron (93.06%), the proposed Version 2 architecture achieves a <strong>+5.77% accuracy gain</strong> while reusing the 256-multiplier systolic array, incurring zero multiplier silicon overhead.
          </p>
        </section>

        {/* Section 2: Problem Statement & Constraints */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>2. PROBLEM STATEMENT &amp; SYSTEM SPECIFICATIONS</h2>
          <p>
            Deploying machine learning models onto embedded FPGAs or ASICs poses severe hardware challenges:
          </p>
          <ul className={styles.bulletsList}>
            <li>
              <strong>Elimination of Floating-Point Units:</strong> Traditional 32-bit IEEE-754 FPUs require thousands of logic gates per operator, creating unacceptable area, routing, and power penalties.
            </li>
            <li>
              <strong>Quantization Distortion &amp; Overflow:</strong> Naïve post-training quantization can cause catastrophic accuracy collapse or overflow during wide sequential accumulations.
            </li>
            <li>
              <strong>Spatial Resolution Preservation:</strong> Aggressive downsampling (e.g., from 28×28 down to 10×10 as in Version 1) causes topological stroke erosion, limiting accuracy to ~93%.
            </li>
          </ul>

          <h3 className={styles.subSubHeading}>Hardware Specifications Summary Table</h3>
          <div className={styles.tableWrapper}>
            <table className={styles.specTable}>
              <thead>
                <tr>
                  <th>Parameter / Subsystem</th>
                  <th>Version 1.0 (Baseline MLP)</th>
                  <th>Version 2.0 (Proposed CNN Accelerator)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Model Architecture</strong></td>
                  <td>100 &rarr; 16 &rarr; 6 &rarr; 10 Fully-Connected</td>
                  <td>Conv1(4ch) &rarr; Pool1 &rarr; Conv2(8ch) &rarr; Pool2 &rarr; Systolic(200&rarr;64&rarr;32&rarr;10)</td>
                </tr>
                <tr>
                  <td><strong>Input Spatial Resolution</strong></td>
                  <td>10×10 (100 pixels)</td>
                  <td>20×20 (400 pixels; 4× spatial information)</td>
                </tr>
                <tr>
                  <td><strong>Arithmetic Format</strong></td>
                  <td>Signed 16-bit Q7.8 Fixed-Point</td>
                  <td>Signed 16-bit Q7.8 with Per-Step Truncation <code>[23:8]</code></td>
                </tr>
                <tr>
                  <td><strong>Hardware Multipliers</strong></td>
                  <td>256 (16×16 Systolic Mesh)</td>
                  <td>256 (Reused via Time-Multiplexing with Dual Ping-Pong RAMs)</td>
                </tr>
                <tr>
                  <td><strong>Execution Latency</strong></td>
                  <td>6,139 clock cycles (61.39 µs @ 100 MHz)</td>
                  <td>9,116 clock cycles (91.16 µs @ 100 MHz)</td>
                </tr>
                <tr>
                  <td><strong>Full Testset Accuracy</strong></td>
                  <td>93.06%</td>
                  <td><strong>98.83% (+5.77% boost)</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 3: Hardware Architecture & Gate-Level RTL */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>3. HARDWARE DATAPATH &amp; GATE-LEVEL CIRCUITS</h2>
          <p>
            The accelerator datapath comprises six pipelined functional stages operating synchronously:
          </p>
          <ol className={styles.numberedList}>
            <li>
              <strong>2D Spatial Window Generator (<code>window_gen.v</code>):</strong> Uses two 20-word SRAM FIFO line buffers and a 3×3 matrix of 9 D-Flip-Flops to stream 9 spatial pixels simultaneously without redundant memory fetches.
            </li>
            <li>
              <strong>Conv1 Array (<code>conv1_array.v</code>):</strong> Houses 4 parallel <code>conv_pe</code> processing elements, each equipped with dedicated 3×3 weight registers and a sequential Q7.8 MAC accumulator.
            </li>
            <li>
              <strong>Fused MaxPool1 &amp; ReLU (<code>maxpool_array.v</code>):</strong> Implements a 2×2 tournament comparator tree (three 16-bit signed comparators) followed by an inverter-and-mask ReLU gate, downsampling to 4 channels of 10×10 feature maps.
            </li>
            <li>
              <strong>Conv2 &amp; MaxPool2 Subsystem (<code>conv2_array.v</code>):</strong> Broadcasts 4 channels across 8 filter groups with multi-channel adder trees, followed by 2×2 pooling into 8 channels of 5×5 feature maps (200 activations).
            </li>
            <li>
              <strong>Time-Multiplexed Systolic Head (<code>mlp_head.v</code>):</strong> Manages dual ping-pong RAMs (<code>ram_A</code> and <code>ram_B</code>) to execute Layer 1 (200&rarr;64 in 4,800 cycles), Layer 2 (64&rarr;32 in 1,824 cycles), and Layer 3 (32&rarr;10 in 1,050 cycles).
            </li>
            <li>
              <strong>Tournament Argmax Classifier (<code>argmax.v</code>):</strong> A pipelined 4-level tournament comparator tree that identifies the maximum logit and latches the 4-bit winning digit index <code>[0..9]</code> in a single cycle.
            </li>
          </ol>
        </section>

        {/* Section 4: State Machine Control */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>4. FINITE STATE MACHINE (FSM) SPECIFICATIONS</h2>
          <p>
            Control across all processing elements is governed by synchronous Mealy and Moore state machines:
          </p>
          <div className={styles.fsmCard}>
            <div className={styles.fsmHeader}>
              <Cpu size={16} />
              <strong>conv_pe 4-State Cycle Controller</strong>
            </div>
            <p>
              States: <code>IDLE</code> (awaits <code>in_valid</code> strobe) &rarr; <code>ACCUM</code> (cycles counter 0..8, executing MAC operations on 9 spatial taps) &rarr; <code>ROUND</code> (applies Q7.8 fixed-point rounding and saturation guard) &rarr; <code>DONE</code> (asserts <code>out_valid</code>, resets accumulator to zero).
            </p>
          </div>
          <div className={styles.fsmCard}>
            <div className={styles.fsmHeader}>
              <ShieldCheck size={16} />
              <strong>mlp_head 8-State Layer Sequencer</strong>
            </div>
            <p>
              States: <code>IDLE</code> &rarr; <code>FLATTEN_IN</code> &rarr; <code>L1_RUN</code> (computes 200&rarr;64, writes <code>ram_B</code>) &rarr; <code>L1_DRAIN</code> &rarr; <code>L2_RUN</code> (computes 64&rarr;32, writes <code>ram_A</code>) &rarr; <code>L2_DRAIN</code> &rarr; <code>L3_RUN</code> (computes 32&rarr;10, writes logits) &rarr; <code>HEAD_DONE</code>.
            </p>
          </div>
        </section>

        {/* Section 5: Verification & Results */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>5. TESTBENCH &amp; HARDWARE VERIFICATION RESULTS</h2>
          <p>
            All hardware modules were verified through Icarus Verilog (IEEE 1364-2001) using strict <code>`default_nettype none</code> discipline:
          </p>
          <div className={styles.verifySummaryGrid}>
            <div className={styles.verifyItem}>
              <CheckCircle2 size={20} className={styles.checkIcon} />
              <div>
                <strong>13/13 Unit Testbenches Passing:</strong>
                <span>All line buffers, conv arrays, systolic arrays, and top-level modules pass with 0 bit errors.</span>
              </div>
            </div>
            <div className={styles.verifyItem}>
              <CheckCircle2 size={20} className={styles.checkIcon} />
              <div>
                <strong>Bit-Exact Golden Alignment:</strong>
                <span>Zero bit discrepancies between Python Q7.8 integer emulator and Verilog RTL across all layers.</span>
              </div>
            </div>
            <div className={styles.verifyItem}>
              <CheckCircle2 size={20} className={styles.checkIcon} />
              <div>
                <strong>Full 10,000-Image Regression:</strong>
                <span>98.83% test accuracy (9,883 / 10,000 correct) on unseen MNIST test vectors.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 6: References */}
        <section className={styles.reportSection}>
          <h2 className={styles.secHeading}>6. REFERENCES &amp; BIBLIOGRAPHY</h2>
          <ol className={styles.refsList}>
            <li>
              Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, "Gradient-based learning applied to document recognition," <em>Proceedings of the IEEE</em>, vol. 86, no. 11, pp. 2278-2324, Nov. 1998.
            </li>
            <li>
              H. T. Kung, "Why systolic architectures?," <em>IEEE Computer</em>, vol. 15, no. 1, pp. 37-46, Jan. 1982.
            </li>
            <li>
              N. P. Jouppi et al., "In-datacenter performance analysis of a tensor processing unit," in <em>Proc. ACM/IEEE 44th Annual International Symposium on Computer Architecture (ISCA)</em>, 2017, pp. 1-12.
            </li>
            <li>
              IEEE Computer Society, "IEEE Standard for Verilog Hardware Description Language," <em>IEEE Std 1364-2001</em>, pp. 1-792, 2001.
            </li>
            <li>
              Department of Computer Science &amp; Engineering, PES University, "UE25CS251A Digital Logic and Computer Design Laboratory Course Manual," Ring Road Campus, Bengaluru, 2026.
            </li>
          </ol>
        </section>
      </article>
    </div>
  );
};
