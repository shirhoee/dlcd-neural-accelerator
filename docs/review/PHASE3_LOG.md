# Phase 3 (Final Corrections) Engineering Log

**Project:** DLCD Neural Network Accelerator (UE25CS251A End Semester Assessment)  
**Branch:** `phase2-fixes`  
**Starting Tag:** `pre-phase3`  
**Date:** November 15, 2026  

---

## Log Entries

### Entry 0: Baseline & Safety Verification
- Checked working tree clean.
- Created git tag `pre-phase3`.
- Established Phase 3 rules:
  - Justify all changes with direct RTL/log reads.
  - Re-run affected testbenches after each fix and verify numbers against `facts.json`.
  - Commit after each numbered task.
  - No silent number changes.

---

### Entry 1: Task 1 - Reconciled 9,116 vs 9,117 Latency Definition
- **Exact Measurement Analysis:**
  - Start Cycle (S): Cycle 0 (at timestamp 35 ns, where `start` is asserted).
  - Sample / Latch Cycle: Cycle 1 (at timestamp 45 ns, where `start` is sampled into `run_latch` and deasserted).
  - Absolute Done Cycle (D): Cycle 9,117 (at timestamp 91,175 ns, where `done` rises).
  - Testbench Reporting Logic: `tb_submission.v:79-82` while loop increments `latency_cycles` on every subsequent posedge while `!done`, counting from Cycle 1 to Cycle 9,117 $\rightarrow D - 1 = 9,116$ cycles.
- **Single Canonical Definition Added to `facts.json`:**
  ```json
  "latency_definition": {
      "start_cycle": 0,
      "done_cycle": 9117,
      "reported_latency": 9116,
      "note": "Cycle 0 is the clock posedge where tb_submission asserts start. At Cycle 1, start is sampled into run_latch and deasserted. The testbench while(!done) loop increments latency_cycles on each subsequent posedge until done rises at absolute Cycle 9,117. Reported inference latency = 9,117 - 1 = 9,116 clock cycles (91.16 us at 100 MHz)."
  }
  ```
- **Documentation Alignment:**
  - Replaced all occurrences where 9,117 was used as a latency claim with 9,116 in `README.md`.
  - Where 9,117 is mentioned, explicitly labeled it as "absolute done cycle (not latency)".
- **Test Evidence:**
  - Re-ran `tb_submission.v`: 10/10 passed with `Latency: 9116 cycles`.
  - Re-ran `test_10.py`: 10/10 passed with `Cycles Mean: 9116.0`.
