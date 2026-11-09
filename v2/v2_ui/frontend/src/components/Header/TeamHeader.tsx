import React from 'react';
import styles from './TeamHeader.module.css';
import { TEAM_MEMBERS } from '../../data/projectData';
import { Cpu } from 'lucide-react';

interface TeamHeaderProps {
  activeSection?: string;
  onSelectSection?: (sectionId: string) => void;
}

export const TeamHeader: React.FC<TeamHeaderProps> = ({ activeSection, onSelectSection }) => {
  const navItems = [
    { id: 'section-1', label: '1. Problem Statement' },
    { id: 'section-2', label: '2. Circuit Diagram' },
    { id: 'section-3', label: '3. FSM State Machines' },
    { id: 'section-4', label: '4. V1 vs V2 Comparison' },
    { id: 'section-5', label: '5. Verilog HDL Code' },
    { id: 'section-6', label: '6. Live Dashboards' },
    { id: 'section-7', label: '7. Output & Waveforms' },
    { id: 'section-8', label: '8. References' }
  ];

  const handleClick = (id: string) => {
    if (onSelectSection) {
      onSelectSection(id);
    } else {
      const el = document.getElementById(id);
      if (el) {
        const yOffset = -70;
        const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    }
  };

  return (
    <header className={styles.header}>
      {/* Top Academic Banner */}
      <div className={styles.universityBanner}>
        <div className={styles.badgeLeft}>
          <span className={styles.univName}>PES UNIVERSITY</span>
          <span className={styles.divider}>•</span>
          <span className={styles.courseCode}>UE25CS251A DIGITAL LOGIC AND COMPUTER DESIGN LABORATORY</span>
          <span className={styles.divider}>•</span>
          <span className={styles.term}>AUGUST – DECEMBER 2026</span>
        </div>
        <div className={styles.hardwareBadge}>
          <span className={styles.statusDot}></span>
          <span>RTL SIMULATION: ONLINE (Icarus Verilog vvp)</span>
        </div>
      </div>

      {/* Main Title & Team Showcase */}
      <div className={styles.titleRow}>
        <div className={styles.titleBlock}>
          <div className={styles.tagline}>
            <Cpu className={styles.chipIcon} size={18} />
            <span>MINI PROJECT SUBMISSION & HARDWARE SPECIFICATION</span>
          </div>
          <h1 className={styles.projectTitle}>
            DESIGN & IMPLEMENTATION OF A Q7.8 FIXED-POINT CONVOLUTIONAL NEURAL ACCELERATOR
          </h1>
          <p className={styles.subtitle}>
            Bit-exact hardware inference for MNIST digit recognition using spatial line buffers and a time-multiplexed 16×16 systolic array.
          </p>
        </div>

        {/* Team Members Roster */}
        <div className={styles.teamGrid}>
          {TEAM_MEMBERS.map((member) => (
            <div key={member.srn} className={styles.memberCard}>
              <div className={styles.avatar}>{member.avatar}</div>
              <div className={styles.memberInfo}>
                <div className={styles.memberName}>{member.name}</div>
                <div className={styles.memberSrn}>{member.srn}</div>
                <div className={styles.memberRole}>{member.role}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Report Section Navigation Bar */}
      <nav className={styles.navBar}>
        <div className={styles.navList}>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`${styles.navBtn} ${activeSection === item.id ? styles.activeNavBtn : ''}`}
              onClick={() => handleClick(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </nav>
    </header>
  );
};
