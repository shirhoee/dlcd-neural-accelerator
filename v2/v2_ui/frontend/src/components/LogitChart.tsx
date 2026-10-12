import React from 'react';
import styles from '../App.module.css';

interface LogitChartProps {
  logits: number[];
  prediction: number;
}

export const LogitChart: React.FC<LogitChartProps> = ({ logits, prediction }) => {
  if (!logits || logits.length === 0) return null;

  const maxLogit = Math.max(...logits);
  const range = Math.max(1, maxLogit - Math.min(...logits));
  const temp = range / 5.0; // Dynamic temperature scaling
  const exps = logits.map((l) => Math.exp((l - maxLogit) / temp));
  const sumExps = exps.reduce((a, b) => a + b, 0);
  const probs = exps.map((e) => e / sumExps);

  return (
    <div className={styles.logitChart}>
      {logits.map((_val, idx) => {
        const isMax = idx === prediction;
        const ht = Math.max(2, probs[idx] * 100);
        return (
          <div key={idx} className={styles.logitBarContainer}>
            <div
              className={`${styles.logitBar} ${isMax ? styles.barActive : styles.barInactive}`}
              style={{ height: `${ht}%` }}
            />
            <span className={`${styles.logitLabel} ${isMax ? styles.labelActive : ''}`}>
              {idx}
            </span>
          </div>
        );
      })}
    </div>
  );
};
