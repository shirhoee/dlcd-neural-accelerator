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
