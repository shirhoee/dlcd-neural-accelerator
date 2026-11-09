import React, { useState, useEffect } from 'react';
import styles from './App.module.css';
import { TeamHeader } from './components/Header/TeamHeader';
import { ProblemStatementSection } from './components/Sections/ProblemStatementSection';
import { UniversalCircuitDiagram } from './components/Circuit/UniversalCircuitDiagram';
import { FsmVisualizer } from './components/FSM/FsmVisualizer';
import { V1V2Comparison } from './components/Comparison/V1V2Comparison';
import { VerilogCodeBrowser } from './components/Code/VerilogCodeBrowser';
import { DashboardTabs } from './components/Dashboards/DashboardTabs';
import { WaveformsSection } from './components/Sections/WaveformsSection';
import { ProjectReportSection } from './components/Documentation/ProjectReportSection';
import { ReferencesSection } from './components/Sections/ReferencesSection';
import { usePredict } from './hooks/usePredict';
import { 
  PlayCircle, 
  GitFork, 
  Workflow, 
  GitCompare, 
  FileCode, 
  Activity, 
  BookOpen, 
  ScrollText,
  ChevronUp 
} from 'lucide-react';

export const App: React.FC = () => {
  const { predictV2, predictV1, predictCompare } = usePredict();
  const [activeTab, setActiveTab] = useState<string>('studio'); // Default: Zero-scroll Canvas Studio
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navTabs = [
    { id: 'studio', label: '1. Live Drawing Studio', icon: PlayCircle, badge: 'Canvas' },
    { id: 'circuit', label: '2. Gate-Level Circuits', icon: GitFork, badge: 'Vector SVGs' },
    { id: 'fsm', label: '3. FSM State Machines', icon: Workflow, badge: 'Live Stepper' },
    { id: 'comparison', label: '4. V1 vs V2 Comparison', icon: GitCompare, badge: '+5.77% Gain' },
    { id: 'verilog', label: '5. Verilog HDL Code', icon: FileCode, badge: 'RTL' },
    { id: 'waveforms', label: '6. Waveforms & Timing', icon: Activity, badge: '9,116 Cyc' },
    { id: 'docs', label: '7. Project Report & Docs', icon: BookOpen, badge: 'Full ESA' },
    { id: 'full_report', label: 'Continuous Full Report', icon: ScrollText, badge: 'Scroll' },
  ];

  const handleSelectTab = (tabId: string) => {
    setActiveTab(tabId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className={styles.appContainer}>
      {/* PES University & Team Member Header */}
      <header className={styles.headerWrapper}>
        <TeamHeader
          activeSection={activeTab}
          onSelectSection={handleSelectTab}
        />
      </header>

      {/* Sticky Top-Level Tab Switcher */}
      <nav className={styles.stickyNav}>
        <div className={styles.navInner}>
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                className={`${styles.navBtn} ${isActive ? styles.activeNavBtn : ''}`}
                onClick={() => handleSelectTab(tab.id)}
              >
                <Icon size={15} className={isActive ? styles.activeIcon : styles.navIcon} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`${styles.navBadge} ${isActive ? styles.activeBadge : ''}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content Body */}
      <main className={styles.mainContent}>
        {/* TAB 1: Live Drawing Studio & Hardware Inference (Zero-Scroll Canvas!) */}
        {activeTab === 'studio' && (
          <section className={styles.activeTabContent}>
            <div className={styles.sectionIntro}>
              <span className={styles.sectionTag}>PRIMARY INTERACTIVE STUDIO</span>
              <h2 className={styles.sectionHeading}>Hardware-in-the-Loop Digit Inference Studio</h2>
              <p className={styles.sectionDescription}>
                Draw a digit on the 380×380 canvas or select a canonical preset. 
                Images are automatically centered by center-of-mass and normalized before streaming to the Verilog hardware simulation.
              </p>
            </div>
            <DashboardTabs
              onPredictV2={predictV2}
              onPredictV1={predictV1}
              onPredictCompare={predictCompare}
            />
          </section>
        )}

        {/* TAB 2: Gate-Level Digital Logic Circuit Schematics */}
        {activeTab === 'circuit' && (
          <section className={styles.activeTabContent}>
            <UniversalCircuitDiagram />
          </section>
        )}

        {/* TAB 3: Finite State Machine (FSM) Visualizer */}
        {activeTab === 'fsm' && (
          <section className={styles.activeTabContent}>
            <FsmVisualizer />
          </section>
        )}

        {/* TAB 4: Literature Survey & Architecture Comparison (V1 vs V2) */}
        {activeTab === 'comparison' && (
          <section className={styles.activeTabContent}>
            <V1V2Comparison />
          </section>
        )}

        {/* TAB 5: Verilog HDL Code Explorer */}
        {activeTab === 'verilog' && (
          <section className={styles.activeTabContent}>
            <VerilogCodeBrowser />
          </section>
        )}

        {/* TAB 6: Output & Waveform Timing Analysis */}
        {activeTab === 'waveforms' && (
          <section className={styles.activeTabContent}>
            <WaveformsSection />
          </section>
        )}

        {/* TAB 7: Full In-App PES University Project Report & Documentation */}
        {activeTab === 'docs' && (
          <section className={styles.activeTabContent}>
            <ProjectReportSection />
          </section>
        )}

        {/* OPTIONAL VIEW: Continuous Full Report View (All sections stacked) */}
        {activeTab === 'full_report' && (
          <div className={styles.fullReportStack}>
            <section className={styles.sectionCard}><ProblemStatementSection /></section>
            <section className={styles.sectionCard}><UniversalCircuitDiagram /></section>
            <section className={styles.sectionCard}><FsmVisualizer /></section>
            <section className={styles.sectionCard}><V1V2Comparison /></section>
            <section className={styles.sectionCard}><VerilogCodeBrowser /></section>
            <section className={styles.sectionCard}>
              <DashboardTabs
                onPredictV2={predictV2}
                onPredictV1={predictV1}
                onPredictCompare={predictCompare}
              />
            </section>
            <section className={styles.sectionCard}><WaveformsSection /></section>
            <section className={styles.sectionCard}><ProjectReportSection /></section>
            <section className={styles.sectionCard}><ReferencesSection /></section>
          </div>
        )}
      </main>

      {/* Academic Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerLeft}>
            <strong>PES UNIVERSITY &bull; RING ROAD CAMPUS</strong>
            <span>Department of Computer Science &amp; Engineering &bull; UE25CS251A DLCD Laboratory (2026)</span>
          </div>
          <div className={styles.footerRight}>
            <span>End Semester Assessment (ESA) &bull; Q7.8 CNN Hardware Accelerator</span>
          </div>
        </div>
      </footer>

      {/* Floating Scroll To Top Button */}
      {showScrollTop && (
        <button className={styles.scrollTopBtn} onClick={scrollToTop} title="Scroll to Top">
          <ChevronUp size={20} />
        </button>
      )}
    </div>
  );
};

export default App;
