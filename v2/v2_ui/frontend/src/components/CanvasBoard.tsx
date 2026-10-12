import React, { useRef, useEffect } from 'react';
import styles from '../App.module.css';
import { CANVAS_SIZE } from '../utils/downsample.ts';
import type { Coordinate } from '../types/api.ts';

interface CanvasBoardProps {
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  loading: boolean;
  onClear: () => void;
  onRun: () => void;
}

export const CanvasBoard: React.FC<CanvasBoardProps> = ({
  canvasRef,
  loading,
  onClear,
  onRun,
}) => {
  const isDrawing = useRef<boolean>(false);
  const lastPos = useRef<Coordinate>({ x: 0, y: 0 });

  // Initialize canvas background to black
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
      }
    }
  }, [canvasRef]);

  const getCoordinates = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ): Coordinate => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const clientX =
      'touches' in e && e.touches.length > 0
        ? e.touches[0].clientX
        : (e as React.MouseEvent).clientX;
    const clientY =
      'touches' in e && e.touches.length > 0
        ? e.touches[0].clientY
        : (e as React.MouseEvent).clientY;

    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  };

  const draw = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
    initialPos: Coordinate | null = null
  ) => {
    e.preventDefault();
    if (!isDrawing.current && !initialPos) return;

    const pos = initialPos || getCoordinates(e);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.strokeStyle = 'white';
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = 24; // Matches MNIST stroke weight

    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    lastPos.current = pos;
  };

  const startDrawing = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    e.preventDefault();
    isDrawing.current = true;
    const pos = getCoordinates(e);
    lastPos.current = pos;
    draw(e, pos);
  };

  const stopDrawing = () => {
    isDrawing.current = false;
  };

  return (
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
        <button className={`${styles.btn} ${styles.btnClear}`} onClick={onClear}>
          Clear
        </button>
        <button
          className={`${styles.btn} ${styles.btnRun}`}
          onClick={onRun}
          disabled={loading}
        >
          {loading ? 'Running...' : 'Run Accelerator'}
        </button>
      </div>
    </div>
  );
};
