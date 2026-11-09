import React, { useState, useEffect } from 'react';
import styles from './FsmVisualizer.module.css';
import { FSM_DEFINITIONS } from '../../data/projectData';
import { Play, Pause, RotateCcw, StepForward, Activity, ArrowRight } from 'lucide-react';

export const FsmVisualizer: React.FC = () => {
  const [selectedFsmId, setSelectedFsmId] = useState<'conv_pe_fsm' | 'mlp_head_fsm'>('conv_pe_fsm');
  const [activeStateIndex, setActiveStateIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const currentFsm = FSM_DEFINITIONS.find((f) => f.id === selectedFsmId)!;

  const handleSelectFsm = (id: 'conv_pe_fsm' | 'mlp_head_fsm') => {
    setSelectedFsmId(id);
    setActiveStateIndex(0);
    setIsRunning(false);
  };

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isRunning) {
      timer = setInterval(() => {
        setActiveStateIndex((prev) => (prev + 1) % currentFsm.states.length);
      }, 1200);
    }
    return () => clearInterval(timer);
  }, [isRunning, currentFsm.states.length]);

  const handleStep = () => {
    setIsRunning(false);
    setActiveStateIndex((prev) => (prev + 1) % currentFsm.states.length);
  };

  const handleReset = () => {
    setIsRunning(false);
    setActiveStateIndex(0);
  };

  return (
    <section className={styles.section} id="fsm">
      <div className={styles.sectionHeader}>
        <div>
          <div className={styles.categoryBadge}>SECTION 3 • FINITE STATE CONTROL</div>
          <h2 className={styles.sectionTitle}>Interactive Finite State Machine (FSM) Visualizer</h2>
          <p className={styles.sectionDesc}>
            Hardware state transitions governing sequential memory streaming and time-multiplexed matrix multiplication.
            Click <span className={styles.highlight}>Step Clock</span> to step the control unit across synchronous clock edges.
          </p>
        </div>

        {/* FSM Selector Tabs */}
        <div className={styles.fsmTabs}>
          {FSM_DEFINITIONS.map((fsm) => (
            <button
              key={fsm.id}
              className={`${styles.fsmTabBtn} ${selectedFsmId === fsm.id ? styles.activeFsmTab : ''}`}
              onClick={() => handleSelectFsm(fsm.id as 'conv_pe_fsm' | 'mlp_head_fsm')}
            >
              {fsm.module} Control FSM
            </button>
          ))}
        </div>
      </div>

      {/* Main FSM Visualizer Card */}
      <div className={styles.fsmCard}>
        <div className={styles.fsmCardHeader}>
          <div>
            <h3 className={styles.fsmTitle}>{currentFsm.title}</h3>
            <span className={styles.cycleBadge}>Cycle Budget: {currentFsm.cycleBudget}</span>
          </div>

          {/* Stepper Controls */}
          <div className={styles.controls}>
            <button
              className={styles.ctrlBtn}
              onClick={() => setIsRunning(!isRunning)}
              title={isRunning ? "Pause" : "Auto Clock"}
            >
              {isRunning ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Auto Clock</>}
            </button>
            <button className={styles.ctrlBtn} onClick={handleStep} title="Step Next Clock Cycle">
              <StepForward size={14} /> Step Clock
            </button>
            <button className={styles.ctrlBtn} onClick={handleReset} title="Synchronous Reset">
              <RotateCcw size={14} /> Reset
            </button>
          </div>
        </div>

        {/* Graphical State Node Diagram */}
        <div className={styles.diagramContainer}>
          <div className={styles.statesTrack}>
            {currentFsm.states.map((st, idx) => {
              const isActive = idx === activeStateIndex;
              return (
                <React.Fragment key={st.name}>
                  <div
                    className={`${styles.stateNode} ${isActive ? styles.activeNode : ''} ${st.isInitial ? styles.initialNode : ''}`}
                    onClick={() => { setIsRunning(false); setActiveStateIndex(idx); }}
                  >
                    <div className={styles.nodeHeader}>
                      <span className={styles.stateNum}>S{idx}</span>
                      {st.isInitial && <span className={styles.initTag}>RESET</span>}
                      {st.isFinal && <span className={styles.finalTag}>VALID</span>}
                    </div>
                    <div className={styles.stateName}>{st.name}</div>
                    <p className={styles.stateDesc}>{st.desc}</p>
                    {isActive && (
                      <div className={styles.activeGlowPulse}>
                        <Activity size={12} className={styles.pulseIcon} /> CURRENT STATE
                      </div>
                    )}
                  </div>

                  {idx < currentFsm.states.length - 1 && (
                    <div className={`${styles.transitionLine} ${isActive ? styles.activeTransition : ''}`}>
                      <span className={styles.transCond}>clk ↑</span>
                      <ArrowRight size={20} className={styles.transArrow} />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* State Transition Table */}
        <div className={styles.transitionTableContainer}>
          <h4 className={styles.tableHeading}>Formal State Transition Contract</h4>
          <table className={styles.transTable}>
            <thead>
              <tr>
                <th>Source State</th>
                <th>Target State</th>
                <th>Guarding Condition</th>
                <th>Hardware Action / Signal Output</th>
              </tr>
            </thead>
            <tbody>
              {currentFsm.transitions.map((trans, i) => (
                <tr key={i}>
                  <td className={styles.monoCell}>{trans.from}</td>
                  <td className={styles.monoCell}>{trans.to}</td>
                  <td className={styles.condCell}>{trans.condition}</td>
                  <td className={styles.actionCell}>{trans.action || 'State register advance'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
