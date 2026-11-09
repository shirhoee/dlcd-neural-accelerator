import React from 'react';
import styles from './LogitChart.module.css';

interface LogitChartProps {
  logits: number[];
  prediction: number;
}

export const LogitChart: React.FC<LogitChartProps> = ({ logits, prediction }) => {
  if (!logits || logits.length === 0) return null;

  // Softmax with numerical stability
  const maxLogit = Math.max(...logits);
  const exps = logits.map((l) => Math.exp((l - maxLogit) / 1.5));
  const sumExps = exps.reduce((a, b) => a + b, 0);
  const probs = exps.map((e) => e / sumExps);

  return (
    <div className={styles.container}>
      <div className={styles.chartHeader}>
        <span className={styles.headerLabel}>DIGIT</span>
        <span className={styles.headerLabel}>CONFIDENCE DISTRIBUTION (SOFTMAX)</span>
        <span className={styles.headerLabel}>LOGIT</span>
      </div>

      <div className={styles.barsList}>
        {probs.map((p, digit) => {
          const isWinner = digit === prediction;
          const pct = (p * 100).toFixed(1);

          return (
            <div
              key={digit}
              className={`${styles.barRow} ${isWinner ? styles.winnerRow : ''}`}
            >
              {/* Digit Label */}
              <div className={`${styles.digitBadge} ${isWinner ? styles.winnerBadge : ''}`}>
                {digit}
              </div>

              {/* Bar Track */}
              <div className={styles.track}>
                <div
                  className={`${styles.fill} ${isWinner ? styles.winnerFill : ''}`}
                  style={{ width: `${Math.max(2, p * 100)}%` }}
                />
                <span className={styles.pctText}>{pct}%</span>
              </div>

              {/* Raw Logit Value */}
              <div className={styles.logitVal}>
                {(logits[digit] || 0).toFixed(1)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
