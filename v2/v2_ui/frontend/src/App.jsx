import React, { useState } from 'react';

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

  const FeatureGrid = ({ data, colorClass }) => {
    if (!data || data.length === 0) return null;
    const h = data.length;
    const w = data[0].length;
    const maxVal = Math.max(0.01, ...data.flat().map(v => Math.abs(v)));
    
    return (
      <div className="grid gap-px bg-gray-700 p-px" style={{ gridTemplateColumns: `repeat(${w}, minmax(0, 1fr))` }}>
        {data.map((row, i) =>
          row.map((val, j) => {
            const op = Math.max(0, val / maxVal);
            return (
              <div key={`${i}-${j}`} className={`w-2 h-2 sm:w-3 sm:h-3 ${colorClass}`} style={{ opacity: op }} />
            );
          })
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen p-8 text-gray-100 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8 text-blue-400">V2 Accelerator Glass Box</h1>
      
      <div className="flex flex-col xl:flex-row gap-8 w-full max-w-7xl">
        
        {/* LEFT PANEL: DRAWING */}
        <div className="flex flex-col items-center bg-gray-800 p-6 rounded-xl border border-gray-700 shrink-0">
          <h2 className="text-xl mb-4 text-gray-300">Input Digit (28x28)</h2>
          <div 
            className="grid bg-gray-900 border border-gray-600 touch-none"
            style={{ gridTemplateColumns: `repeat(${GRID_SIZE}, 12px)` }}
            onMouseLeave={() => setIsDrawing(false)}
            onMouseUp={() => setIsDrawing(false)}
            onMouseDown={() => setIsDrawing(true)}
          >
            {drawing.map((row, r) =>
              row.map((val, c) => (
                <div 
                  key={`${r}-${c}`} 
                  className="w-[12px] h-[12px]" 
                  style={{ backgroundColor: `rgba(255, 255, 255, ${val})` }}
                  onMouseDown={() => drawPixel(r, c)}
                  onMouseEnter={() => isDrawing && drawPixel(r, c)}
                />
              ))
            )}
          </div>
          <div className="flex gap-4 mt-6">
            <button 
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition"
              onClick={() => setDrawing(Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0)))}
            >
              Clear
            </button>
            <button 
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded font-bold shadow-lg shadow-blue-900 transition"
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Running...' : 'Run Accelerator'}
            </button>
          </div>
        </div>
        
        {/* RIGHT PANEL: VISUALIZER */}
        <div className="flex flex-col gap-6 w-full flex-grow bg-gray-800 p-6 rounded-xl border border-gray-700">
          <div className="flex justify-between items-center border-b border-gray-700 pb-4">
            <h2 className="text-xl text-gray-300">Feature Maps & Output</h2>
            {result && (
              <div className="text-2xl font-bold">
                Prediction: <span className="text-blue-400">{result.prediction}</span>
              </div>
            )}
          </div>

          {!result ? (
            <div className="text-center text-gray-500 mt-20">Draw a digit and run to inspect internal logic.</div>
          ) : (
            <div className="flex flex-col gap-8">
              
              {/* Logits */}
              <div>
                <h3 className="text-sm text-gray-400 mb-2 uppercase tracking-wider font-semibold">Raw Logits (Dense -> Argmax)</h3>
                <div className="flex gap-2 items-end h-32 border-b border-gray-700 pb-2">
                  {result.logits.map((val, idx) => {
                    const isMax = idx === result.prediction;
                    const h = Math.max(5, (val / Math.max(...result.logits.map(Math.abs))) * 100);
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center justify-end gap-2 group">
                        <span className="text-xs text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">{val.toFixed(1)}</span>
                        <div 
                          className={`w-full rounded-t-sm ${isMax ? 'bg-blue-500' : 'bg-gray-600'}`} 
                          style={{ height: `${h}%` }}
                        />
                        <span className={`font-mono ${isMax ? 'text-blue-400 font-bold' : 'text-gray-400'}`}>{idx}</span>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Pre-processed Input */}
              <div>
                 <h3 className="text-sm text-gray-400 mb-2 uppercase tracking-wider font-semibold">Downsampled Hardware Input (20x20)</h3>
                 <div className="flex">
                   <FeatureGrid data={result.input} colorClass="bg-white" />
                 </div>
              </div>

              {/* MaxPool1 */}
              <div>
                <h3 className="text-sm text-gray-400 mb-2 uppercase tracking-wider font-semibold">MaxPool1 Channels (4x10x10)</h3>
                <div className="flex flex-wrap gap-4">
                  {result.mp1.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorClass="bg-green-500" />
                  ))}
                </div>
              </div>
              
              {/* MaxPool2 */}
              <div>
                <h3 className="text-sm text-gray-400 mb-2 uppercase tracking-wider font-semibold">MaxPool2 Channels (8x5x5)</h3>
                <div className="flex flex-wrap gap-4">
                  {result.mp2.map((ch, i) => (
                    <FeatureGrid key={i} data={ch} colorClass="bg-purple-500" />
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
