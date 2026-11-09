import React from 'react';

export interface FeatureGridProps {
  data: number[][];
  colorHex: string;
}

export const FeatureGrid: React.FC<FeatureGridProps> = ({ data, colorHex }) => {
  if (!data || data.length === 0) return null;
  const w = data[0].length;
  const maxVal = Math.max(0.01, ...data.flat().map((v: number) => Math.abs(v)));

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${w}, minmax(0, 1fr))`,
        gap: '2px',
        width: 'fit-content',
      }}
    >
      {data.map((row: number[], i: number) =>
        row.map((val: number, j: number) => {
          const op = Math.max(0, val / maxVal);
          return (
            <div
              key={`${i}-${j}`}
              style={{
                width: '8px',
                height: '8px',
                backgroundColor: `rgba(${colorHex}, ${op})`,
                borderRadius: '1px',
              }}
            />
          );
        })
      )}
    </div>
  );
};
