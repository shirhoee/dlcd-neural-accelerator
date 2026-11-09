import React from 'react';
import styles from './ProblemStatementSection.module.css';
import { Target, Cpu, Clock, Layers, ShieldCheck } from 'lucide-react';

export const ProblemStatementSection: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.tag}>SECTION 1 &bull; SPECIFICATION</div>
        <h2 className={styles.title}>Problem Statement & Design Objectives</h2>
        <p className={styles.desc}>
          Edge AI platforms demand high-throughput, deterministic neural inference without the prohibitive silicon area, power dissipation, and latency overheads of 32-bit Floating-Point Units (FPUs).
        </p>
      </div>

      {/* Grid of Key Constraint Pillars */}
      <div className={styles.pillarsGrid}>
        <div className={styles.pillarCard}>
          <div className={styles.pillarIconBox}>
            <Target size={22} className={styles.pillarIcon} />
          </div>
          <h3 className={styles.pillarTitle}>Primary Objective</h3>
          <p className={styles.pillarDesc}>
            Synthesize an end-to-end, bit-exact CNN accelerator in Verilog-2001 (IEEE 1364-2001) targeting handwritten digit classification (MNIST) with zero software intervention.
          </p>
          <div className={styles.pillarBadge}>Target: &gt;98% Accuracy</div>
        </div>

        <div className={styles.pillarCard}>
          <div className={styles.pillarIconBox}>
            <Cpu size={22} className={styles.pillarIconCyan} />
          </div>
          <h3 className={styles.pillarTitle}>Q7.8 Arithmetic Invariant</h3>
          <p className={styles.pillarDesc}>
            All weights, activations, and multiply-accumulate operations use signed 16-bit fixed-point (1 sign, 7 integer, 8 fractional bits) with sequential per-step truncation matching RTL.
          </p>
          <div className={styles.pillarBadgeCyan}>Multiplier: 256.0 | Step Truncation</div>
        </div>

        <div className={styles.pillarCard}>
          <div className={styles.pillarIconBox}>
            <Clock size={22} className={styles.pillarIconEmerald} />
          </div>
          <h3 className={styles.pillarTitle}>Deterministic Latency</h3>
          <p className={styles.pillarDesc}>
            Fully pipelined 2D window generator and time-multiplexed systolic head guarantee deterministic execution bounded at exactly 9,116 clock cycles (91.16 µs @ 100 MHz).
          </p>
          <div className={styles.pillarBadgeEmerald}>Bounded: 9,116 Cycles / Frame</div>
        </div>

        <div className={styles.pillarCard}>
          <div className={styles.pillarIconBox}>
            <ShieldCheck size={22} className={styles.pillarIconAmber} />
          </div>
          <h3 className={styles.pillarTitle}>Silicon Budget & Zero-FPU</h3>
          <p className={styles.pillarDesc}>
            Eliminates all IEEE-754 hardware. Utilizes distributed line buffers, dual ping-pong RAMs (`ram_A`, `ram_B`), and 12 parallel systolic PEs with automatic zero-padding.
          </p>
          <div className={styles.pillarBadgeAmber}>Zero FPU Overhead</div>
        </div>
      </div>

      {/* Pipeline Flow Bar */}
      <div className={styles.pipelineFlow}>
        <div className={styles.flowHeader}>
          <Layers size={16} />
          <span>END-TO-END VERILOG HARDWARE DATAPATH</span>
        </div>
        <div className={styles.flowStages}>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 1</span>
            <strong className={styles.stageName}>Input Buffer</strong>
            <span className={styles.stageSpec}>20×20 px (Q7.8)</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 2</span>
            <strong className={styles.stageName}>Conv1 Array</strong>
            <span className={styles.stageSpec}>4 Channels (3×3)</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 3</span>
            <strong className={styles.stageName}>MaxPool 1</strong>
            <span className={styles.stageSpec}>4ch × 10×10 fmaps</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 4</span>
            <strong className={styles.stageName}>Conv2 Array</strong>
            <span className={styles.stageSpec}>8 Channels (3×3)</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 5</span>
            <strong className={styles.stageName}>MaxPool 2</strong>
            <span className={styles.stageSpec}>8ch × 5×5 (200 acts)</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={styles.stageNode}>
            <span className={styles.stageStep}>STEP 6</span>
            <strong className={styles.stageName}>Systolic Head</strong>
            <span className={styles.stageSpec}>200 &rarr; 64 &rarr; 32 &rarr; 10</span>
          </div>
          <div className={styles.stageArrow}>&rarr;</div>
          <div className={`${styles.stageNode} ${styles.stageFinal}`}>
            <span className={styles.stageStep}>OUTPUT</span>
            <strong className={styles.stageName}>Argmax Class</strong>
            <span className={styles.stageSpec}>Digit [0..9]</span>
          </div>
        </div>
      </div>
    </div>
  );
};
