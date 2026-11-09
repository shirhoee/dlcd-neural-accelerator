import React, { useState } from 'react';
import styles from './DualComparisonDashboard.module.css';
import { SmoothCanvas } from '../Canvas/SmoothCanvas';
import { PresetRibbon } from '../Canvas/PresetRibbon';
import { FeatureHeatmap } from '../FeatureGrid/FeatureHeatmap';
import { LogitChart } from '../LogitChart/LogitChart';
import type { ComparePredictResponse } from '../../types/api';
import { CheckCircle2, AlertOctagon, Zap, Cpu, Sparkles, ArrowRight } from 'lucide-react';

interface DualComparisonDashboardProps {
  onPredictCompare: (matrix28: number[][]) => Promise<ComparePredictResponse>;
}

export const DualComparisonDashboard: React.FC<DualComparisonDashboardProps> = ({ onPredictCompare }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparePredictResponse | null>(null);
  const [presetMatrix, setPresetMatrix] = useState<number[][] | null>(null);

  const handleRun = async (matrix28: number[][]) => {
    setLoading(true);
    try {
      const res = await onPredictCompare(matrix28);
      setResult(res);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleSelectPreset = (_digit: number, matrix: number[][]) => {
    setPresetMatrix(matrix);
    handleRun(matrix);
  };

  return (
    <div className={styles.container}>
      {/* Top Banner Description */}
      <div className={styles.introCard}>
        <div className={styles.introLeft}>
          <div className={styles.badge}>
            <Sparkles size={14} />
            <span>DUAL-ENGINE HARNESS BENCHMARK</span>
          </div>
          <h2 className={styles.title}>Simultaneous V1 vs V2 Co-Inference</h2>
          <p className={styles.subtitle}>
            Submit a single handwritten digit simultaneously across both hardware generations. 
            Directly observe spatial resolution preservation, feature map extraction, and classification confidence divergence in real time.
          </p>
        </div>
      </div>

      {/* Input Canvas Ribbon */}
      <div className={styles.inputSection}>
        <div className={styles.canvasWrapper}>
          <PresetRibbon onSelectPreset={handleSelectPreset} disabled={loading} />
          <SmoothCanvas
            onRun={handleRun}
            loading={loading}
            presetMatrix={presetMatrix}
            onClearPreset={() => setPresetMatrix(null)}
          />
        </div>
      </div>

      {/* Results Section */}
      {result ? (
        <div className={styles.resultsWrapper}>
          {/* Agreement Hero Banner */}
          <div className={`${styles.agreementHero} ${result.agreement ? styles.agreementMatch : styles.agreementMismatch}`}>
            <div className={styles.agreementIconBox}>
              {result.agreement ? (
                <CheckCircle2 size={32} className={styles.matchIcon} />
              ) : (
                <AlertOctagon size={32} className={styles.mismatchIcon} />
              )}
            </div>
            <div className={styles.agreementText}>
              <div className={styles.agreementStatus}>
                {result.agreement ? 'HARDWARE CONSENSUS REACHED' : 'ARCHITECTURE DIVERGENCE DETECTED'}
              </div>
              <div className={styles.agreementDetails}>
                {result.agreement ? (
                  <>Both V1 Baseline and V2 CNN accelerator unanimously classified this digit as <strong>Digit {result.v2.prediction}</strong>.</>
                ) : (
                  <>V1 Baseline predicted <strong>Digit {result.v1.prediction}</strong> while V2 CNN accelerator classified as <strong>Digit {result.v2.prediction}</strong>.</>
                )}
              </div>
            </div>
            <div className={styles.versusPill}>
              <span className={styles.v1Pill}>V1: {result.v1.prediction}</span>
              <ArrowRight size={16} />
              <span className={styles.v2Pill}>V2: {result.v2.prediction}</span>
            </div>
          </div>

          {/* Side-by-Side Dual Columns */}
          <div className={styles.columnsGrid}>
            {/* Version 1 Baseline Column */}
            <div className={styles.v1Card}>
              <div className={styles.columnHeaderV1}>
                <div className={styles.headerTitleRow}>
                  <div className={styles.modelTagV1}>VERSION 1.0</div>
                  <span className={styles.cyclesTag}>6,139 cycles</span>
                </div>
                <h3 className={styles.archTitle}>Pure MLP Systolic Array</h3>
                <span className={styles.archSubtitle}>100 → 16 → 6 → 10 Fully Connected</span>
              </div>

              {/* Big Prediction Box */}
              <div className={styles.predictionBoxV1}>
                <div className={styles.predLeft}>
                  <span className={styles.predLabel}>V1 PREDICTION</span>
                  <span className={styles.predDigitV1}>{result.v1.prediction}</span>
                </div>
                <div className={styles.predRight}>
                  <div className={styles.metricItem}>
                    <span>ACCURACY</span>
                    <strong className={styles.statAmber}>93.06%</strong>
                  </div>
                  <div className={styles.metricItem}>
                    <span>LATENCY</span>
                    <strong>61.4 µs</strong>
                  </div>
                </div>
              </div>

              {/* Downsampled 10x10 Input */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <Cpu size={15} />
                  <span>10×10 Downsampled Input Matrix</span>
                </div>
                <div className={styles.centerHeatmap}>
                  <FeatureHeatmap data={result.v1.input_10x10} colorHex="245, 158, 11" label="V1 10×10 Input" cellSize={16} />
                </div>
                <p className={styles.lossNote}>
                  ⚠️ Significant spatial aliasing: stroke topology often breaks down at 10×10 resolution.
                </p>
              </div>

              {/* V1 Hidden Activations */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <Zap size={15} />
                  <span>Layer Activations (16 → 6 Neurons)</span>
                </div>
                <div className={styles.v1MiniBarsContainer}>
                  <div className={styles.miniGroup}>
                    <span className={styles.miniGroupLabel}>L1 (16 Neurons)</span>
                    <div className={styles.barStrip16}>
                      {result.v1.layer1.map((act, i) => (
                        <div key={i} className={styles.barStick} style={{ height: `${Math.min(100, act * 30)}%` }} />
                      ))}
                    </div>
                  </div>
                  <div className={styles.miniGroup}>
                    <span className={styles.miniGroupLabel}>L2 (6 Neurons)</span>
                    <div className={styles.barStrip6}>
                      {result.v1.layer2.map((act, i) => (
                        <div key={i} className={styles.barStickAmber} style={{ height: `${Math.min(100, act * 30)}%` }} />
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* V1 Logits */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <span>V1 Logits Distribution</span>
                </div>
                <LogitChart logits={result.v1.logits} prediction={result.v1.prediction} />
              </div>
            </div>

            {/* Version 2 Accelerator Column */}
            <div className={styles.v2Card}>
              <div className={styles.columnHeaderV2}>
                <div className={styles.headerTitleRow}>
                  <div className={styles.modelTagV2}>VERSION 2.0</div>
                  <span className={styles.cyclesTagV2}>9,116 cycles</span>
                </div>
                <h3 className={styles.archTitle}>Pipelined 2D CNN + Systolic Head</h3>
                <span className={styles.archSubtitle}>Conv1(4ch) → Pool1 → Conv2(8ch) → Pool2 → Systolic(200)</span>
              </div>

              {/* Big Prediction Box */}
              <div className={styles.predictionBoxV2}>
                <div className={styles.predLeft}>
                  <span className={styles.predLabel}>V2 PREDICTION</span>
                  <span className={styles.predDigitV2}>{result.v2.prediction}</span>
                </div>
                <div className={styles.predRight}>
                  <div className={styles.metricItem}>
                    <span>ACCURACY</span>
                    <strong className={styles.statCyan}>98.83% (+5.77%)</strong>
                  </div>
                  <div className={styles.metricItem}>
                    <span>LATENCY</span>
                    <strong>91.2 µs</strong>
                  </div>
                </div>
              </div>

              {/* Downsampled 20x20 Input */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <Cpu size={15} />
                  <span>20×20 Preserved Input Matrix</span>
                </div>
                <div className={styles.centerHeatmap}>
                  <FeatureHeatmap data={result.v2.input} colorHex="6, 182, 212" label="V2 20×20 Input" cellSize={11} />
                </div>
                <p className={styles.gainNote}>
                  ✨ 4× pixel density: preserved loops, diagonals, and junction features without loss.
                </p>
              </div>

              {/* V2 Feature Maps Overview */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <Zap size={15} />
                  <span>Conv2 MaxPool Feature Maps (8 Channels × 5×5)</span>
                </div>
                <div className={styles.mp2GridMini}>
                  {result.v2.mp2.map((fmap, ch) => (
                    <div key={ch} className={styles.miniFmapBox}>
                      <span className={styles.fmapLabel}>C{ch}</span>
                      <FeatureHeatmap data={fmap} colorHex="168, 85, 247" cellSize={7} />
                    </div>
                  ))}
                </div>
              </div>

              {/* V2 Logits */}
              <div className={styles.sectionBlock}>
                <div className={styles.sectionHeader}>
                  <span>V2 Logits Distribution</span>
                </div>
                <LogitChart logits={result.v2.logits} prediction={result.v2.prediction} />
              </div>
            </div>
          </div>

          {/* Architectural Comparison Summary Table */}
          <div className={styles.comparisonTableCard}>
            <h4 className={styles.tableTitle}>Hardware Architectural Delta Summary</h4>
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Metric / Subsystem</th>
                    <th>Version 1.0 (Baseline MLP)</th>
                    <th>Version 2.0 (CNN + Systolic)</th>
                    <th>Delta / Engineering Advantage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>MNIST Test Accuracy</strong></td>
                    <td>93.06%</td>
                    <td className={styles.highlightText}>98.83%</td>
                    <td className={styles.highlightGain}>+5.77% (Near SOTA for 16-bit Q7.8)</td>
                  </tr>
                  <tr>
                    <td><strong>Spatial Input Dimension</strong></td>
                    <td>10×10 (100 pixels)</td>
                    <td>20×20 (400 pixels)</td>
                    <td>4× pixel information preserved</td>
                  </tr>
                  <tr>
                    <td><strong>Feature Extraction</strong></td>
                    <td>None (Direct linear projection)</td>
                    <td>Two 3×3 Conv layers (4ch & 8ch)</td>
                    <td>Translation & shift invariance</td>
                  </tr>
                  <tr>
                    <td><strong>Clock Cycles Per Inference</strong></td>
                    <td>6,139 cycles</td>
                    <td>9,116 cycles</td>
                    <td>Only +48.5% cycles for massive accuracy leap</td>
                  </tr>
                  <tr>
                    <td><strong>Arithmetic Format</strong></td>
                    <td>Q7.8 Fixed-Point (Sequential MAC)</td>
                    <td>Q7.8 Fixed-Point (Per-step truncation)</td>
                    <td>Zero floating-point drift, identical 16-bit format</td>
                  </tr>
                  <tr>
                    <td><strong>Hardware Datapath Reuse</strong></td>
                    <td>Single-pass systolic execution</td>
                    <td>Time-multiplexed systolic array (L1, L2, L3)</td>
                    <td>Reused V1 PE array with dual ping-pong RAMs</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.emptyState}>
          <Cpu size={28} className={styles.emptyIcon} />
          <span>Draw a digit above or choose a preset to trigger simultaneous V1 and V2 hardware co-inference.</span>
        </div>
      )}
    </div>
  );
};
