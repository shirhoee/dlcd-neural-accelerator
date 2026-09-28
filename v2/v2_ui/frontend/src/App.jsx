import React, { useState } from 'react';
import styles from './App.module.css';

const GRID_SIZE = 28;

function App() {
  const [drawing, setDrawing] = useState(
    Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0))
  );
  const [isDrawing, setIsDrawing] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const drawPixel = (r, c) => {
    setDrawing(prev => {
      const newD = prev.map(row => [...row]);
      newD[r][c] = 1.0;
      if (r > 0) newD[r-1][c] = Math.max(newD[r-1][c], 0.6);
      if (r < GRID_SIZE-1) newD[r+1][c] = Math.max(newD[r+1][c], 0.6);
      if (c > 0) newD[r][c-1] = Math.max(newD[r][c-1], 0.6);
      if (c < GRID_SIZE-1) newD[r][c+1] = Math.max(newD[r][c+1], 0.6);
      return newD;
    });
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: drawing })
      });
      const data = await res.json();
      setResult(data);
    } catch(e) {
      console.error(e);
      alert('Backend error: ' + e.message);
    }
    setLoading(false);
  };

  const FeatureGrid = ({ data, colorHex }) => {
    if (!data || data.length === 0) return null;
    const h = data.length;
    const w = data[0].length;
    const maxVal = Math.max(0.01, ...data.flat().map(v => Math.abs(v)));
    
    // Parse the hex color (e.g. "34, 197, 94") so we can inject opacity
    return (
      <div className={styles.featureGrid} style={{ gridTemplateColumns: `repeat(${w}, minmax(0, 1fr))` }}>
        {data.map((row, i) =>
          row.map((val, j) => {
            const op = Math.max(0, val / maxVal);
            return (
              <div 
                key={`${i}-${j}`} 
                className={styles.featureCell} 
                style={{ backgroundColor: `rgba(${colorHex}, ${op})` }} 
              />
            );
          })
        )}
      </div>
    );
  };

  return (
    <div className={styles.dashboard}>
      <h1 className={styles.title}>V2 Accelerator Glass Box</h1>
      
      <div className={styles.layout}>
        
        {/* LEFT PANEL: DRAWING */}
        <div className={`${styles.panel} ${styles.leftPanel}`}>
          <h2 className={styles.panelTitle}>Input Digit (28x28)</h2>
          <div 
            className={styles.drawingBoard}
            style={{ gridTemplateColumns: `repeat(${GRID_SIZE}, 12px)` }}
            onMouseLeave={() => setIsDrawing(false)}
            onMouseUp={() => setIsDrawing(false)}
            onMouseDown={() => setIsDrawing(true)}
          >
            {drawing.map((row, r) =>
              row.map((val, c) => (
                <div 
                  key={`${r}-${c}`} 
                  className={styles.drawPixel} 
                  style={{ backgroundColor: `rgba(255, 255, 255, ${val})` }}
                  onMouseDown={() => drawPixel(r, c)}
                  onMouseEnter={() => isDrawing && drawPixel(r, c)}
                />
              ))
            )}
          </div>
          <div className={styles.controls}>
            <button 
              className={`${styles.btn} ${styles.btnClear}`}
              onClick={() => setDrawing(Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0)))}
            >
              Clear
            </button>
            <button 
              className={`${styles.btn} ${styles.btnRun}`}
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Running...' : 'Run Accelerator'}
            </button>
          </div>
        </div>
        
        {/* RIGHT PANEL: VISUALIZER */}
        <div className={`${styles.panel} ${styles.rightPanel}`}>
          <div className={styles.headerRow}>
            <h2 className={styles.panelTitle} style={{marginBottom: 0}}>Feature Maps & Output</h2>
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
              
              {/* Logits */}
              <div>
                <h3 className={styles.sectionTitle}>Raw Logits (Dense -&gt; Argmax)</h3>
                <div className={styles.logitChart}>
                  {(() => {
                    const maxLogit = Math.max(...result.logits);
                    const exps = result.logits.map(l => Math.exp(l - maxLogit));
                    const sumExps = exps.reduce((a, b) => a + b, 0);
                    const probs = exps.map(e => e / sumExps);
                    
                    return result.logits.map((val, idx) => {
                      const isMax = idx === result.prediction;
                      const ht = Math.max(2, probs[idx] * 100); // 2% min height for visibility
                      return (
                        <div key={idx} className={styles.logitBarContainer}>
                          <div 
                            className={`${styles.logitBar} ${isMax ? styles.barActive : styles.barInactive}`} 
                            style={{ height: `${ht}%` }}
                          />
                          <span className={`${styles.logitLabel} ${isMax ? styles.labelActive : ''}`}>{idx}</span>
                        </div>
                      )
                    });
                  })()}
                </div>
              </div>

              {/* Pre-processed Input */}
              <div>
                 <h3 className={styles.sectionTitle}>Downsampled Hardware Input (20x20)</h3>
                 <div className={styles.featureMaps}>
                   <FeatureGrid data={result.input} colorHex="255, 255, 255" />
                 </div>
              </div>

              {/* MaxPool1 */}
              <div>
                <h3 className={styles.sectionTitle}>MaxPool1 Channels (4x10x10)</h3>
                <div className={styles.featureMaps}>
                  {result.mp1.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorHex="34, 197, 94" />
                  ))}
                </div>
              </div>
              
              {/* MaxPool2 */}
              <div>
                <h3 className={styles.sectionTitle}>MaxPool2 Channels (8x5x5)</h3>
                <div className={styles.featureMaps}>
                  {result.mp2.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorHex="168, 85, 247" />
                  ))}
                </div>
              </div>
              
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
