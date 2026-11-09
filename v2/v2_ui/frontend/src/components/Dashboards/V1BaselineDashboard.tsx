import React, { useState } from 'react';
import styles from './V1BaselineDashboard.module.css';
import { SmoothCanvas } from '../Canvas/SmoothCanvas';
import { PresetRibbon } from '../Canvas/PresetRibbon';
import { FeatureHeatmap } from '../FeatureGrid/FeatureHeatmap';
import { LogitChart } from '../LogitChart/LogitChart';
import { V1PredictResponse } from '../../types/api';
import { Award, AlertTriangle, Activity } from 'lucide-react';

interface V1BaselineDashboardProps {
  onPredictV1: (matrix28: number[][]) => Promise<V1PredictResponse>;
}

export const V1BaselineDashboard: React.FC<V1BaselineDashboardProps> = ({ onPredictV1 }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<V1PredictResponse | null>(null);
  const [presetMatrix, setPresetMatrix] = useState<number[][] | null>(null);

  const handleRun = async (matrix28: number[][]) => {
    setLoading(true);
    try {
      const res = await onPredictV1(matrix28);
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
      <div className={styles.v1Notice}>
        <AlertTriangle size={18} className={styles.warnIcon} />
        <div>
          <strong>Version 1 Baseline Mode:</strong> Evaluates the legacy 3-layer MLP architecture ($100 \rightarrow 16 \rightarrow 6 \rightarrow 10$) using fixed-point Q7.8 systolic array weights.
        </div>
      </div>

      <div className={styles.mainGrid}>
        {/* Left Column: Drawing */}
        <div className={styles.leftCol}>
          <div className={styles.panelCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardTag}>V1 INPUT STUDIO</span>
              <h3 className={styles.cardTitle}>Draw Digit (10×10 Target)</h3>
              <p className={styles.cardDesc}>
                V1 downsamples the canvas directly to 10×10 pixels before feeding the 100-input systolic array.
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

        {/* Right Column: V1 Activations */}
        <div className={styles.rightCol}>
          {result ? (
            <>
              {/* Winner Banner */}
              <div className={styles.winnerHero}>
                <div className={styles.winnerLeft}>
                  <div className={styles.winnerBadge}>
                    <Award size={20} className={styles.awardIcon} />
                    <span>V1 BASELINE PREDICTION</span>
                  </div>
                  <div className={styles.digitDisplayRow}>
                    <span className={styles.digitNumber}>{result.prediction}</span>
                    <div>
                      <div className={styles.baselineTag}>
                        BASELINE ACCURACY: <strong>93.06%</strong>
                      </div>
                      <div className={styles.cycleReadout}>
                        ⏱️ Latency: <strong>6,139 Clock Cycles</strong> (61.39 µs @ 100 MHz)
                      </div>
                    </div>
                  </div>
                </div>

                <div className={styles.v1Specs}>
                  <div className={styles.specBox}>
                    <span>TOPOLOGY</span>
                    <strong>100 → 16 → 6 → 10</strong>
                  </div>
                  <div className={styles.specBox}>
                    <span>RECEPTIVE FIELD</span>
                    <strong>Global (No 2D Convolutions)</strong>
                  </div>
                </div>
              </div>

              {/* V1 Layer Breakdown */}
              <div className={styles.layersStack}>
                {/* 10x10 Downsampled Grid */}
                <div className={styles.layerCard}>
                  <h4 className={styles.layerHeading}>1. Downsampled Hardware Input (10×10)</h4>
                  <div className={styles.centerHeatmap}>
                    <FeatureHeatmap data={result.input_10x10} colorHex="245, 158, 11" label="V1 10×10 Grid" cellSize={16} />
                  </div>
                </div>

                {/* Hidden Layers 1 & 2 Activations */}
                <div className={styles.layerCard}>
                  <h4 className={styles.layerHeading}>2. Hidden Layer Activations</h4>
                  <div className={styles.neuronMetersGrid}>
                    {/* Layer 1 (16 neurons) */}
                    <div className={styles.neuronSubGroup}>
                      <span className={styles.neuronSubTitle}>Layer 1 (16 Neurons)</span>
                      <div className={styles.barsGrid16}>
                        {result.layer1.map((act, i) => (
                          <div key={i} className={styles.miniNeuronBar}>
                            <div className={styles.barFill} style={{ height: `${Math.min(100, act * 30)}%` }} />
                            <span className={styles.neuronIdx}>n{i}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Layer 2 (6 neurons) */}
                    <div className={styles.neuronSubGroup}>
                      <span className={styles.neuronSubTitle}>Layer 2 (6 Neurons)</span>
                      <div className={styles.barsGrid6}>
                        {result.layer2.map((act, i) => (
                          <div key={i} className={styles.miniNeuronBar}>
                            <div className={styles.barFill2} style={{ height: `${Math.min(100, act * 30)}%` }} />
                            <span className={styles.neuronIdx}>n{i}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Logits */}
                <div className={styles.layerCard}>
                  <h4 className={styles.layerHeading}>3. Softmax Output Logits</h4>
                  <LogitChart logits={result.logits} prediction={result.prediction} />
                </div>
              </div>
            </>
          ) : (
            <div className={styles.emptyHero}>
              <Activity size={24} className={styles.emptyIcon} />
              <span>Draw a digit on the left and click <strong>RUN HARDWARE INFERENCE</strong> to evaluate the V1 baseline.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
