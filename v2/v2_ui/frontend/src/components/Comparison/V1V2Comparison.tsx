import React, { useState } from 'react';
import styles from './V1V2Comparison.module.css';
import { Cpu, Maximize2, Zap } from 'lucide-react';

export const V1V2Comparison: React.FC = () => {
  const [selectedAspect, setSelectedAspect] = useState<'accuracy' | 'hardware' | 'math'>('accuracy');

  return (
    <section className={styles.section} id="comparison">
      <div className={styles.sectionHeader}>
        <div>
          <div className={styles.categoryBadge}>SECTION 4 • LITERATURE SURVEY & DESIGN EVOLUTION</div>
          <h2 className={styles.sectionTitle}>Architectural Comparison: Version 1 vs Version 2</h2>
          <p className={styles.sectionDesc}>
            Evolution from the baseline Multi-Layer Perceptron (V1) to the 6-layer Convolutional Neural Accelerator (V2).
            Demonstrating how reusing the 16×16 systolic array achieved <span className={styles.highlight}>+5.77% higher accuracy</span> with zero multiplier overhead.
          </p>
        </div>

        {/* Tab Controls */}
        <div className={styles.aspectTabs}>
          <button
            className={`${styles.tabBtn} ${selectedAspect === 'accuracy' ? styles.activeTab : ''}`}
            onClick={() => setSelectedAspect('accuracy')}
          >
            Accuracy & Generalization
          </button>
          <button
            className={`${styles.tabBtn} ${selectedAspect === 'hardware' ? styles.activeTab : ''}`}
            onClick={() => setSelectedAspect('hardware')}
          >
            Hardware & Silicon Area
          </button>
          <button
            className={`${styles.tabBtn} ${selectedAspect === 'math' ? styles.activeTab : ''}`}
            onClick={() => setSelectedAspect('math')}
          >
            Arithmetic & Dataflow
          </button>
        </div>
      </div>

      {/* Side-by-Side Architectural Scorecard */}
      <div className={styles.scorecardGrid}>
        {/* Version 1 Card */}
        <div className={styles.versionCard}>
          <div className={styles.cardHeader}>
            <span className={styles.versionTag}>V1 BASELINE</span>
            <h3 className={styles.versionTitle}>Multi-Layer Perceptron (MLP)</h3>
            <p className={styles.cardSub}>10×10 Input → 16 → 6 → 10 (Systolic Feedforward)</p>
          </div>

          <div className={styles.metricsList}>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>MNIST Testset Accuracy</span>
              <span className={styles.metricValV1}>93.06%</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Input Resolution</span>
              <span className={styles.metricVal}>10×10 (100 pixels)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Multiplier Allocation</span>
              <span className={styles.metricVal}>256 Multipliers (16×16 mesh)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Inference Latency</span>
              <span className={styles.metricVal}>6,139 clock cycles (61.4 µs)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Spatial Feature Extraction</span>
              <span className={styles.metricValDim}>None (Flattened global vector)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Shift / Stroke Tolerance</span>
              <span className={styles.metricValDim}>Low (Fails on 1-pixel shift)</span>
            </div>
          </div>
        </div>

        {/* Version 2 Card */}
        <div className={`${styles.versionCard} ${styles.v2HighlightCard}`}>
          <div className={styles.cardHeader}>
            <div className={styles.v2HeaderTop}>
              <span className={`${styles.versionTag} ${styles.v2Tag}`}>V2 ACCELERATOR (SUBMITTED)</span>
              <span className={styles.gainBadge}>+5.77% ACCURACY BOOST</span>
            </div>
            <h3 className={styles.versionTitle}>CNN + Time-Multiplexed Systolic Head</h3>
            <p className={styles.cardSub}>20×20 Input → Conv1 → MP1 → Conv2 → MP2 → 200→64→32→10</p>
          </div>

          <div className={styles.metricsList}>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>MNIST Testset Accuracy</span>
              <span className={styles.metricValV2}>98.83%</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Input Resolution</span>
              <span className={styles.metricVal}>20×20 (400 pixels)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Multiplier Allocation</span>
              <span className={styles.metricValV2}>256 Reused MACs (Zero added area)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Inference Latency</span>
              <span className={styles.metricVal}>9,116 clock cycles (91.2 µs)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Spatial Feature Extraction</span>
              <span className={styles.metricValV2}>High (3×3 receptive fields, 2D filters)</span>
            </div>
            <div className={styles.metricRow}>
              <span className={styles.metricLabel}>Shift / Stroke Tolerance</span>
              <span className={styles.metricValV2}>Very High (Spatial pooling invariance)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Engineering Insights & Deep Dives */}
      <div className={styles.insightsGrid}>
        <div className={styles.insightCard}>
          <div className={styles.insightIcon}><Maximize2 size={20} /></div>
          <h4 className={styles.insightTitle}>1. The Downsampling Bottleneck (10×10 vs 20×20)</h4>
          <p className={styles.insightDesc}>
            Downsampling an MNIST digit directly from 28×28 to 10×10 causes catastrophic morphological erosion. Critical loops (in 8s and 0s) and thin serif strokes collapse into dense blobs, placing a strict theoretical ceiling of ~93% on any MLP. Increasing resolution to 20×20 preserves topology.
          </p>
        </div>

        <div className={styles.insightCard}>
          <div className={styles.insightIcon}><Cpu size={20} /></div>
          <h4 className={styles.insightTitle}>2. Time-Multiplexing the 16×16 Systolic Array</h4>
          <p className={styles.insightDesc}>
            A naïve unrolled implementation of the 200→64→32→10 dense head requires 15,168 parallel hardware multipliers, making FPGA placement impossible. Instead, V2 imports V1’s verified 16×16 systolic array (256 MACs) and time-multiplexes it across all 3 layers in 2,978 cycles using dual ping-pong RAMs.
          </p>
        </div>

        <div className={styles.insightCard}>
          <div className={styles.insightIcon}><Zap size={20} /></div>
          <h4 className={styles.insightTitle}>3. Fused MaxPool + ReLU Hardware Optimization</h4>
          <p className={styles.insightDesc}>
            Because ReLU is monotonically non-decreasing, max(ReLU(x)) is mathematically identical to ReLU(max(x)). By placing the ReLU unit immediately after the 2×2 pooling tree, V2 eliminates 75% of ReLU activation hardware operations with zero bit-level distortion.
          </p>
        </div>
      </div>
    </section>
  );
};
