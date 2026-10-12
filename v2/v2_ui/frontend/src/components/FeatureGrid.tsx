import React from 'react';
import styles from '../App.module.css';
import type { FeatureGridProps } from '../types/api.ts';

export const FeatureGrid: React.FC<FeatureGridProps> = ({ data, colorHex }) => {
  if (!data || data.length === 0) return null;
  const w = data[0].length;
  const maxVal = Math.max(0.01, ...data.flat().map((v) => Math.abs(v)));

  return (
    <div
      className={styles.featureGrid}
      style={{ gridTemplateColumns: `repeat(${w}, minmax(0, 1fr))` }}
    >
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
