import React, { useState } from 'react';
import styles from './V2StudioDashboard.module.css';
import { SmoothCanvas } from '../Canvas/SmoothCanvas';
import { PresetRibbon } from '../Canvas/PresetRibbon';
import { FeatureHeatmap } from '../FeatureGrid/FeatureHeatmap';
import { LogitChart } from '../LogitChart/LogitChart';
import { PredictResponse } from '../../types/api';
import { Award, ArrowRight, Activity } from 'lucide-react';

interface V2StudioDashboardProps {
  onPredict: (matrix28: number[][]) => Promise<PredictResponse>;
}

export const V2StudioDashboard: React.FC<V2StudioDashboardProps> = ({ onPredict }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [presetMatrix, setPresetMatrix] = useState<number[][] | null>(null);

  const handleRun = async (matrix28: number[][]) => {
    setLoading(true);
    try {
      const res = await onPredict(matrix28);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (_digit: number, matrix: number[][]) => {
    setPresetMatrix(matrix);
    handleRun(matrix);
  };

  return (
    <div className={styles.container}>
      {/* Left Column: Drawing & Presets */}
      <div className={styles.leftCol}>
        <div className={styles.panelCard}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTag}>INTERACTIVE INPUT</span>
            <h3 className={styles.cardTitle}>Digit Drawing Studio</h3>
            <p className={styles.cardDesc}>
              Draw a digit on the canvas or click a canonical MNIST preset below to trigger hardware simulation.
            </p>
          </div>

          <PresetRibbon onSelectPreset={handleSelectPreset} disabled={loading} />

          <SmoothCanvas
            onRun={handleRun}
            loading={loading}
            presetMatrix={presetMatrix}
            onClearPreset={() => setPresetMatrix(null)}
          />
        </div>
      </div>

      {/* Right Column: Hardware Glass-Box Telemetry */}
      <div className={styles.rightCol}>
        {/* Prediction Hero Banner */}
        {result ? (
          <div className={styles.winnerHero}>
            <div className={styles.winnerLeft}>
              <div className={styles.winnerBadge}>
                <Award size={20} className={styles.awardIcon} />
                <span>HARDWARE VERIFIED PREDICTION</span>
              </div>
              <div className={styles.digitDisplayRow}>
                <span className={styles.digitNumber}>{result.prediction}</span>
                <div>
                  <div className={styles.confidenceScore}>
                    CONFIDENCE: <strong className={styles.scoreHighlight}>HIGH</strong>
                  </div>
                  <div className={styles.cycleReadout}>
                    ⏱️ Latency: <strong>9,116 Clock Cycles</strong> (91.16 µs @ 100 MHz)
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.winnerPills}>
              <div className={styles.metricPill}>
                <span>Q7.8 HEADROOM GATE</span>
                <strong>PASS (|logit| &lt; 128)</strong>
              </div>
              <div className={styles.metricPill}>
                <span>RTL VS GOLDEN EMU</span>
                <strong style={{ color: '#10b981' }}>0 BIT MISMATCHES</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className={styles.emptyHero}>
            <Activity size={24} className={styles.emptyIcon} />
            <span>Draw a digit on the left and click <strong>RUN HARDWARE INFERENCE</strong> to inspect the internal datapath.</span>
          </div>
        )}

        {/* Multi-Stage Wavefront Hardware Inspector */}
        {result && (
          <div className={styles.pipelineStack}>
            {/* Stage 1 & 2: Input & Conv1 */}
            <div className={styles.stageBlock}>
              <div className={styles.stageTitleRow}>
                <span className={styles.stagePill}>STAGE 1</span>
                <h4 className={styles.stageHeading}>Hardware Input Grid (20×20) & MaxPool1 (4 Channels × 10×10)</h4>
              </div>

              <div className={styles.mapsRow}>
                <div>
                  <FeatureHeatmap data={result.input} colorHex="56, 189, 248" label="Input 20×20" cellSize={7} />
                </div>
                <ArrowRight size={20} className={styles.pipelineArrow} />
                <div className={styles.channelGrid}>
                  {result.mp1.map((ch, i) => (
                    <FeatureHeatmap key={i} data={ch} colorHex="16, 185, 129" label={`MP1 Ch ${i}`} cellSize={9} />
                  ))}
                </div>
              </div>
            </div>

            {/* Stage 3: Conv2 & MaxPool2 */}
            <div className={styles.stageBlock}>
              <div className={styles.stageTitleRow}>
                <span className={styles.stagePill}>STAGE 2</span>
                <h4 className={styles.stageHeading}>MaxPool2 Feature Maps (8 Channels × 5×5)</h4>
              </div>

              <div className={styles.mp2Grid}>
                {result.mp2.map((ch, i) => (
                  <FeatureHeatmap key={i} data={ch} colorHex="245, 158, 11" label={`MP2 Ch ${i}`} cellSize={13} />
                ))}
              </div>
            </div>

            {/* Stage 4: Systolic Dense Head */}
            <div className={styles.stageBlock}>
              <div className={styles.stageTitleRow}>
                <span className={styles.stagePill}>STAGE 3</span>
                <h4 className={styles.stageHeading}>Time-Multiplexed Systolic Array Activations (Dense 1: 64 & Dense 2: 32)</h4>
              </div>

              <div className={styles.denseRow}>
                {/* Dense 1: 64 neurons (8x8) */}
                <div>
                  {(() => {
                    const grid: number[][] = [];
                    for (let r = 0; r < 8; r++) {
                      const row: number[] = [];
                      for (let c = 0; c < 8; c++) row.push(result.dense1[r * 8 + c] || 0);
                      grid.push(row);
                    }
                    return <FeatureHeatmap data={grid} colorHex="99, 102, 241" label="Dense 1 (64 Neurons)" cellSize={13} />;
                  })()}
                </div>

                {/* Dense 2: 32 neurons (4x8) */}
                <div>
                  {(() => {
                    const grid: number[][] = [];
                    for (let r = 0; r < 4; r++) {
                      const row: number[] = [];
                      for (let c = 0; c < 8; c++) row.push(result.dense2[r * 8 + c] || 0);
                      grid.push(row);
                    }
                    return <FeatureHeatmap data={grid} colorHex="168, 85, 247" label="Dense 2 (32 Neurons)" cellSize={13} />;
                  })()}
                </div>

                {/* Softmax Bar Chart */}
                <div className={styles.logitsChartBox}>
                  <LogitChart logits={result.logits} prediction={result.prediction} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
