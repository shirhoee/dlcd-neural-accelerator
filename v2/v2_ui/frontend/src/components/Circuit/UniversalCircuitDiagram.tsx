import React, { useState } from 'react';
import styles from './UniversalCircuitDiagram.module.css';
import { CIRCUIT_MODULES } from '../../data/projectData';
import { CircuitModule } from '../../types/api';
import { ModuleInspectorModal } from './ModuleInspectorModal';
import { ArrowRight } from 'lucide-react';

export const UniversalCircuitDiagram: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<CircuitModule | null>(null);

  const stages = [
    {
      stageNum: 1,
      title: "Input & Conv1 Frontend",
      desc: "3×3 Spatial Line Buffer & 4-Channel Convolution Array",
      modules: ["window_gen", "conv_pe", "mac_q7_8", "conv1_array"]
    },
    {
      stageNum: 2,
      title: "MaxPool1 Subsystem",
      desc: "2×2 Spatial Router & Fused ReLU Downsampling",
      modules: ["maxpool_pe", "relu_q7_8"]
    },
    {
      stageNum: 3,
      title: "Conv2 & MaxPool2 Pipeline",
      desc: "Multi-Channel Parallel Adder Trees & 8-Channel Reduction",
      modules: ["conv2_array"]
    },
    {
      stageNum: 4,
      title: "Systolic MLP Head",
      desc: "Time-Multiplexed 16×16 Matrix Core (200→64→32→10)",
      modules: ["mlp_head", "systolic_array"]
    },
    {
      stageNum: 5,
      title: "Argmax & Output",
      desc: "Pipelined 10-Way Signed Binary Comparator Tree",
      modules: ["argmax", "v2_top"]
    }
  ];

  return (
    <section className={styles.section} id="circuit">
      <div className={styles.sectionHeader}>
        <div>
          <div className={styles.categoryBadge}>SECTION 2 • HARDWARE ARCHITECTURE</div>
          <h2 className={styles.sectionTitle}>Interactive Universal RTL Datapath Circuit Diagram</h2>
          <p className={styles.sectionDesc}>
            Complete gate-level and functional schematic of the CNN accelerator. 
            <span className={styles.highlight}> Click on any functional block</span> to inspect its internal gate schematic, pinout contract, cycle budget, and Verilog HDL source.
          </p>
        </div>
        <div className={styles.legend}>
          <div className={styles.legendItem}><span className={`${styles.legendDot} ${styles.dotInput}`}></span> Input / Line Buffer</div>
          <div className={styles.legendItem}><span className={`${styles.legendDot} ${styles.dotConv}`}></span> Convolution Array</div>
          <div className={styles.legendItem}><span className={`${styles.legendDot} ${styles.dotPool}`}></span> Fused Pooling</div>
          <div className={styles.legendItem}><span className={`${styles.legendDot} ${styles.dotSystolic}`}></span> Systolic Array</div>
        </div>
      </div>

      {/* Interactive Datapath Canvas / Pipeline Flow */}
      <div className={styles.datapathContainer}>
        <div className={styles.flowStages}>
          {stages.map((stg, stgIdx) => (
            <React.Fragment key={stg.stageNum}>
              <div className={styles.stageCard}>
                <div className={styles.stageHeader}>
                  <span className={styles.stageBadge}>STAGE {stg.stageNum}</span>
                  <h4 className={styles.stageTitle}>{stg.title}</h4>
                  <p className={styles.stageDesc}>{stg.desc}</p>
                </div>

                <div className={styles.moduleList}>
                  {stg.modules.map((modId) => {
                    const mod = CIRCUIT_MODULES.find((m) => m.id === modId);
                    if (!mod) return null;

                    return (
                      <div
                        key={mod.id}
                        className={`${styles.moduleCard} ${styles['cat_' + mod.category]}`}
                        onClick={() => setSelectedModule(mod)}
                        title="Click to inspect module details"
                      >
                        <div className={styles.modTopRow}>
                          <span className={styles.modName}>{mod.name}.v</span>
                          <span className={styles.viewBadge}>INSPECT 🔍</span>
                        </div>
                        <p className={styles.modDesc}>{mod.description}</p>
                        <div className={styles.modFooter}>
                          <span className={styles.latencyTag}>⏱️ {mod.latencyCycles}</span>
                          <span className={styles.portCount}>{mod.ports.length} Ports</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {stgIdx < stages.length - 1 && (
                <div className={styles.flowConnector}>
                  <div className={styles.pulseWire}></div>
                  <ArrowRight className={styles.flowArrow} size={24} />
                  <span className={styles.busLabel}>Q7.8 Bus</span>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Module Inspector Modal */}
      {selectedModule && (
        <ModuleInspectorModal
          module={selectedModule}
          onClose={() => setSelectedModule(null)}
        />
      )}
    </section>
  );
};
