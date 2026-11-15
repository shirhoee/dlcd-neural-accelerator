# Phase 2 Engineering & Remediation Log

**Project:** DLCD Neural Network Accelerator (UE25CS251A End Semester Assessment)  
**Branch:** `phase2-fixes`  
**Starting Baseline Tag:** `pre-phase2`  
**Date:** November 15, 2026  

---

## Log Entries

### Entry 0: Baseline & Safety Verification
- **Actions:**
  - Verified git status: working tree clean.
  - Created safety tag `pre-phase2`.
  - Created and checked out feature branch `phase2-fixes`.
  - Confirmed global invariants: No behavioral RTL modifications allowed; all edits strictly limited to compiler directives, declarations, toolchain portability, and documentation reconciliation.

---

### Entry 1: Task 2 Safe RTL, Testbench, and Toolchain Updates
- **2.1 Timescale Directives:** Added `` `timescale 1ns / 1ps `` to `mac_q7_8.v` and `relu_q7_8.v` (V2 copies only; V1 untouched).
- **2.2 Default Nettype Directives (18 of 18 Active RTL Modules):**
  - Added `` `default_nettype none `` (and `` `default_nettype wire `` at end of module) to all 18 active RTL files:
    1. `mac_q7_8.v`
    2. `relu_q7_8.v`
    3. `maxpool_pe.v`
    4. `pool_window_gen.v`
    5. `pool2_window_gen.v`
    6. `window_gen.v`
    7. `conv2_window_gen.v`
    8. `conv_pe.v`
    9. `conv2_pe.v`
    10. `systolic_pe.v`
    11. `systolic_array.v`
    12. `argmax.v`
    13. `maxpool_array.v`
    14. `maxpool2_array.v`
    15. `conv1_array.v`
    16. `conv2_array.v`
    17. `mlp_head.v`
    18. `v2_top.v`
  - Zero implicit nets were inferred; design compiled cleanly with `iverilog -g2001 -Wall`.
  - Regression re-run: `tb_submission` passed 10/10 with 100% accuracy and 9,116 cycles per test.
- **2.3 Testbench Instrumentation (`tb_v2_top_fixed.v`):**
  - Added `` `ifndef TEST_IMAGE_FILE `define TEST_IMAGE_FILE "test_image_tmp.txt" `endif `` fallback define.
  - Corrected `dense_start` / `dense_end` timing to trigger when `dense_inst.state == 1` (`LOAD_WEIGHT`) and end on `d_valid`, measuring true dense execution of 2,977 cycles.
  - Verified `test_10.py` regression: 10/10 PASS, Mean Cycles = 9,116.0, Dense Cycles = 2,977.0.
  - Verified `tb_mlp_head`: ALL TESTS PASSED (10/10 matched in 2,978 cycles).
- **2.4 Toolchain Portability:**
  - Replaced hardcoded `C:\iverilog\bin` paths with `shutil.which` + fallback in `harness.py`, `test_10.py`, `v2/run_all_tests.py`, and `v1/batch_regression_m15.py`.
- **2.5 Canonical Test Runner (`run_all_tests.bat`):**
  - Clarified batch file inventory: identified that `run_all_tests.bat` previously only existed inside `v2/verilog_src/`.
  - Created canonical root-level `run_all_tests.bat` with `where iverilog` dynamic detection, explicit dependency file lists, dedicated build/log redirection to `docs/review/`, and precise regex/string pass detection.
  - Executed test suite: **13/13 PASSED (0 FAILED)**.
- **2.6 Git Ignore Rules:**
  - Added `build/` and `docs/review/build/*.vvp` to `.gitignore`.

---

### Entry 2: Task 3 GTKWave Setup & Screenshot Tooling
- **3.1 Interactive Screenshot Runner (`docs/review/run_for_screenshots.bat`):**
  - Re-authored batch runner with `mode con cols=100 lines=45`, clear section headers, and interactive pauses across all 5 screenshot steps.
- **3.2 GTKWave Save Files (`docs/review/wave/`):**
  - Created 4 specialized GTKWave `.gtkw` files:
    1. `wave_full.gtkw`: Full 9,116-cycle inference trace (clock, reset, start, pixel_addr, stage valids, prediction, done).
    2. `wave_conv1_mac.gtkw`: Conv1 line buffer valid, tap counter (0..8), accumulator reset, and PE valid strobe.
    3. `wave_mlp_fsm.gtkw`: Systolic head FSM state transitions (IDLE $\rightarrow$ LOAD_WEIGHT $\rightarrow$ FEED_INPUT $\rightarrow$ DRAIN $\rightarrow$ STORE_OUTPUT $\rightarrow$ DONE), layer counter, tile indices, and timer.
    4. `wave_end.gtkw`: Dense valid assertion, tournament argmax comparator, and final `done` pulse.
  - Authored `docs/review/build/check_gtkw.py`: validated that all 21 signals referenced across the 4 `.gtkw` files exist in the `wave.vcd` symbol table.
- **3.3 Screenshot Guide:**
  - Authored `docs/review/screenshots/README.txt` providing explicit terminal sizing, GTKWave zoom coordinates, signal grouping, and visual expectations for Figures 7.1 through 7.9.

---

### Entry 3: Task 4 Publication Figures (300 DPI)
- **4.1 Script Authoring (`docs/review/build/generate_figures.py`):**
  - Authored high-resolution matplotlib diagram generator rendering 6 publication-quality architectural and FSM diagrams:
    - `fig2_1_v2_top_block_diagram.png`: Pipelined 6-stage top-level interconnect with streaming data widths and memory interfaces.
    - `fig2_2_mac_conv_pe_datapath.png`: mac_q7_8 16x16 fixed-point ALU and conv_pe datapath showing per-step truncation [23:8] and tap counter.
    - `fig2_3_conv2_systolic_pe.png`: conv2_pe 4-channel parallel PE and systolic_pe output-stationary datapath.
    - `fig3_1_conv1_fsm.png`: Conv1 array 3-state FSM (IDLE, INIT, COMPUTE) with counter bounds.
    - `fig3_2_conv2_fsm.png`: Conv2 array 3-state FSM (IDLE, INIT, COMPUTE).
    - `fig3_3_mlp_head_fsm.png`: MLP head 6-state FSM (IDLE, LOAD_WEIGHT, FEED_INPUT, DRAIN, STORE_OUTPUT, DONE) with layer counter (1..3) and tile counts (52, 8, 2).
  - Generated `fig7_4_stage_breakdown.png`: Horizontal bar chart detailing cycle apportioning across the 9,116-cycle budget.
  - Rendered terminal snapshots: `fig7_1_testbench_suite.png` and `fig7_2_regression_10.png` in `docs/review/screenshots/`.

---

### Entry 4: Task 1 Single Source of Truth (`facts.json`) & 10,000-Image Evaluation
- **4.1 Full 10,000-Image Bit-Exact Software Evaluation:**
  - Evaluated all 10,000 MNIST test images via `docs/review/build/eval_emu_10k.py` across PyTorch Float32 and Q7.8 `int_emulator_v2.py`:
    - PyTorch Float32: 9,883 / 10,000 correct = **98.83%**.
    - Q7.8 Fixed-Point Emulator: 9,883 / 10,000 correct = **98.83%**.
    - Float32 vs Q7.8 Disagreements: 12 images out of 10,000 (0.12%).
    - Wrote full confusion matrix: `docs/review/confusion_matrix.csv` and rendered heatmap `docs/review/confusion_matrix.png`.
- **4.2 Full 10,000-Image Parallel Hardware Regression:**
  - Executed `v2/regression/harness.py --workers 16` in background with multi-worker parallelism:
    - Total Images: 10,000
    - Wall Time: 2,208.15 seconds (~36.8 minutes)
    - Hardware RTL Accuracy: **98.83% (9,883 / 10,000)**
    - RTL vs Q7.8 Emulator Mismatches: **EXACTLY 0 (100% bit-exact parity across all 10,000 images)**
    - Mean Cycles: **9,116.0** (Min: 9116, Max: 9116)
- **4.3 Facts Consolidation (`docs/review/build/measure_facts.py`):**
  - Generated `docs/review/facts.json` containing programmatic measurements for cycles, memories, multipliers, latencies, accuracies, and testbench scorecard.

---

### Entry 5: Task 5 Report Overhaul & Table of Contents Synchronization
- **5.1 Report Generator (`docs/review/build/generate_final_report.py`):**
  - Re-authored script reading 100% of data from `facts.json`.
  - Removed all unsynthesized metrics; explicitly clarified that FPGA/ASIC synthesis is future work and all metrics are empirically verified in cycle-accurate RTL simulation and bit-exact software emulation.
  - Replaced ASCII schematics with embedded 300 DPI figures and confusion matrix.
  - Added comparative analysis table with published architectures (Google TPU v1, MIT Eyeriss, Kung Systolic Arrays).
  - Detailed fixed-point arithmetic, per-step truncation `product[23:8]`, natural 2's complement wraparound, and the training Headroom Gate ($|logit| < 128$).
  - Appended 8 formal IEEE bibliographic citations.
- **5.2 Two-Pass Automated TOC Synchronization:**
  - Pass 1: Generated DOCX and compiled to PDF via headless LibreOffice (`C:\Program fFles\LibreOffice\program\soffice.com`).
  - Extracted exact physical page numbers for Headings 1..8 using PyMuPDF (`pymupdf`).
  - Pass 2: Updated Table 0 in DOCX with measured page numbers (4, 6, 9, 12, 14, 33, 41, 46) and recompiled to final PDF.
  - Re-extracted and asserted exact matching between TOC text and heading locations.
  - Generated output:
    - `docs/review/DLCD_Final_Project_Report_UE25CS251A.docx` (and copied to repo root)
    - `docs/review/DLCD_Final_Project_Report_UE25CS251A.pdf` (46 pages)

---

### Entry 6: Task 6 Repository Documentation Refresh
- **6.1 Root README.md:** Replaced with comprehensive, publication-ready overview documenting 9,116 cycles, 292 multipliers, 98.83% accuracy, 13/13 passing testbenches, and 10,000-image hardware regression.
- **6.2 CURRENT_STATE.md:** Updated repository audit status, active module table, memory footprint (16,623 words), and execution breakdown.
- **6.3 dlcd_presentation.md:** Synchronized presentation slide metrics (3x3 kernels, 9,116 cycles, 292 multipliers, 98.83% accuracy, and time-multiplexed area savings).
- **6.4 Module Specification:** Verified that `docs/mini_project_submission/module_specification.md` accurately describes the 9-tap counter and modular architecture of `conv_pe.v`.

---

### Entry 7: Task 7 Automated Quality Assurance Gate
- **7.1 Script Execution (`docs/review/build/check_report.py`):**
  - Verified 0 forbidden strings across the entire 46-page PDF report.
  - Verified 9,116 headline latency assertion.
  - Verified 2,978 / 2,977 MLP head cycle metrics.
  - Verified 292 total V2 multiplier count (4 in Conv1 + 32 in Conv2 + 256 in Systolic Head).
  - Verified stage table rows sum exactly to 9,116 cycles.
  - Verified Table of Contents page synchronization against physical PDF pages.
  - Verified existence of all 7 publication figures at 300 DPI.
  - Verified testbench suite pass rate: 13/13 passed (100%).
  - Verified full 10,000-image hardware regression status: complete with 0 mismatches.
- **Result:** `>> ALL QUALITY ASSURANCE CHECKS PASSED SUCCESSFULLY! <<` (Exit code 0).

---

## Residual Risks & Operational Notes
1. **Hardware Reset Requirement:** `v2_top.v` uses an asynchronous `run_latch` that remains high after inference completes until `reset` is pulsed. Between consecutive inferences, pulse `reset` high for at least 1 clock cycle.
2. **Toolchain Location:** On this machine, LibreOffice is located at `C:\Program fFles\LibreOffice\program\soffice.com` (note "Program fFles" directory naming). All scripts use dynamic fallback detection.
3. **Submission Readiness:** Both the DOCX report and 46-page PDF report are fully formatted, synchronized, and ready for submission.
