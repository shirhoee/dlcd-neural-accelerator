import React, { useState } from 'react';
import styles from './VerilogCodeBrowser.module.css';
import { CIRCUIT_MODULES } from '../../data/projectData';
import { FileCode, Copy, Check } from 'lucide-react';

export const VerilogCodeBrowser: React.FC = () => {
  const [selectedModId, setSelectedModId] = useState<string>('conv_pe');
  const [copied, setCopied] = useState(false);

  const activeModule = CIRCUIT_MODULES.find((m) => m.id === selectedModId) || CIRCUIT_MODULES[0];

  const handleCopy = () => {
    navigator.clipboard.writeText(activeModule.verilogSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className={styles.section} id="verilog">
      <div className={styles.sectionHeader}>
        <div>
          <div className={styles.categoryBadge}>SECTION 5 • MAIN VERILOG CODE</div>
          <h2 className={styles.sectionTitle}>Synthesizable Verilog HDL Source Browser</h2>
          <p className={styles.sectionDesc}>
            IEEE 1364-2001 compliant register-transfer level hardware modules. Fully verified using Icarus Verilog (`iverilog`) and cycle-accurate GTKWave testbenches.
          </p>
        </div>
      </div>

      <div className={styles.browserContainer}>
        {/* Module Sidebar Tabs */}
        <div className={styles.sidebar}>
          <div className={styles.sidebarTitle}>HARDWARE MODULES</div>
          <div className={styles.tabList}>
            {CIRCUIT_MODULES.map((mod) => (
              <button
                key={mod.id}
                className={`${styles.moduleTab} ${selectedModId === mod.id ? styles.activeModuleTab : ''}`}
                onClick={() => setSelectedModId(mod.id)}
              >
                <FileCode size={14} className={styles.tabIcon} />
                <span>{mod.verilogFile}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Code Display Pane */}
        <div className={styles.codePane}>
          <div className={styles.paneHeader}>
            <div className={styles.paneInfo}>
              <span className={styles.activeFile}>{activeModule.verilogFile}</span>
              <span className={styles.compPill}>IEEE 1364-2001 (Verilog-2001)</span>
              <span className={styles.compPill}>default_nettype none</span>
            </div>
            <button className={styles.copyBtn} onClick={handleCopy}>
              {copied ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy Source</>}
            </button>
          </div>

          <pre className={styles.codeContent}>
            <code>{activeModule.verilogSnippet}</code>
          </pre>

          <div className={styles.paneFooter}>
            <span>Module Role: {activeModule.description}</span>
            <span>Latency: {activeModule.latencyCycles}</span>
          </div>
        </div>
      </div>
    </section>
  );
};
