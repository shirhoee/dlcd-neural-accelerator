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

### Entry 2: Task 2 - MLP Head 2,977 vs 2,978 Cycles Reconciliation
- **Exact Root Cause:**
  - In `tb_mlp_head.v:103-106`, cycle counting begins upon `valid_in` deassertion while `mlp_head` is still in state `IDLE` (0). It counts the 1-cycle `IDLE -> LOAD_WEIGHT` transition + 2,976 tile compute cycles (62 tiles × 48 cycles) + 1-cycle `DONE` state transition before `valid_out` rises, yielding exactly **2,978 cycles**.
  - In integrated `v2_top` simulation (`tb_v2_top_fixed.v:217`), `dense_start` triggers when `dense_inst.state == 1` (`LOAD_WEIGHT`) on Cycle 6,137. It measures from the first active `LOAD_WEIGHT` cycle until `d_valid` assertion on Cycle 9,114, yielding exactly $9,114 - 6,137 = \mathbf{2,977\text{ cycles}}$ (omitting the initial 1-cycle IDLE entry transition).
- **Facts & Report Updates:**
  - Added `mlp_head_cycle_note` to `measure_facts.py` and `facts.json`.
  - Added exact explanatory paragraph into `generate_final_report.py` (Section 3.3).
  - Confirmed test output unchanged: `tb_mlp_head` passes with 2,978 cycles; `test_10.py` measures 2,977.0 dense cycles.

### Entry 3: Task 3 - 1-Cycle Front-End Latch Stage Justification
- **Hardware Mechanism Confirmation:**
  - In `v2_top.v:16-25`, `run_latch` is cleared during reset.
  - While `run_latch == 0`, `internal_reset = reset | ~run_latch` is held high.
  - When `start` is pulsed high by the testbench at Cycle 0 (35 ns), `run_latch <= 1'b1` is scheduled at the 35 ns posedge.
  - During Cycle 0 (35 ns to 45 ns), `conv1_inst` and all downstream logic remain in reset.
  - At Cycle 1 (45 ns posedge), `internal_reset` is now low, releasing `conv1_inst` to begin active execution (`init_cnt <= init_cnt + 1`).
  - Thus, this 1-cycle latency is a physical register delay caused by `run_latch` (`v2_top.v:16-23`) and `internal_reset` (`v2_top.v:25`).
- **Documentation Updates:**
  - Updated stage row description across `measure_facts.py`, `facts.json`, `README.md`, and `CURRENT_STATE.md` to explicitly cite `run_latch` (`v2_top.v:16-23`) and `internal_reset` (`v2_top.v:25`).

---

### Entry 4: Task 4 - Fix Throughput Claims & Formulas
- **V2 Throughput Derivation & Separation:**
  - `tb_submission.v:62-72` executes a 4-cycle reset-to-start sequence: 3 cycles of synchronous reset assertion (`reset <= 1'b1`) followed by 1 idle cycle before asserting `start <= 1'b1`.
  - Theoretical throughput (hypothetical continuous back-to-back pipelining without reset overhead): $100\text{ MHz} / 9,116\text{ cycles} = \mathbf{10,969.7\text{ FPS}}$.
  - Demonstrated throughput (measured rate including 4-cycle reset sequence): $100\text{ MHz} / (9,116 + 4)\text{ cycles} = 100\text{ MHz} / 9,120\text{ cycles} = \mathbf{10,964.9\text{ FPS}}$.
- **V1 Throughput Derivation & Separation:**
  - V1 inference compute: 159 cycles $\rightarrow 100\text{ MHz} / 159 = \mathbf{628,930.8\text{ FPS}}$ (theoretical pipelined).
  - V1 from reset including 100-cycle feature preload (100 pixels @ 1 pixel/cycle via `pixel_in`): $100\text{ MHz} / (100 + 159) = 100\text{ MHz} / 259 = \mathbf{386,100.4\text{ FPS}}$.
- **Updates Applied:**
  - `docs/review/build/measure_facts.py` and `docs/review/facts.json`: added structured `throughput` object and explicit metrics (`v2_throughput_theoretical_fps`, `v2_throughput_demonstrated_fps`, `v1_throughput_inference_only_fps`, `v1_throughput_from_reset_fps`).
  - `README.md`, `CURRENT_STATE.md`, `dlcd_presentation.md`, and `generate_final_report.py`: updated throughput tables and text to report both theoretical and demonstrated numbers with clear derivations.
- **Verification:**
  - Re-generated `facts.json` via `measure_facts.py`.
  - Confirmed `generate_final_report.py` at root and in `docs/review/build/` are synchronized.

---

### Entry 5: Task 5 - Fix Overstated Host CPU Claims & Verify FPU Absence
- **Overstated Claim Resolution:**
  - Replaced all occurrences of "zero host CPU intervention" and "zero host processor intervention" across `README.md`, `dlcd_presentation.md`, and `generate_final_report.py` (both root and `docs/review/build/`).
  - Replaced with verifiably accurate phrasing: "the RTL datapath performs inference with no arithmetic or control involvement from a host CPU during the 9,116-cycle compute window; input pixels are requested and supplied externally via `pixel_addr`/`pixel_in`, and an external host process (such as the FastAPI service in the interactive UI) streams pixel memory and reads the final classification result."
- **FPU Absence Hardware Verification:**
  - Checked all active Verilog modules in `v2/verilog_src/` using regex pattern `float|real|fpu`.
  - Result: 0 matches found across all modules. Confirmed zero floating-point units or real-number operations exist in the RTL; all datapath calculations execute using pure Q7.8 signed fixed-point integer arithmetic.
