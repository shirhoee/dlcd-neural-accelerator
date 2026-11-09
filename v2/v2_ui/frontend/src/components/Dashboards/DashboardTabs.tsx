import React, { useState } from 'react';
import styles from './DashboardTabs.module.css';
import { V2StudioDashboard } from './V2StudioDashboard';
import { V1BaselineDashboard } from './V1BaselineDashboard';
import { DualComparisonDashboard } from './DualComparisonDashboard';
import type { PredictResponse, V1PredictResponse, ComparePredictResponse } from '../../types/api';
import { Sparkles, Layers, SplitSquareVertical } from 'lucide-react';

interface DashboardTabsProps {
  onPredictV2: (matrix28: number[][]) => Promise<PredictResponse>;
  onPredictV1: (matrix28: number[][]) => Promise<V1PredictResponse>;
  onPredictCompare: (matrix28: number[][]) => Promise<ComparePredictResponse>;
}

type TabMode = 'v2' | 'v1' | 'compare';

export const DashboardTabs: React.FC<DashboardTabsProps> = ({
  onPredictV2,
  onPredictV1,
  onPredictCompare,
}) => {
  const [activeTab, setActiveTab] = useState<TabMode>('v2');

  return (
    <div className={styles.container}>
      {/* Tab Navigation Pill Bar */}
      <div className={styles.tabNav}>
        <button
          className={`${styles.tabBtn} ${activeTab === 'v2' ? styles.activeV2 : ''}`}
          onClick={() => setActiveTab('v2')}
        >
          <Sparkles size={16} />
          <span>V2 Glass-Box CNN Accelerator (Primary)</span>
          <span className={styles.tabBadgeCyan}>98.83%</span>
        </button>

        <button
          className={`${styles.tabBtn} ${activeTab === 'v1' ? styles.activeV1 : ''}`}
          onClick={() => setActiveTab('v1')}
        >
          <Layers size={16} />
          <span>V1 Baseline MLP Studio</span>
          <span className={styles.tabBadgeAmber}>93.06%</span>
        </button>

        <button
          className={`${styles.tabBtn} ${activeTab === 'compare' ? styles.activeCompare : ''}`}
          onClick={() => setActiveTab('compare')}
        >
          <SplitSquareVertical size={16} />
          <span>Side-by-Side Dual Inference</span>
          <span className={styles.tabBadgeGreen}>Co-Sim</span>
        </button>
      </div>

      {/* Tab Content Display */}
      <div className={styles.tabBody}>
        {activeTab === 'v2' && <V2StudioDashboard onPredict={onPredictV2} />}
        {activeTab === 'v1' && <V1BaselineDashboard onPredictV1={onPredictV1} />}
        {activeTab === 'compare' && <DualComparisonDashboard onPredictCompare={onPredictCompare} />}
      </div>
    </div>
  );
};
