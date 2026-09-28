import React, { useState, useRef, useEffect } from 'react';
import styles from './App.module.css';

const GRID_SIZE = 28;
const CANVAS_SIZE = 280; // 10x scale for smooth drawing

function App() {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 });

  // Initialize canvas background to black
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = 'black';
      ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    }
  }, []);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    // Support both mouse and touch events
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  };

  const startDrawing = (e) => {
    e.preventDefault();
    setIsDrawing(true);
    const pos = getCoordinates(e);
    setLastPos(pos);
    draw(e, pos); // Draw a dot immediately
  };

  const draw = (e, initialPos = null) => {
    e.preventDefault();
    if (!isDrawing && !initialPos) return;
    
    const pos = initialPos || getCoordinates(e);
    const ctx = canvasRef.current.getContext('2d');
    
    ctx.strokeStyle = 'white';
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 20; // Fat brush for MNIST

    ctx.beginPath();
    ctx.moveTo(lastPos.x, lastPos.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    setLastPos(pos);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    setResult(null);
  };

  const extract28x28 = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE).data;
    
    const grid = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0));
    const scale = CANVAS_SIZE / GRID_SIZE; // 10

    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        let sum = 0;
        // Average the 10x10 block
        for (let y = 0; y < scale; y++) {
          for (let x = 0; x < scale; x++) {
            const px = (c * scale) + x;
            const py = (r * scale) + y;
            const idx = (py * CANVAS_SIZE + px) * 4;
            sum += imageData[idx]; // Red channel (since it's grayscale white-on-black)
          }
        }
        // Normalize 0-255 to 0.0-1.0
        grid[r][c] = (sum / (scale * scale)) / 255.0;
      }
    }
    return grid;
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      const drawing = extract28x28();
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
          <h2 className={styles.panelTitle}>Input Digit (Draw Smoothly!)</h2>
          <div className={styles.drawingBoardWrapper}>
            <canvas
              ref={canvasRef}
              width={CANVAS_SIZE}
              height={CANVAS_SIZE}
              className={styles.smoothCanvas}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchMove={draw}
              onTouchEnd={stopDrawing}
              onTouchCancel={stopDrawing}
            />
          </div>
          <div className={styles.controls}>
            <button className={`${styles.btn} ${styles.btnClear}`} onClick={clearCanvas}>
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
                    const range = Math.max(1, maxLogit - Math.min(...result.logits));
                    const temp = range / 5.0; // Dynamic temperature scaling
                    const exps = result.logits.map(l => Math.exp((l - maxLogit) / temp));
                    const sumExps = exps.reduce((a, b) => a + b, 0);
                    const probs = exps.map(e => e / sumExps);
                    
                    return result.logits.map((val, idx) => {
                      const isMax = idx === result.prediction;
                      const ht = Math.max(2, probs[idx] * 100);
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
