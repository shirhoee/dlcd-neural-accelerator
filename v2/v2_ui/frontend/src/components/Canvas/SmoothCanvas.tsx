import React, { useRef, useState, useEffect, useCallback } from 'react';
import styles from './SmoothCanvas.module.css';
import { extract28x28FromCanvas, CANVAS_SIZE } from '../../utils/downsample';
import { Trash2, Play, Brush, Eye } from 'lucide-react';

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
  onClearPreset,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [lastPoint, setLastPoint] = useState<{ x: number; y: number } | null>(null);
  const [brushSize, setBrushSize] = useState<number>(26);
  const [preview20, setPreview20] = useState<number[][] | null>(null);

  // Initialize black canvas
  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#030712';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    setPreview20(null);
  }, []);

  useEffect(() => {
    initCanvas();
  }, [initCanvas]);

  // Update preview when drawing finishes or preset loads
  const updatePreview = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const { grid20 } = extract28x28FromCanvas(canvas);
    setPreview20(grid20);
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
          ctx.fillRect(c * scale, r * scale, scale + 0.5, scale + 0.5);
        }
      }
    }
    updatePreview();
  }, [presetMatrix, updatePreview]);

  const getCanvasPos = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
    return {
      x: ((clientX - rect.left) / rect.width) * CANVAS_SIZE,
      y: ((clientY - rect.top) / rect.height) * CANVAS_SIZE,
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

    // Anti-aliased stroke with soft cyan glow
    ctx.shadowBlur = 10;
    ctx.shadowColor = 'rgba(6, 182, 212, 0.6)';
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
    if (isDrawing) {
      setIsDrawing(false);
      setLastPoint(null);
      updatePreview();
    }
  };

  const handleClear = () => {
    initCanvas();
    if (onClearPreset) onClearPreset();
  };

  const handleExecute = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const { grid28 } = extract28x28FromCanvas(canvas);
    onRun(grid28);
  };

  return (
    <div className={styles.canvasWrapper}>
      {/* Canvas Viewport */}
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
        <div className={styles.gridOverlay} />
      </div>

      {/* Brush Settings Toolbar */}
      <div className={styles.brushToolbar}>
        <div className={styles.brushGroup}>
          <span className={styles.brushLabel}><Brush size={13} /> STROKE:</span>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 20 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(20)}
          >
            Fine
          </button>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 26 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(26)}
          >
            Medium
          </button>
          <button
            className={`${styles.brushSizeBtn} ${brushSize === 34 ? styles.activeBrush : ''}`}
            onClick={() => setBrushSize(34)}
          >
            Thick
          </button>
        </div>

        <button className={styles.clearBtn} onClick={handleClear} title="Clear Drawing Canvas">
          <Trash2 size={14} /> Clear
        </button>
      </div>

      {/* Live Preprocessed Hardware Preview */}
      {preview20 && (
        <div className={styles.previewBox}>
          <div className={styles.previewHeader}>
            <Eye size={13} className={styles.previewIcon} />
            <span>MNIST CENTER-OF-MASS HARDWARE VIEW (20×20)</span>
          </div>
          <div className={styles.previewContent}>
            <div className={styles.previewGrid}>
              {preview20.map((row, r) =>
                row.map((val, c) => (
                  <div
                    key={`${r}-${c}`}
                    className={styles.previewCell}
                    style={{
                      backgroundColor: `rgba(6, 182, 212, ${Math.min(1, val * 1.2)})`,
                    }}
                  />
                ))
              )}
            </div>
            <div className={styles.previewStats}>
              <span>&bull; Aspect ratio preserved</span>
              <span>&bull; Center of mass centered at (13.5, 13.5)</span>
              <span>&bull; Scaled to 20×20 bounding box</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Execute Button */}
      <button
        className={`${styles.runBtn} ${loading ? styles.runLoading : ''}`}
        onClick={handleExecute}
        disabled={loading}
      >
        <Play size={18} className={styles.runIcon} />
        <span>{loading ? 'SIMULATING RTL IN ICARUS VERILOG...' : 'RUN HARDWARE INFERENCE'}</span>
      </button>
    </div>
  );
};
