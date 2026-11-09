import React from 'react';
import styles from './PresetRibbon.module.css';
import { PRESET_DIGITS } from '../../data/presetDigits';
import { Sparkles } from 'lucide-react';

interface PresetRibbonProps {
  onSelectPreset: (digit: number, matrix: number[][]) => void;
  disabled?: boolean;
}

export const PresetRibbon: React.FC<PresetRibbonProps> = ({ onSelectPreset, disabled }) => {
  const digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  return (
    <div className={styles.container}>
      <div className={styles.ribbonHeader}>
        <Sparkles size={14} className={styles.sparkleIcon} />
        <span>INSTANT MNIST TEST PRESETS:</span>
      </div>
      <div className={styles.btnRow}>
        {digits.map((d) => (
          <button
            key={d}
            className={styles.digitBtn}
            onClick={() => onSelectPreset(d, PRESET_DIGITS[d])}
            disabled={disabled}
            title={`Run hardware test with canonical MNIST digit ${d}`}
          >
            {d}
          </button>
        ))}
      </div>
    </div>
  );
};
