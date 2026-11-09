import React, { useState } from 'react';
import styles from './FeatureHeatmap.module.css';

interface FeatureHeatmapProps {
  data: number[][];
  colorHex?: string; // e.g. "56, 189, 248"
  label?: string;
  cellSize?: number;
}

export const FeatureHeatmap: React.FC<FeatureHeatmapProps> = ({
  data,
  colorHex = "56, 189, 248",
  label,
  cellSize = 12
}) => {
  const [hoveredCell, setHoveredCell] = useState<{ r: number; c: number; val: number } | null>(null);

  if (!data || data.length === 0) return null;
  const rows = data.length;
  const cols = data[0].length;

  // Find max for contrast normalization
  let maxVal = 0.0001;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (Math.abs(data[r][c]) > maxVal) maxVal = Math.abs(data[r][c]);
    }
  }

  const toHex16 = (val: number) => {
    const q7_8 = Math.round(val * 256.0);
    const u16 = q7_8 & 0xFFFF;
    return '0x' + u16.toString(16).padStart(4, '0').toUpperCase();
  };

  return (
    <div className={styles.heatmapWrapper}>
      {label && <div className={styles.mapLabel}>{label}</div>}

      <div
        className={styles.gridContainer}
        style={{
          gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`
        }}
      >
        {data.map((row, r) =>
          row.map((val, c) => {
            const intensity = Math.min(1, Math.max(0, Math.abs(val) / maxVal));
            return (
              <div
                key={`${r}-${c}`}
                className={styles.cell}
                style={{
                  width: `${cellSize}px`,
                  height: `${cellSize}px`,
                  backgroundColor: `rgba(${colorHex}, ${intensity * 0.9 + 0.05})`,
                  borderColor: intensity > 0.4 ? `rgba(${colorHex}, 0.6)` : 'rgba(255, 255, 255, 0.04)'
                }}
                onMouseEnter={() => setHoveredCell({ r, c, val })}
                onMouseLeave={() => setHoveredCell(null)}
              />
            );
          })
        )}
      </div>

      {/* Floating Q7.8 Inspector Tooltip */}
      {hoveredCell && (
        <div className={styles.inspectorTooltip}>
          <div className={styles.ttHeader}>
            <span>COORD: ({hoveredCell.r}, {hoveredCell.c})</span>
            <span className={styles.ttFormat}>Q7.8 FIXED-POINT</span>
          </div>
          <div className={styles.ttBody}>
            <div>Hex: <strong className={styles.ttHex}>{toHex16(hoveredCell.val)}</strong></div>
            <div>Float: <strong className={styles.ttVal}>{hoveredCell.val.toFixed(4)}</strong></div>
          </div>
        </div>
      )}
    </div>
  );
};
