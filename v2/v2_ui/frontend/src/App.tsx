import React, { useRef } from 'react';
import styles from './App.module.css';
import { CanvasBoard } from './components/CanvasBoard.tsx';
import { FeatureGrid } from './components/FeatureGrid.tsx';
import { LogitChart } from './components/LogitChart.tsx';
import { usePredict } from './hooks/usePredict.ts';
import { extract28x28FromCanvas, CANVAS_SIZE } from './utils/downsample.ts';

export const App: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { result, loading, runPrediction, clearResult } = usePredict();

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
      }
    }
    clearResult();
  };

  const handleRun = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const drawing = extract28x28FromCanvas(canvas);
    runPrediction(drawing);
  };

  return (
    <div className={styles.dashboard}>
      <h1 className={styles.title}>V2 Accelerator Glass Box</h1>

      <div className={styles.layout}>
        <CanvasBoard
          canvasRef={canvasRef}
          loading={loading}
          onClear={handleClear}
          onRun={handleRun}
        />

        <div className={`${styles.panel} ${styles.rightPanel}`}>
          <div className={styles.headerRow}>
            <h2 className={styles.panelTitle} style={{ marginBottom: 0 }}>
              Feature Maps & Output
            </h2>
            {result && (
              <div className={styles.prediction}>
                Prediction: <span className={styles.predictionHighlight}>{result.prediction}</span>
              </div>
            )}
          </div>

          {!result ? (
            <div className={styles.emptyState}>Draw a digit and run to inspect internal logic.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <div>
                <h3 className={styles.sectionTitle}>Raw Logits (Dense -&gt; Argmax)</h3>
                <LogitChart logits={result.logits} prediction={result.prediction} />
              </div>

              <div>
                <h3 className={styles.sectionTitle}>Downsampled Hardware Input (20x20)</h3>
                <div className={styles.featureMaps}>
                  <FeatureGrid data={result.input} colorHex="255, 255, 255" />
                </div>
              </div>

              <div>
                <h3 className={styles.sectionTitle}>MaxPool1 Channels (4x10x10)</h3>
                <div className={styles.featureMaps}>
                  {result.mp1.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorHex="16, 185, 129" />
                  ))}
                </div>
              </div>

              <div>
                <h3 className={styles.sectionTitle}>MaxPool2 Channels (8x5x5)</h3>
                <div className={styles.featureMaps}>
                  {result.mp2.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorHex="16, 185, 129" />
                  ))}
                </div>
              </div>

              <div>
                <h3 className={styles.sectionTitle}>Dense 1 (64 Neurons)</h3>
                <div className={styles.featureMaps}>
                  {(() => {
                    const grid: number[][] = [];
                    if (result.dense1) {
                      for (let i = 0; i < 8; i++) {
                        const row: number[] = [];
                        for (let j = 0; j < 8; j++) row.push(result.dense1[i * 8 + j] || 0);
                        grid.push(row);
                      }
                    }
                    return <FeatureGrid data={grid} colorHex="59, 130, 246" />;
                  })()}
                </div>
              </div>

              <div>
                <h3 className={styles.sectionTitle}>Dense 2 (32 Neurons)</h3>
                <div className={styles.featureMaps}>
                  {(() => {
                    const grid: number[][] = [];
                    if (result.dense2) {
                      for (let i = 0; i < 4; i++) {
                        const row: number[] = [];
                        for (let j = 0; j < 8; j++) row.push(result.dense2[i * 8 + j] || 0);
                        grid.push(row);
                      }
                    }
                    return <FeatureGrid data={grid} colorHex="139, 92, 246" />;
                  })()}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
