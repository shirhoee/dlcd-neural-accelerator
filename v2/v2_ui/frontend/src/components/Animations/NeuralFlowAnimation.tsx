import React from 'react';
import styles from './NeuralFlowAnimation.module.css';
import { Layers, Activity } from 'lucide-react';

interface NeuralFlowAnimationProps {
  activeStage?: number; // 0..5
  isSimulating?: boolean;
}

export const NeuralFlowAnimation: React.FC<NeuralFlowAnimationProps> = ({
  activeStage = 0,
  isSimulating = false,
}) => {
  const stages = [
    { id: 1, name: 'Input 20×20', sub: '400 Pixels', color: '#e11d48' },
    { id: 2, name: 'Conv1 (4ch)', sub: '3×3 Windows', color: '#be123c' },
    { id: 3, name: 'MaxPool 1', sub: '4×10×10', color: '#9f1239' },
    { id: 4, name: 'Conv2 (8ch)', sub: '3×3 Filters', color: '#be123c' },
    { id: 5, name: 'MaxPool 2', sub: '8×5×5 (200)', color: '#9f1239' },
    { id: 6, name: 'Systolic Core', sub: '200→64→32→10', color: '#d4af37' },
    { id: 7, name: 'Argmax', sub: 'Digit [0..9]', color: '#fb7185' },
  ];

  return (
    <div className={styles.flowCard}>
      <div className={styles.flowHeader}>
        <div className={styles.headerLeft}>
          <Layers size={16} className={styles.headerIcon} />
          <span className={styles.headerTitle}>RTL PIPELINE DATAFLOW WAVEFRONT</span>
        </div>
        <div className={styles.liveIndicator}>
          <Activity size={13} className={`${styles.pulseIcon} ${isSimulating ? styles.pulseActive : ''}`} />
          <span>{isSimulating ? 'SIMULATION IN FLIGHT (100 MHz)' : 'HARDWARE PIPELINE IDLE'}</span>
        </div>
      </div>

      <div className={styles.pipelineTrack}>
        {stages.map((stage, idx) => {
          const isPassed = isSimulating || activeStage >= stage.id;
          const isCurrent = isSimulating && (activeStage === stage.id || activeStage === 0);

          return (
            <React.Fragment key={stage.id}>
              <div
                className={`${styles.stageBox} ${isPassed ? styles.stageActive : ''} ${isCurrent ? styles.stagePulse : ''}`}
                style={{ borderColor: stage.color }}
              >
                <span className={styles.stageStep}>S{stage.id}</span>
                <span className={styles.stageName}>{stage.name}</span>
                <span className={styles.stageSub}>{stage.sub}</span>
                {isCurrent && <div className={styles.activeGlowRing} style={{ borderColor: stage.color }} />}
              </div>

              {idx < stages.length - 1 && (
                <div className={styles.connector}>
                  <div
                    className={`${styles.wireSegment} ${isSimulating ? styles.wireFlowing : ''}`}
                  />
                  <span className={styles.wireArrow}>&rarr;</span>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
