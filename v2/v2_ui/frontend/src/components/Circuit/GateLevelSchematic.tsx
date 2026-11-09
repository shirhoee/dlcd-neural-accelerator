import React, { useState } from 'react';
import styles from './GateLevelSchematic.module.css';

interface GateLevelSchematicProps {
  moduleId: string;
}

export const GateLevelSchematic: React.FC<GateLevelSchematicProps> = ({ moduleId }) => {
  const [hoveredSignal, setHoveredSignal] = useState<string | null>(null);

  return (
    <div className={styles.schematicContainer}>
      <div className={styles.schematicToolbar}>
        <div className={styles.legend}>
          <span className={styles.legendItem}><span className={styles.gateDotCyan}></span> Logic Gates / Arithmetic</span>
          <span className={styles.legendItem}><span className={styles.gateDotPurple}></span> D-Flip-Flops / Registers</span>
          <span className={styles.legendItem}><span className={styles.gateDotAmber}></span> Multiplexers (MUX)</span>
          <span className={styles.legendItem}><span className={styles.gateDotEmerald}></span> Comparators / Trees</span>
        </div>
        {hoveredSignal && (
          <div className={styles.signalReadout}>
            Signal: <strong>{hoveredSignal}</strong>
          </div>
        )}
      </div>

      <div className={styles.svgViewport}>
        {/* Render Dedicated Gate Schematic Based on moduleId */}
        {moduleId === 'mac_q7_8' && (
          <svg className={styles.svg} viewBox="0 0 780 320" xmlns="http://www.w3.org/2000/svg">
            {/* Input Ports */}
            <rect x="20" y="50" width="80" height="34" rx="4" className={styles.portBox} />
            <text x="60" y="72" className={styles.portText}>A[15:0]</text>
            <path d="M100 67 L220 67" className={styles.busLine} onMouseEnter={() => setHoveredSignal('A[15:0] (Q7.8 Multiplicand)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="140" y="60" className={styles.busSlash}>/16</text>

            <rect x="20" y="110" width="80" height="34" rx="4" className={styles.portBox} />
            <text x="60" y="132" className={styles.portText}>B[15:0]</text>
            <path d="M100 127 L220 127" className={styles.busLine} onMouseEnter={() => setHoveredSignal('B[15:0] (Q7.8 Multiplier)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="140" y="120" className={styles.busSlash}>/16</text>

            {/* 16x16 Multiplier Block */}
            <rect x="220" y="45" width="110" height="105" rx="8" className={styles.gateBoxCyan} />
            <text x="275" y="85" className={styles.gateSymbol}>&times;</text>
            <text x="275" y="105" className={styles.gateSub}>16&times;16 Booth Mult</text>
            <text x="275" y="125" className={styles.gateSub2}>Signed 2's Compl</text>

            {/* Product Bus [31:0] */}
            <path d="M330 97 L410 97" className={styles.busLine} onMouseEnter={() => setHoveredSignal('Product[31:0] (Full 32-bit Product)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="360" y="90" className={styles.busSlash}>/32</text>

            {/* Truncator Shift Block [23:8] */}
            <rect x="410" y="65" width="80" height="65" rx="6" className={styles.shiftBox} />
            <text x="450" y="95" className={styles.gateTitle}>&gt;&gt; 8</text>
            <text x="450" y="115" className={styles.gateSub}>[23:8]</text>

            {/* Truncated Bus [15:0] */}
            <path d="M490 97 L540 97" className={styles.busLine} onMouseEnter={() => setHoveredSignal('product[23:8] (Q7.8 Truncated Product)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="510" y="90" className={styles.busSlash}>/16</text>

            {/* Carry-Lookahead Adder */}
            <polygon points="540,70 590,97 540,124 540,180 590,153 590,97" className={styles.adderPolygon} />
            <text x="560" y="132" className={styles.gateSymbol}>+</text>
            <text x="560" y="150" className={styles.gateSub}>CLA-16</text>

            {/* Accumulator Input C[15:0] */}
            <rect x="20" y="210" width="80" height="34" rx="4" className={styles.portBox} />
            <text x="60" y="232" className={styles.portText}>C[15:0]</text>
            <path d="M100 227 L540 227 L540 160" className={styles.busLine} onMouseEnter={() => setHoveredSignal('C[15:0] (Accumulation Input)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="240" y="220" className={styles.busSlash}>/16</text>

            {/* Adder Output [15:0] */}
            <path d="M590 125 L640 125" className={styles.busLine} onMouseEnter={() => setHoveredSignal('Sum[15:0]')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="610" y="118" className={styles.busSlash}>/16</text>

            {/* D-Flip-Flop Output Register */}
            <rect x="640" y="90" width="70" height="70" rx="6" className={styles.dffBox} />
            <text x="675" y="120" className={styles.gateTitle}>DFF-16</text>
            <text x="675" y="140" className={styles.gateSub}>Register</text>
            {/* Clock triangle */}
            <polyline points="640,145 650,150 640,155" className={styles.clockTriangle} />

            {/* Output Port */}
            <path d="M710 125 L760 125" className={styles.busLineCyan} onMouseEnter={() => setHoveredSignal('P[15:0] (Result Out)')} onMouseLeave={() => setHoveredSignal(null)} />
            <text x="730" y="118" className={styles.busSlash}>/16</text>
            <circle cx="760" cy="125" r="4" className={styles.outputPin} />
            <text x="765" y="129" className={styles.outputLabel}>P[15:0]</text>
          </svg>
        )}

        {/* conv_pe Gate Schematic */}
        {moduleId === 'conv_pe' && (
          <svg className={styles.svg} viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg">
            {/* 3x3 Weight Register Bank */}
            <rect x="30" y="30" width="130" height="150" rx="8" className={styles.regBankBox} />
            <text x="95" y="55" className={styles.gateTitle}>WEIGHT REG BANK</text>
            <text x="95" y="75" className={styles.gateSub}>9 &times; 16-bit DFFs</text>
            <rect x="45" y="90" width="100" height="20" rx="3" className={styles.subReg} />
            <text x="95" y="104" className={styles.subRegText}>W0 .. W2 (Row 0)</text>
            <rect x="45" y="115" width="100" height="20" rx="3" className={styles.subReg} />
            <text x="95" y="129" className={styles.subRegText}>W3 .. W5 (Row 1)</text>
            <rect x="45" y="140" width="100" height="20" rx="3" className={styles.subReg} />
            <text x="95" y="154" className={styles.subRegText}>W6 .. W8 (Row 2)</text>

            {/* MUX 9:1 for Weights */}
            <polygon points="200,60 230,80 230,130 200,150" className={styles.muxBox} />
            <text x="215" y="110" className={styles.muxText}>MUX 9:1</text>
            <path d="M160 105 L200 105" className={styles.busLine} />

            {/* 9-Element Window Data Input Port */}
            <rect x="30" y="220" width="130" height="40" rx="6" className={styles.portBox} />
            <text x="95" y="245" className={styles.portText}>win_data[143:0]</text>

            {/* MUX 9:1 for Window Pixels */}
            <polygon points="200,200 230,220 230,270 200,290" className={styles.muxBox} />
            <text x="215" y="250" className={styles.muxText}>MUX 9:1</text>
            <path d="M160 240 L200 240" className={styles.busLine} />

            {/* 4-Bit State Counter */}
            <rect x="190" y="155" width="50" height="35" rx="4" className={styles.counterBox} />
            <text x="215" y="172" className={styles.counterTitle}>CNT 0..8</text>
            <text x="215" y="184" className={styles.counterSub}>4-bit</text>
            {/* Control lines into MUX select */}
            <path d="M215 155 L215 140" className={styles.controlLine} />
            <path d="M215 190 L215 210" className={styles.controlLine} />

            {/* mac_q7_8 Unit */}
            <rect x="300" y="120" width="130" height="110" rx="8" className={styles.gateBoxCyan} />
            <text x="365" y="155" className={styles.gateTitle}>mac_q7_8</text>
            <text x="365" y="175" className={styles.gateSub}>W[k] &times; Win[k] + Acc</text>
            <text x="365" y="195" className={styles.gateSub2}>Per-step [23:8]</text>

            <path d="M230 105 L300 145" className={styles.busLine} />
            <path d="M230 245 L300 185" className={styles.busLine} />

            {/* Accumulator Loop Register */}
            <rect x="480" y="140" width="90" height="70" rx="6" className={styles.dffBox} />
            <text x="525" y="170" className={styles.gateTitle}>ACCUMULATOR</text>
            <text x="525" y="190" className={styles.gateSub}>16-bit DFF</text>
            <polyline points="480,195 490,200 480,205" className={styles.clockTriangle} />

            <path d="M430 175 L480 175" className={styles.busLine} />
            {/* Feedback loop back into MAC */}
            <path d="M570 175 L600 175 L600 270 L365 270 L365 230" className={styles.feedbackLine} />
            <text x="470" y="285" className={styles.busSlash}>Feedback [15:0]</text>

            {/* Comparator count == 8 & Valid Gate */}
            <rect x="480" y="45" width="85" height="45" rx="6" className={styles.comparatorBox} />
            <text x="522" y="68" className={styles.gateTitle}>COMP == 8</text>
            <text x="522" y="82" className={styles.gateSub}>Cycle Match</text>
            <path d="M240 172 L480 68" className={styles.controlLine} />

            {/* Output Registers & Strobe */}
            <rect x="660" y="145" width="110" height="60" rx="6" className={styles.portBox} />
            <text x="715" y="172" className={styles.portText}>out_data[15:0]</text>
            <text x="715" y="190" className={styles.gateSub2}>Valid Pixel</text>
            <path d="M570 175 L660 175" className={styles.busLineCyan} />

            <path d="M565 68 L660 68" className={styles.controlLineGreen} />
            <circle cx="660" cy="68" r="4" className={styles.outputPin} />
            <text x="670" y="72" className={styles.outputLabel}>out_valid</text>
          </svg>
        )}

        {/* window_gen Gate Schematic */}
        {moduleId === 'window_gen' && (
          <svg className={styles.svg} viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg">
            {/* Input Pixel Stream */}
            <rect x="20" y="130" width="80" height="40" rx="4" className={styles.portBox} />
            <text x="60" y="155" className={styles.portText}>in_data[15:0]</text>
            <path d="M100 150 L160 150" className={styles.busLine} />

            {/* Line Buffer 0 (20 words FIFO) */}
            <rect x="160" y="40" width="130" height="60" rx="6" className={styles.lineBufBox} />
            <text x="225" y="68" className={styles.gateTitle}>LINE BUFFER 0</text>
            <text x="225" y="85" className={styles.gateSub}>20 &times; 16-bit SRAM FIFO</text>

            {/* Line Buffer 1 (20 words FIFO) */}
            <rect x="160" y="120" width="130" height="60" rx="6" className={styles.lineBufBox} />
            <text x="225" y="148" className={styles.gateTitle}>LINE BUFFER 1</text>
            <text x="225" y="165" className={styles.gateSub}>20 &times; 16-bit SRAM FIFO</text>

            {/* Tap Connections */}
            <path d="M100 150 L160 70" className={styles.busLine} />
            <path d="M290 70 L340 70" className={styles.busLine} />
            <path d="M290 150 L340 150" className={styles.busLine} />

            {/* 3x3 Tap Register Grid (9 DFFs) */}
            <g transform="translate(340, 30)">
              <rect x="0" y="0" width="220" height="230" rx="8" className={styles.tapGridBox} />
              <text x="110" y="25" className={styles.gateTitle}>3&times;3 TAP REGISTERS (9 &times; DFF-16)</text>

              {/* Row 0: w00, w01, w02 */}
              <rect x="15" y="40" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="42" y="67" className={styles.dffMiniText}>w00</text>
              <rect x="82" y="40" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="109" y="67" className={styles.dffMiniText}>w01</text>
              <rect x="150" y="40" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="177" y="67" className={styles.dffMiniText}>w02</text>

              {/* Row 1: w10, w11, w12 */}
              <rect x="15" y="100" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="42" y="127" className={styles.dffMiniText}>w10</text>
              <rect x="82" y="100" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="109" y="127" className={styles.dffMiniText}>w11</text>
              <rect x="150" y="100" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="177" y="127" className={styles.dffMiniText}>w12</text>

              {/* Row 2: w20, w21, w22 */}
              <rect x="15" y="160" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="42" y="187" className={styles.dffMiniText}>w20</text>
              <rect x="82" y="160" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="109" y="187" className={styles.dffMiniText}>w21</text>
              <rect x="150" y="160" width="55" height="45" rx="4" className={styles.dffMiniBox} />
              <text x="177" y="187" className={styles.dffMiniText}>w22</text>
            </g>

            {/* Zero-Padding Boundary Logic */}
            <rect x="590" y="60" width="80" height="50" rx="6" className={styles.gateBoxCyan} />
            <text x="630" y="85" className={styles.gateTitle}>PAD LOGIC</text>
            <text x="630" y="100" className={styles.gateSub}>Border AND/MUX</text>

            <path d="M560 145 L700 145" className={styles.busLineCyan} />
            <rect x="700" y="125" width="85" height="40" rx="4" className={styles.portBox} />
            <text x="742" y="150" className={styles.portText}>win[143:0]</text>
          </svg>
        )}

        {/* maxpool_pe Gate Schematic */}
        {moduleId === 'maxpool_pe' && (
          <svg className={styles.svg} viewBox="0 0 780 320" xmlns="http://www.w3.org/2000/svg">
            {/* 4 Inputs: in0, in1, in2, in3 */}
            <rect x="20" y="30" width="70" height="30" rx="4" className={styles.portBox} />
            <text x="55" y="50" className={styles.portText}>in0[15:0]</text>
            <rect x="20" y="75" width="70" height="30" rx="4" className={styles.portBox} />
            <text x="55" y="95" className={styles.portText}>in1[15:0]</text>
            <rect x="20" y="160" width="70" height="30" rx="4" className={styles.portBox} />
            <text x="55" y="180" className={styles.portText}>in2[15:0]</text>
            <rect x="20" y="205" width="70" height="30" rx="4" className={styles.portBox} />
            <text x="55" y="225" className={styles.portText}>in3[15:0]</text>

            {/* Stage 1: Comparator 1 & MUX 1 (Top Pair) */}
            <rect x="150" y="35" width="80" height="45" rx="6" className={styles.comparatorBox} />
            <text x="190" y="60" className={styles.gateTitle}>CMP 1</text>
            <text x="190" y="72" className={styles.gateSub}>in0 &gt; in1 ?</text>
            <polygon points="260,35 285,45 285,85 260,95" className={styles.muxBox} />
            <text x="272" y="70" className={styles.muxText}>MUX</text>

            <path d="M90 45 L150 45" className={styles.busLine} />
            <path d="M90 90 L150 90" className={styles.busLine} />
            <path d="M90 45 L260 45" className={styles.busLine} />
            <path d="M90 90 L260 85" className={styles.busLine} />
            <path d="M230 57 L272 45" className={styles.controlLine} />

            {/* Stage 1: Comparator 2 & MUX 2 (Bottom Pair) */}
            <rect x="150" y="165" width="80" height="45" rx="6" className={styles.comparatorBox} />
            <text x="190" y="190" className={styles.gateTitle}>CMP 2</text>
            <text x="190" y="202" className={styles.gateSub}>in2 &gt; in3 ?</text>
            <polygon points="260,165 285,175 285,215 260,225" className={styles.muxBox} />
            <text x="272" y="200" className={styles.muxText}>MUX</text>

            <path d="M90 175 L150 175" className={styles.busLine} />
            <path d="M90 220 L150 220" className={styles.busLine} />
            <path d="M90 175 L260 175" className={styles.busLine} />
            <path d="M90 220 L260 215" className={styles.busLine} />
            <path d="M230 187 L272 175" className={styles.controlLine} />

            {/* Stage 2: Final Comparator 3 & MUX 3 */}
            <rect x="350" y="100" width="80" height="45" rx="6" className={styles.comparatorBox} />
            <text x="390" y="125" className={styles.gateTitle}>CMP 3</text>
            <text x="390" y="137" className={styles.gateSub}>M1 &gt; M2 ?</text>

            <polygon points="460,95 485,105 485,145 460,155" className={styles.muxBox} />
            <text x="472" y="130" className={styles.muxText}>MUX</text>

            <path d="M285 65 L460 105" className={styles.busLine} />
            <path d="M285 195 L460 145" className={styles.busLine} />
            <path d="M285 65 L350 110" className={styles.busLine} />
            <path d="M285 195 L350 135" className={styles.busLine} />
            <path d="M430 122 L472 105" className={styles.controlLine} />

            {/* Stage 3: Fused ReLU Gate (Sign-bit Inverter + AND Gate) */}
            <g transform="translate(530, 95)">
              <rect x="0" y="0" width="130" height="60" rx="8" className={styles.gateBoxCyan} />
              <text x="65" y="25" className={styles.gateTitle}>FUSED ReLU GATE</text>
              <text x="65" y="42" className={styles.gateSub}>sign ? 0 : max_val</text>
              <text x="65" y="54" className={styles.gateSub2}>Monotonic Zero-Distort</text>
            </g>

            <path d="M485 125 L530 125" className={styles.busLine} />
            <path d="M660 125 L720 125" className={styles.busLineCyan} />

            <circle cx="720" cy="125" r="4" className={styles.outputPin} />
            <text x="730" y="129" className={styles.outputLabel}>out[15:0]</text>
          </svg>
        )}

        {/* argmax Gate Schematic */}
        {moduleId === 'argmax' && (
          <svg className={styles.svg} viewBox="0 0 780 320" xmlns="http://www.w3.org/2000/svg">
            <text x="390" y="25" className={styles.gateTitle}>10-INPUT PIPELINED TOURNAMENT COMPARATOR TREE</text>

            {/* Level 1: 5 Comparators */}
            <g transform="translate(40, 45)">
              <rect x="0" y="0" width="100" height="38" rx="4" className={styles.comparatorBox} />
              <text x="50" y="22" className={styles.subRegText}>CMP(0, 1)</text>
              <rect x="0" y="48" width="100" height="38" rx="4" className={styles.comparatorBox} />
              <text x="50" y="70" className={styles.subRegText}>CMP(2, 3)</text>
              <rect x="0" y="96" width="100" height="38" rx="4" className={styles.comparatorBox} />
              <text x="50" y="118" className={styles.subRegText}>CMP(4, 5)</text>
              <rect x="0" y="144" width="100" height="38" rx="4" className={styles.comparatorBox} />
              <text x="50" y="166" className={styles.subRegText}>CMP(6, 7)</text>
              <rect x="0" y="192" width="100" height="38" rx="4" className={styles.comparatorBox} />
              <text x="50" y="214" className={styles.subRegText}>CMP(8, 9)</text>
            </g>

            {/* Level 2: 3 Comparators */}
            <g transform="translate(220, 70)">
              <rect x="0" y="0" width="110" height="42" rx="4" className={styles.comparatorBox} />
              <text x="55" y="24" className={styles.subRegText}>CMP(W01, W23)</text>
              <rect x="0" y="60" width="110" height="42" rx="4" className={styles.comparatorBox} />
              <text x="55" y="84" className={styles.subRegText}>CMP(W45, W67)</text>
              <rect x="0" y="120" width="110" height="42" rx="4" className={styles.subReg} />
              <text x="55" y="144" className={styles.subRegText}>BYPASS W89</text>
            </g>

            {/* Level 3: 2 Comparators */}
            <g transform="translate(400, 95)">
              <rect x="0" y="0" width="110" height="42" rx="4" className={styles.comparatorBox} />
              <text x="55" y="24" className={styles.subRegText}>CMP Semi 1</text>
              <rect x="0" y="60" width="110" height="42" rx="4" className={styles.comparatorBox} />
              <text x="55" y="84" className={styles.subRegText}>CMP Semi 2</text>
            </g>

            {/* Level 4: Final Comparator & Priority Index Latch */}
            <g transform="translate(570, 115)">
              <rect x="0" y="0" width="130" height="65" rx="8" className={styles.gateBoxCyan} />
              <text x="65" y="28" className={styles.gateTitle}>FINAL CMP &amp; INDEX</text>
              <text x="65" y="45" className={styles.gateSub}>4-bit Class Latch</text>
            </g>

            {/* Interconnecting Lines */}
            <path d="M140 64 L220 91" className={styles.busLine} />
            <path d="M140 115 L220 91" className={styles.busLine} />
            <path d="M330 91 L400 116" className={styles.busLine} />
            <path d="M330 151 L400 116" className={styles.busLine} />
            <path d="M510 116 L570 147" className={styles.busLineCyan} />

            <path d="M700 147 L750 147" className={styles.busLineCyan} />
            <circle cx="750" cy="147" r="4" className={styles.outputPin} />
            <text x="755" y="151" className={styles.outputLabel}>digit_out[3:0]</text>
          </svg>
        )}

        {/* Fallback for other modules: systolic_pe, systolic_array, conv1_array, conv2_array, mlp_head, v2_top */}
        {!['mac_q7_8', 'conv_pe', 'window_gen', 'maxpool_pe', 'argmax'].includes(moduleId) && (
          <svg className={styles.svg} viewBox="0 0 780 320" xmlns="http://www.w3.org/2000/svg">
            <rect x="40" y="40" width="700" height="240" rx="12" className={styles.macroBox} />
            <text x="390" y="75" className={styles.gateTitle}>
              {moduleId.toUpperCase()} &bull; HARDWARE GATE-LEVEL SCHEMATIC ARCHITECTURE
            </text>

            {/* Block Representation */}
            <g transform="translate(80, 100)">
              <rect x="0" y="0" width="160" height="130" rx="8" className={styles.gateBoxCyan} />
              <text x="80" y="40" className={styles.gateTitle}>INPUT REGISTERS</text>
              <text x="80" y="65" className={styles.gateSub}>Synchronous Flip-Flops</text>
              <text x="80" y="85" className={styles.gateSub2}>CLK + RESET_N</text>
            </g>

            <path d="M240 165 L320 165" className={styles.busLineCyan} />
            <text x="270" y="155" className={styles.busSlash}>Data Bus</text>

            <g transform="translate(320, 100)">
              <rect x="0" y="0" width="180" height="130" rx="8" className={styles.dffBox} />
              <text x="90" y="40" className={styles.gateTitle}>COMPUTATION CORE</text>
              <text x="90" y="65" className={styles.gateSub}>Q7.8 Fixed-Point ALU</text>
              <text x="90" y="85" className={styles.gateSub2}>Parallel MAC Arrays</text>
            </g>

            <path d="M500 165 L580 165" className={styles.busLineCyan} />
            <text x="530" y="155" className={styles.busSlash}>Results</text>

            <g transform="translate(580, 100)">
              <rect x="0" y="0" width="140" height="130" rx="8" className={styles.comparatorBox} />
              <text x="70" y="40" className={styles.gateTitle}>OUTPUT LATCH</text>
              <text x="70" y="65" className={styles.gateSub}>Valid Strobe Router</text>
              <text x="70" y="85" className={styles.gateSub2}>Pipelined Flow</text>
            </g>
          </svg>
        )}
      </div>
    </div>
  );
};
