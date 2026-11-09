import React, { useState } from 'react';
import styles from './ModuleInspectorModal.module.css';
import { CircuitModule } from '../../types/api';
import { GateLevelSchematic } from './GateLevelSchematic';
import { X, Copy, Check, Cpu, Clock, Layers } from 'lucide-react';

interface ModuleInspectorModalProps {
  module: CircuitModule;
  onClose: () => void;
}

export const ModuleInspectorModal: React.FC<ModuleInspectorModalProps> = ({ module, onClose }) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'schematic' | 'ports' | 'code'>('schematic');

  const handleCopy = () => {
    navigator.clipboard.writeText(module.verilogSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <div className={styles.headerLeft}>
            <div className={styles.titleRow}>
              <span className={styles.modBadge}>{module.category.toUpperCase()} MODULE</span>
              <h3 className={styles.modTitle}>{module.name}.v</h3>
            </div>
            <p className={styles.modDesc}>{module.description}</p>
          </div>
          <button className={styles.closeBtn} onClick={onClose} title="Close Inspector">
            <X size={20} />
          </button>
        </div>

        {/* Quick Specs Strip */}
        <div className={styles.specsStrip}>
          <div className={styles.specItem}>
            <Clock size={16} className={styles.specIcon} />
            <div>
              <span className={styles.specLabel}>Cycle Latency</span>
              <span className={styles.specVal}>{module.latencyCycles}</span>
            </div>
          </div>
          <div className={styles.specItem}>
            <Cpu size={16} className={styles.specIcon} />
            <div>
              <span className={styles.specLabel}>Arithmetic Format</span>
              <span className={styles.specVal}>{module.arithmeticType}</span>
            </div>
          </div>
          <div className={styles.specItem}>
            <Layers size={16} className={styles.specIcon} />
            <div>
              <span className={styles.specLabel}>Source File</span>
              <span className={styles.specVal}>v2/verilog_src/{module.verilogFile}</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className={styles.tabRow}>
          <button
            className={`${styles.tabBtn} ${activeTab === 'schematic' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('schematic')}
          >
            Gate-Level RTL Architecture
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'ports' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('ports')}
          >
            Interface Signal Contract ({module.ports.length} Ports)
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'code' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('code')}
          >
            Verilog HDL Source
          </button>
        </div>

        {/* Body Content */}
        <div className={styles.modalBody}>
          {activeTab === 'schematic' && (
            <div className={styles.schematicTab}>
              <h4 className={styles.subHeading}>Vector Logic Gate &amp; Register Schematic</h4>
              <GateLevelSchematic moduleId={module.id} />

              <h4 className={styles.subHeading} style={{ marginTop: '1.25rem' }}>Datapath Building Blocks</h4>
              <div className={styles.blocksList}>
                {module.schematicSummary.map((item, idx) => (
                  <div key={idx} className={styles.blockCard}>
                    <span className={styles.blockIdx}>0{idx + 1}</span>
                    <span className={styles.blockText}>{item}</span>
                  </div>
                ))}
              </div>

              {module.fsmName && (
                <div className={styles.fsmBanner}>
                  <div className={styles.fsmInfo}>
                    <strong>Finite State Machine Attached:</strong> This module contains synchronous state transition logic.
                  </div>
                  <a href="#fsm" className={styles.fsmLink} onClick={onClose}>
                    Jump to FSM State Machine Section →
                  </a>
                </div>
              )}
            </div>
          )}

          {activeTab === 'ports' && (
            <div className={styles.portsTab}>
              <table className={styles.portTable}>
                <thead>
                  <tr>
                    <th>Signal Name</th>
                    <th>Direction</th>
                    <th>Bit-Width</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {module.ports.map((port) => (
                    <tr key={port.name}>
                      <td className={styles.portName}>{port.name}</td>
                      <td>
                        <span className={`${styles.dirBadge} ${port.direction === 'input' ? styles.dirIn : styles.dirOut}`}>
                          {port.direction.toUpperCase()}
                        </span>
                      </td>
                      <td className={styles.portWidth}>{port.width}</td>
                      <td className={styles.portDesc}>{port.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'code' && (
            <div className={styles.codeTab}>
              <div className={styles.codeTopBar}>
                <span className={styles.codeLang}>Verilog-2001 (IEEE 1364-2001)</span>
                <button className={styles.copyBtn} onClick={handleCopy}>
                  {copied ? <><Check size={14} /> Copied!</> : <><Copy size={14} /> Copy Source</>}
                </button>
              </div>
              <pre className={styles.codeBlock}>
                <code>{module.verilogSnippet}</code>
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
