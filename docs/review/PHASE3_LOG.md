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

---

### Entry 6: Task 6 - V1 Accuracy Provenance & Reproducibility Clarification
- **Provenance Analysis:**
  - Identified that 93.06% originated as a hardcoded constant in `main.py` / historical milestone log (M15/M17) evaluating on an 8×8 optical digits split zero-padded to 10×10. This number is not directly reproducible from an automated script in the repository.
  - In contrast, `v1/eval_accuracy.py` tests the exported Q7.8 weights against the full 10,000-image MNIST testset downsampled to 10×10, yielding a reproducible accuracy of **95.39%**.
- **Updates Applied:**
  - `docs/review/build/measure_facts.py` and `docs/review/facts.json`:
    - Updated `accuracy_m15_provenance` to `"hardcoded constant in main.py / historical milestone log (M15/M17); not reproducible from a script in this repository"` and set `accuracy_m15_reproducible: false`.
    - Added `accuracy_mnist10k_reproducible: true`.
  - `README.md`, `CURRENT_STATE.md`, `dlcd_presentation.md`, and `generate_final_report.py`:
    - Added asterisk `93.06%*` and explicit footnote clarifying that 93.06% is a historical milestone figure from M15/M17 project logs, while the active reproducible V1 baseline in this repository is 95.39% on MNIST 10×10 (`v1/eval_accuracy.py`).
- **Verification:**
  - Re-ran `measure_facts.py` to regenerate `facts.json`.
  - Confirmed `generate_final_report.py` at root and in `docs/review/build/` are synchronized.

---

### Entry 7: Task 7 - Resolve FSM Contradictions, Multiplier Attribution & Systolic Description
- **FSM State Verification against RTL:**
  - `conv1_array.v:56-61`: verified 6 real states (`ST_INIT=0`, `ST_ADVANCE=1`, `ST_FETCH=2`, `ST_MAC=3`, `ST_WAIT_VALID=4`, `ST_DONE=5`). Replaced stale 3-state descriptions in `CURRENT_STATE.md` and `generate_final_report.py`.
  - `conv2_array.v:52-57`: verified 6 real states (`ST_LOAD=0`, `ST_FETCH=1`, `ST_MAC=2`, `ST_WAIT_VALID=3`, `ST_ADVANCE=4`, `ST_DONE=5`). Added missing 6-state FSM table in `generate_final_report.py`.
  - `mlp_head.v:49`: verified 4 real states (`IDLE=0`, `LOAD_WEIGHT=1`, `COMPUTE=2`, `DONE=3`). Corrected stale 6-state descriptions to the real 4-state architecture.
  - `conv_pe.v`: confirmed absence of FSM; relies solely on synchronous modulo-9 `tap_idx` (0..8) up-counter and control strobes (`load_weight`, `mac_en`, `clr_acc`).
- **Multiplier Attribution Invariant:**
  - Updated `CURRENT_STATE.md` module table so container modules (`v2_top`, `conv1_array`, `conv2_array`, `mlp_head`, `systolic_array`) display `— (container)` to prevent double-counting.
  - Multiplier counts are placed exclusively on leaf modules where the multiplication arithmetic is performed:
    - `conv_pe.v`: 1 multiplier (via `mac_q7_8`) × 4 instances = 4
    - `conv2_pe.v`: 4 multipliers (via `mac_q7_8`) × 8 instances = 32
    - `systolic_pe.v`: 1 multiplier (via `mac_q7_8`) × 256 instances = 256
    - Total Hardware Multipliers = $4 + 32 + 256 = \mathbf{292}$.
- **Systolic Architecture Description Correction:**
  - Replaced all erroneous mentions of "output-stationary" and "diagonal skew registers" in `CURRENT_STATE.md` and `generate_final_report.py`.
  - Formally documented as: "Weight-stationary 2D systolic array; activations are dynamically staggered by the mlp_head controller (via `r = timer - 16`) rather than explicit hardware skew registers."
- **Verification:**
  - Confirmed `generate_figures.py` already renders the real 6 states for Conv1/Conv2, 4 states for MLP head, and weight-stationary PE datapath.
  - Synchronized `docs/review/build/generate_final_report.py` and root `generate_final_report.py`.

---

### Entry 8: Task 8 - Testbench Count Verification & Elimination of Dead layer_relu.v
- **Active Testbench Count Verification:**
  - Inspected `run_all_tests.bat`: verified exactly 13 active testbenches invoked (`tb_conv_pe`, `tb_window_gen`, `tb_pool_window_gen`, `tb_maxpool_pe`, `tb_maxpool_array`, `tb_maxpool2_array`, `tb_conv1_array`, `tb_conv1_maxpool_chain`, `tb_conv2_array`, `tb_mlp_head`, `tb_argmax`, `tb_v2_top_fixed`, `tb_submission`).
  - Confirmed all active documentation and reports state 13 active testbenches.
- **Dead `layer_relu.v` Removal from Compilation Commands:**
  - Removed `layer_relu.v` from:
    - `v2/regression/test_10.py:32`
    - `v2/regression/harness.py:38`
    - `v2/v2_ui/backend/simulator.py:33`
    - `v2/verilog_src/run_all_tests.bat:22,24,25`
    - `docs/review/build/compile_fixed_img.bat:4`
    - `docs/review/build/compile_wave.bat:4`
    - `docs/review/build/_compile_and_run.ps1:21,34`
- **Verification Evidence:**
  - Re-ran `python test_10.py` in `v2/regression`: 10/10 passed (Cycles Mean: 9116.0, 0 mismatches) without compiling `layer_relu.v`.
  - Re-compiled and ran `tb_mlp_head`: passed cleanly with 2,978 cycles (`ALL TESTS PASSED: 10/10 MLP Head output logits matched in 2978 cycles`).

---

### Entry 9: Task 9 - Synchronize Canonical Submission Report at Repo Root
- **Canonical Architecture Decision:**
  - Standardized `DLCD_Final_Project_Report_UE25CS251A.docx` and `DLCD_Final_Project_Report_UE25CS251A.pdf` at the repository root as the canonical submission deliverables. The copies under `docs/review/` serve as synchronized working copies.
- **Generator Modifications:**
  - Updated both `docs/review/build/generate_final_report.py` and root `generate_final_report.py` to copy both the final synchronized DOCX and the final PDF to `REPO_ROOT` upon successful completion.
- **Documentation Updates:**
  - Updated `README.md` directory tree to formally document both root DOCX and PDF as canonical submission files and `docs/review/` copies as working copies.

---

### Entry 10: Task 10 - Full Regression Gate & Final Delivery Verification
- **QA Gate Script Updates (`check_report.py`):**
  - Added programmatic assertions verifying headline latency 9,116 cycles (no bare 9,117 claim).
  - Added verification of MLP head 1-cycle timing explanation (2,978 standalone vs 2,977 integrated).
  - Added verification of normalized theoretical (10,969.7 FPS) and demonstrated (10,964.9 FPS) throughput claims.
  - Added verification of V1 accuracy footnote (93.06%* historical milestone vs 95.39% reproducible baseline).
  - Added verification of real FSM state architectures (Conv1=6 states, Conv2=6 states, MLP head=4 states).
  - Added verification of leaf multiplier breakdown summing to 292 with containers marked non-duplicating.
  - Verified zero forbidden strings across all 46 pages of the generated PDF.
- **Full End-to-End Execution Sequence Pass Evidence:**
  1. `python docs/review/build/measure_facts.py`: exited code 0 (`facts.json` regenerated).
  2. `python docs/review/build/generate_figures.py`: exited code 0 (all 6 architectural/FSM figures rendered at 300 DPI).
  3. `python docs/review/build/generate_final_report.py`: exited code 0 (2-pass TOC synchronization verified bit-exact, canonical DOCX & PDF copied to root).
  4. `run_all_tests.bat --no-pause`: exited code 0 (13/13 testbenches passed).
  5. `python v2/regression/test_10.py`: exited code 0 (10/10 matched, Cycles Mean: 9116.0, 0 mismatches).
  6. `python docs/review/build/check_report.py`: exited code 0 (all 12 QA checks passed).

---

## Final Verification Checklist & Before/After Diff Table

| Investigation Topic | Phase 1/2 Baseline | Phase 3 Canonical Final Value | Verification / Direct Evidence |
| :--- | :--- | :--- | :--- |
| **Inference Latency** | 9,117 cycles (confused latency with done cycle) | **9,116 clock cycles** (91.16 μs at 100 MHz) | `tb_submission.v:63-82`: `start` deasserted Cycle 1, while loop counts until `done` at Cycle 9,117 ($9,117 - 1 = 9,116$). Absolute done cycle is 9,117. |
| **MLP Head Latency** | 2,978 cycles vs 2,977 cycles unexplained | **2,978 standalone vs 2,977 integrated** | Standalone `tb_mlp_head` counts from state `IDLE` upon `valid_in` deassertion (1 cycle IDLE $\rightarrow$ LOAD + 2,976 compute + 1 cycle DONE). Integrated `v2_top` triggers on `dense_inst.state == 1` at Cycle 6,137, measuring to `d_valid` at Cycle 9,114. |
| **Front-End Latch** | 1-cycle latency unattributed | **1-cycle register delay in `run_latch`** | `v2_top.v:16-25`: `internal_reset = reset \| ~run_latch`. `run_latch` registers `start` on Cycle 0 (35 ns), releasing `internal_reset` to low on Cycle 1 (45 ns). |
| **V2 Throughput** | 10,969.7 FPS (continuous) | **10,969.7 FPS (theoretical pipelined)**<br>**10,964.9 FPS (demonstrated)** | Theoretical: $100\text{ MHz} / 9,116 = 10,969.7\text{ FPS}$. Demonstrated: $100\text{ MHz} / (9,116 + 4) = 10,964.9\text{ FPS}$ (includes 4-cycle reset sequence in `tb_submission.v:62-72`). |
| **V1 Throughput** | ~386,100 FPS (burst) | **628,930.8 FPS (pipelined)**<br>**386,100.4 FPS (from reset with preload)** | Pipelined: $100\text{ MHz} / 159 = 628,930.8\text{ FPS}$. From reset with 100-cycle preload (100 pixels @ 1 pixel/cycle): $100\text{ MHz} / 259 = 386,100.4\text{ FPS}$. |
| **Host CPU Claim** | "Zero host CPU intervention" | **Verified bus streaming interface** | Pure hardware execution during 9,116-cycle compute window without host CPU arithmetic/control; host streams pixels via `pixel_addr`/`pixel_in` and reads `done`/`digit_out`. |
| **FPU Check** | Unchecked | **Zero Floating-Point Units (FPUs)** | Checked all 15 active modules in `v2/verilog_src/`; 0 matches for `float\|real\|fpu`. Pure Q7.8 signed integer arithmetic. |
| **V1 Baseline Accuracy**| 93.06% unqualified | **93.06%* (M15 milestone)**<br>**95.39% (reproducible baseline)** | 93.06% is historical milestone from M15/M17 on 8×8 optical digits; active reproducible V1 script `v1/eval_accuracy.py` achieves 95.39% on MNIST 10×10. |
| **Conv1 FSM States** | 3 or 4 states reported | **6 real states (3-bit: 3'd0..3'd5)** | `conv1_array.v:56-61`: `ST_INIT=0`, `ST_ADVANCE=1`, `ST_FETCH=2`, `ST_MAC=3`, `ST_WAIT_VALID=4`, `ST_DONE=5`. |
| **Conv2 FSM States** | 4 states reported | **6 real states (3-bit: 3'd0..3'd5)** | `conv2_array.v:52-57`: `ST_LOAD=0`, `ST_FETCH=1`, `ST_MAC=2`, `ST_WAIT_VALID=3`, `ST_ADVANCE=4`, `ST_DONE=5`. |
| **MLP Head FSM States**| 6 states reported | **4 real states (2-bit: 0..3)** | `mlp_head.v:49`: `IDLE=0`, `LOAD_WEIGHT=1`, `COMPUTE=2`, `DONE=3`. |
| **Conv PE FSM** | Unclear | **No FSM (Modulo-9 counter)** | `conv_pe.v:24`: synchronous `tap_idx` counter (0..8) and combinational control strobes. |
| **Hardware Multipliers**| Container double-counting | **Leaf attribution only = 292 mults** | Containers marked `—`. Leaf multipliers: `conv_pe` (4) + `conv2_pe` (32) + `systolic_pe` (256) = **292 total**. |
| **Systolic PE Model** | "Output-stationary with skew DFFs"| **Weight-stationary (no skew DFFs)** | `systolic_pe.v:17,34`: weights held in `stationary_weight`. Row activation staggering handled dynamically by `mlp_head.v` controller (`r = timer - 16`). |
| **Active Testbenches** | 13 vs 14 ambiguous | **Exactly 13 active testbenches** | `run_all_tests.bat:28-40`: exactly 13 testbenches invoked. Dead `layer_relu.v` eliminated from compilation scripts. |
| **Canonical Report** | Root vs `docs/review/` split | **Root DOCX and PDF canonical** | `DLCD_Final_Project_Report_UE25CS251A.docx` and `.pdf` at repository root are canonical submission files, synchronized with working copies in `docs/review/`. |
