import React, { useRef, useState, useEffect } from 'react';
import styles from './SmoothCanvas.module.css';
import { extract28x28FromCanvas, CANVAS_SIZE } from '../../utils/downsample';
import { Trash2, Play, Brush } from 'lucide-react';

interface SmoothCanvasProps {
  onRun: (matrix28: number[][]) => void;
  loading: boolean;
  presetMatrix?: number[][] | null;
  onClearPreset?: () => void;
}

export const SmoothCanvas: React.FC<SmoothCanvasProps> = ({
  onRun,
  loading,
  presetMatrix,
  onClearPreset
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [lastPoint, setLastPoint] = useState<{ x: number; y: number } | null>(null);
  const [brushSize, setBrushSize] = useState<number>(20);

  // Initialize black canvas
  const initCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#030712';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
  };

  useEffect(() => {
    initCanvas();
  }, []);

  // When a preset matrix is selected, render it onto canvas
  useEffect(() => {
    if (!presetMatrix) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#030712';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    const scale = CANVAS_SIZE / 28;
    for (let r = 0; r < 28; r++) {
      for (let c = 0; c < 28; c++) {
        const val = presetMatrix[r][c];
        if (val > 0.05) {
          const brightness = Math.min(255, Math.floor(val * 255));
          ctx.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness})`;
          ctx.fillRect(c * scale, r * scale, scale, scale);
        }
      }
    }
  }, [presetMatrix]);

  const getCanvasPos = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
    return {
      x: ((clientX - rect.left) / rect.width) * CANVAS_SIZE,
      y: ((clientY - rect.top) / rect.height) * CANVAS_SIZE
    };
  };

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (onClearPreset) onClearPreset();
    setIsDrawing(true);
    const pos = getCanvasPos(e);
    setLastPoint(pos);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing || !lastPoint) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const currentPos = getCanvasPos(e);

    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Dual-pass glow: Cyan plasma blur + solid white core
    ctx.shadowBlur = 12;
    ctx.shadowColor = '#06b6d4';
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = brushSize;

    ctx.beginPath();
    ctx.moveTo(lastPoint.x, lastPoint.y);
    const midX = (lastPoint.x + currentPos.x) / 2;
    const midY = (lastPoint.y + currentPos.y) / 2;
    ctx.quadraticCurveTo(lastPoint.x, lastPoint.y, midX, midY);
    ctx.stroke();

    setLastPoint(currentPos);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    setLastPoint(null);
  };

  const handleClear = () => {
    initCanvas();
    if (onClearPreset) onClearPreset();
  };

  const handleExecute = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const matrix = extract28x28FromCanvas(canvas);
    onRun(matrix);
  };

  return (
    <div className={styles.canvasWrapper}>
      <div className={styles.canvasFrame}>
        <canvas
          ref={canvasRef}
          width={CANVAS_SIZE}
          height={CANVAS_SIZE}
          className={styles.canvas}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
        <div className={styles.gridOverlay}></div>
      </div>

      {/* Brush Settings */}
      <div className={styles.brushToolbar}>
        <div className={styles.brushGroup}>
          <span className={styles.brushLabel}><Brush size={13} /> STROKE:</span>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 16 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(16)}
          >
            Fine
          </button>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 22 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(22)}
          >
            Medium
          </button>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 28 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(28)}
          >
            Fat
          </button>
        </div>

        <button className={styles.clearBtn} onClick={handleClear} title="Clear Drawing Canvas">
          <Trash2 size={14} /> Clear
        </button>
      </div>

      {/* Main Execute Button */}
      <button
        className={`${styles.runBtn} ${loading ? styles.runLoading : ''}`}
        onClick={handleExecute}
        disabled={loading}
      >
        <Play size={18} className={styles.runIcon} />
        <span>{loading ? 'SIMULATING RTL IN ICARUS...' : 'RUN HARDWARE INFERENCE'}</span>
      </button>
    </div>
  );
};
