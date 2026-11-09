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
import { ReferencesSection } from './components/Sections/ReferencesSection';
import { usePredict } from './hooks/usePredict';
import { 
  Target, 
  GitFork, 
  Workflow, 
  GitCompare, 
  FileCode, 
  PlayCircle, 
  Activity, 
  BookOpen, 
  ChevronUp 
} from 'lucide-react';

export const App: React.FC = () => {
  const { predictV2, predictV1, predictCompare } = usePredict();
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 400) {
        setShowScrollTop(true);
      } else {
        setShowScrollTop(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navItems = [
    { id: 'section-1', label: '1. Problem Statement', icon: Target },
    { id: 'section-2', label: '2. Circuit Diagram', icon: GitFork },
    { id: 'section-3', label: '3. FSM Machines', icon: Workflow },
    { id: 'section-4', label: '4. Literature Survey', icon: GitCompare },
    { id: 'section-5', label: '5. Verilog Code', icon: FileCode },
    { id: 'section-6', label: '6. Hardware Inference', icon: PlayCircle },
    { id: 'section-7', label: '7. Output & Waveforms', icon: Activity },
    { id: 'section-8', label: '8. References', icon: BookOpen },
  ];

  const handleNavClick = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const yOffset = -70; // offset for sticky nav
      const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  return (
    <div className={styles.appContainer}>
      {/* PES University & Team Member Header */}
      <header className={styles.headerWrapper}>
        <TeamHeader />
      </header>

      {/* Sticky Quick-Jump Navigation Bar */}
      <nav className={styles.stickyNav}>
        <div className={styles.navInner}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={styles.navBtn}
                onClick={() => handleNavClick(item.id)}
              >
                <Icon size={14} className={styles.navIcon} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content Body */}
      <main className={styles.mainContent}>
        {/* Section 1: Problem Statement */}
        <section id="section-1" className={styles.sectionCard}>
          <ProblemStatementSection />
        </section>

        {/* Section 2: Universal Circuit Diagram with Clickable Drill-Down Modals */}
        <section id="section-2" className={styles.sectionCard}>
          <UniversalCircuitDiagram />
        </section>

        {/* Section 3: Interactive Finite State Machine (FSM) Visualizer */}
        <section id="section-3" className={styles.sectionCard}>
          <FsmVisualizer />
        </section>

        {/* Section 4: Literature Survey & Architecture Comparison (V1 vs V2) */}
        <section id="section-4" className={styles.sectionCard}>
          <V1V2Comparison />
        </section>

        {/* Section 5: Main Verilog Code Browser */}
        <section id="section-5" className={styles.sectionCard}>
          <VerilogCodeBrowser />
        </section>

        {/* Section 6: Hardware Inference Dashboards (V2 Studio, V1 Baseline, Dual Inference) */}
        <section id="section-6" className={styles.sectionCard}>
          <div className={styles.sectionIntro}>
            <span className={styles.sectionTag}>SECTION 6 &bull; INTERACTIVE SYSTEM</span>
            <h2 className={styles.sectionHeading}>Hardware Inference Dashboards</h2>
            <p className={styles.sectionDescription}>
              Select between the primary 6-layer CNN accelerator, legacy V1 baseline MLP studio, or simultaneous dual co-inference to test handwritten digits live on Q7.8 arithmetic models.
            </p>
          </div>
          <DashboardTabs
            onPredictV2={predictV2}
            onPredictV1={predictV1}
            onPredictCompare={predictCompare}
          />
        </section>

        {/* Section 7: Output & Waveform Timing Analysis */}
        <section id="section-7" className={styles.sectionCard}>
          <WaveformsSection />
        </section>

        {/* Section 8: References */}
        <section id="section-8" className={styles.sectionCard}>
          <ReferencesSection />
        </section>
      </main>

      {/* Academic Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerLeft}>
            <strong>PES UNIVERSITY &bull; RING ROAD CAMPUS</strong>
            <span>Department of Computer Science &amp; Engineering &bull; UE25CS251A DLCD Laboratory (2026)</span>
          </div>
          <div className={styles.footerRight}>
            <span>End Semester Assessment (ESA) &bull; Verilog-2001 Neural Network Hardware Accelerator</span>
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
