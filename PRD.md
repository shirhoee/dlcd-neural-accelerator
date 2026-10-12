# PRD.md — Stabilization & Mini Project Submission Requirements Document

**Project:** DLCD Neural Network Accelerator (Hardware V1 & V2)  
**Author:** AI Engineering Assistant  
**Date:** October 2026  
**Status:** Approved for Execution  

---

## 1. Product Overview

### 1.1 Problem Statement
The DLCD Neural Accelerator has successfully reached 98.83% hardware accuracy for CNN-based MNIST digit recognition with zero bit-level mismatches between Verilog RTL and a bit-exact Python Q7.8 integer emulator. However, the codebase has accumulated critical technical debt:
- A monolithic 306-line React component (`App.jsx`) combines canvas drawing, downsampling math, network requests, feature map rendering, and logit plotting.
- The FastAPI backend lacks Pydantic schema validation, runs synchronous subprocesses that block the asyncio event loop, and hardcodes machine-specific executable paths (`C:\iverilog\bin\...`).
- Large binary files (`vvp_out` 1.7 MB, `tb_array.vcd` 16 MB, `tb_*.out` >20 MB) and triplicate MNIST datasets (~50 MB) dirty the repository and git tree.
- The academic deadline requires a **Mini Project Submission: Circuit Diagram and Architectural Specification of One Module of the Project** (as requested by course requirements).

### 1.2 Target Audience
- **Course Instructors & Evaluators:** Evaluating digital logic circuit design (DLCD), datapath schematics, FSM control units, timing waveforms, and hardware-software co-design rigor.
- **Hardware & Software Engineers:** Maintaining, synthesizing, and deploying the RTL accelerator to FPGA/ASIC targets while utilizing the interactive Glass Box UI for visualization.

### 1.3 Success Criteria
1. **Stabilization & Cleanliness:** All monolithic files refactored; zero tracked binary artifacts in git; strict typing enforced across Python (Pydantic, mypy) and Frontend (TypeScript).
2. **Portability:** Backend automatically detects `iverilog` and `vvp` on system PATH with fallback paths.
3. **Submission Readiness:** A publication-grade, rigorous digital circuit diagram, datapath schematic, and formal functional specification of the core accelerator module ready for the Mini Project submission.

---

## 2. MVP Scope & User Stories

### 2.1 User Stories

- **US-1 (Type Safety & Validation):** As a developer, I want all frontend components typed in TypeScript and backend routes validated with Pydantic schemas so that invalid payloads fail fast with clear errors.
- **US-2 (Repository Hygiene):** As a collaborator, I want simulation outputs, waveforms, and duplicate datasets removed from git tracking so that cloning and building is fast and clean.
- **US-3 (Component Modularity):** As a frontend engineer, I want the canvas drawing board, downsampling logic, feature map viewer, and logit chart separated into modular components so that each can be independently modified and tested.
- **US-4 (Non-Blocking Backend):** As a user interacting with the UI, I want simulation execution offloaded to an asynchronous worker thread so that concurrent requests do not block the web server.
- **US-5 (Mini Project Submission — Feature X):** As a student submitting the DLCD mini-project, I want a complete, comprehensive, publication-grade digital circuit diagram, register-transfer datapath schematic, and timing specification for the core Processing Element module (`conv_pe.v` / `mac_q7_8.v`) so that I can directly submit it for academic grading.

---

## 3. Out of Scope

- Re-training the neural network weights in PyTorch (frozen at 98.83% accuracy).
- Rewriting the core datapath Verilog modules (`conv1_array`, `conv2_array`, `maxpool_array`, `mlp_head`, `v2_top`), which have already been verified with 0 bit-level errors.
- Adding physical FPGA board drivers (e.g. UART/JTAG to real Xilinx/Altera FPGA) in this phase.
- Cloud hosting or remote multi-user authentication.

---

## 4. Tech Stack & Architecture

- **Frontend:** React 19, TypeScript (`.tsx`), Vite 8, Oxlint, CSS Modules.
- **Backend:** Python 3.10+, FastAPI, Pydantic v2, Uvicorn, `asyncio.to_thread`.
- **Hardware Simulation:** Icarus Verilog (`iverilog`, `vvp`), GTKWave.
- **Linting & Analysis:** Ruff / Mypy (Python), Oxlint / TSC (TypeScript), Verilog conventions (` `default_nettype none`).
- **Documentation & Schematics:** Markdown, Mermaid.js, ASCII RTL Datapath Schematics, LaTeX math equations.

---

## 5. Target Clean Directory Structure

```
c:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator\
├── CURRENT_STATE.md                       # Repository audit report
├── PRD.md                                 # Stabilization & submission PRD
├── dlcd_presentation.md                   # Presentation slide deck
├── run_v2_ui.bat                          # One-click Windows dashboard launcher
├── .gitignore                             # Comprehensive ignore rules
│
├── data/                                  # Canonical, unified dataset store
│   └── MNIST/raw/                         # Single source of truth for MNIST binaries
│
├── docs/                                  # Academic submissions & diagrams
│   ├── mini_project_submission/           # Feature X Deliverables
│   │   ├── circuit_diagram_conv_pe.png    # High-resolution rendered schematic
│   │   └── module_specification.md        # Complete academic report & datapath analysis
│   └── architecture/                      # Architecture contracts and rules
│
├── v1/                                    # V1 Reference MLP Accelerator
│   ├── verilog_src/                       # Clean V1 RTL & testbenches (no .out/.vcd)
│   └── python_golden_model/               # V1 math models
│
└── v2/                                    # V2 CNN Accelerator & Platform
    ├── verilog_src/                       # V2 RTL modules & testbenches
    │   ├── include/                       # Common headers & parameter files
    │   └── *.v                            # Zero tracked binaries or waveforms
    ├── python_golden_model/               # PyTorch models, Q7.8 emulators, ROM generators
    ├── regression/                        # Automated regression harness
    └── v2_ui/                             # Decoupled Glass Box Web Application
        ├── backend/                       # Modular FastAPI Application
        │   ├── app/
        │   │   ├── main.py                # Thin FastAPI route definitions
        │   │   ├── schemas.py             # Pydantic v2 request/response models
        │   │   ├── simulator.py           # Async non-blocking iverilog runner
        │   │   ├── preprocessor.py        # 28x28->20x20 scaling & Q7.8 quantizer
        │   │   └── config.py              # Toolchain locator & environment configs
        │   └── requirements.txt
        └── frontend/                      # Modular React 19 + TypeScript App
            ├── src/
            │   ├── components/
            │   │   ├── CanvasBoard.tsx    # Smooth drawing canvas & touch controls
            │   │   ├── FeatureGrid.tsx    # Heatmap visualizer for layer outputs
            │   │   └── LogitChart.tsx     # Dynamic softmax logit bar chart
            │   ├── hooks/
            │   │   └── usePredict.ts      # Custom hook managing state & API communication
            │   ├── utils/
            │   │   └── downsample.ts      # Pure downsampling & image normalization
            │   ├── types/
            │   │   └── api.ts             # TypeScript interfaces for API contracts
            │   ├── App.tsx                # Clean high-level dashboard orchestrator
            │   └── main.tsx
            ├── tsconfig.json              # Strict TypeScript configuration
            └── package.json
```

---

## 6. Phases of Work (Implementation Roadmap)

### Phase 1: Linting & Type Safety
*Goal: Enforce strict compile-time checks, type safety, and static analysis across all tiers.*
- **Step 1.1 (Frontend TypeScript Migration):**
  - Add `typescript` and `@types/*` to `v2/v2_ui/frontend/package.json`.
  - Create strict `tsconfig.json` (`strict: true`, `noImplicitAny: true`, `jsx: react-jsx`).
  - Convert `src/main.jsx` $\rightarrow$ `src/main.tsx` and create explicit types in `src/types/api.ts` for all simulation payloads:
    ```typescript
    export interface PredictResponse {
      prediction: number;
      logits: number[];
      dense1: number[];
      dense2: number[];
      input: number[][];
      mp1: number[][][];
      mp2: number[][][];
    }
    ```
- **Step 1.2 (Backend Type Safety & Pydantic Validation):**
  - Install and configure Pydantic v2 in `v2/v2_ui/backend`.
  - Define strict validation schemas:
    ```python
    class PredictRequest(BaseModel):
        image: list[list[float]] = Field(..., description="28x28 normalized grayscale matrix")
        
        @field_validator("image")
        @classmethod
        def validate_dimensions(cls, v):
            if len(v) != 28 or any(len(row) != 28 for row in v):
                raise ValueError("Input image must be exactly 28x28")
            return v
    ```
  - Add type annotations (`mypy` compliant) to all backend helper functions (`hex16`, `parse_signed_str`, `downsample_28_to_20`).
- **Step 1.3 (RTL Linting & Hygiene Protocol):**
  - Verify all Verilog modules compile with `` `default_nettype none `` in testbenches to eliminate implicit single-bit wire bugs.
  - Audit port bit-widths across `v2_top.v` and child modules to ensure zero truncation warnings.

---

### Phase 2: File Restructuring & Git Hygiene
*Goal: Purge binary bloat, unify redundant assets, and establish clean folder segregation.*
- **Step 2.1 (Purge Large Binaries & Waveforms from Git Tracking):**
  - Untrack and remove `v2/verilog_src/vvp_out` (1.7 MB).
  - Untrack and remove `v1/verilog_src/tb_array.vcd` (16 MB), `tb_accelerator_top.out` (7.3 MB), `tb_top.out` (7.3 MB), and `tb_array.out` (6.6 MB).
  - Remove root clutter (`v2.zip`, `DLCD_Neural_Accelerator.lnk`).
- **Step 2.2 (Update `.gitignore`):**
  - Comprehensively block simulation artifacts:
    ```gitignore
    *.out
    *.vvp
    *.vcd
    vvp_out
    v2_top_fixed_test
    *_test
    *.zip
    *.lnk
    node_modules/
    dist/
    .vite/
    __pycache__/
    *.pyc
    .pytest_cache/
    .mypy_cache/
    temp/
    tmp/
    ```
- **Step 2.3 (Dataset Consolidation):**
  - Keep single canonical dataset directory at `/data/MNIST/raw/`.
  - Remove redundant duplicate copies in `v1/data/MNIST/raw/` and `v2/python_golden_model/data/MNIST/raw/`.
  - Update any trainer scripts to reference the root `data/` path.
- **Step 2.4 (Clean Build Directory Setup):**
  - Ensure all temporary simulation builds output to a transient or ignored `build/` or system `tempfile` directory rather than polluting `verilog_src/`.

---

### Phase 3: Component & Logic Extraction
*Goal: Decompose monolithic files into single-responsibility, highly maintainable units.*
- **Step 3.1 (Frontend Component Extraction):**
  - Extract `v2/v2_ui/frontend/src/App.jsx` (306 lines) into modular components:
    1. `components/CanvasBoard.tsx`: Handles drawing events, touch support, fat brush configuration, clear action, and coordinate transforms.
    2. `utils/downsample.ts`: Pure function converting canvas imageData (280×280) to 28×28 matrix via 10×10 block averaging.
    3. `components/FeatureGrid.tsx`: Pure visualization component rendering normalized 2D matrices with custom RGB accent tints and dynamic contrast scaling.
    4. `components/LogitChart.tsx`: Softmax probability bar chart with dynamic temperature scaling.
    5. `hooks/usePredict.ts`: Custom hook managing prediction state, error states, and async fetch.
    6. `App.tsx`: High-level layout composer (< 80 lines).
- **Step 3.2 (Backend Logic Extraction & Async Execution):**
  - Decompose `v2/v2_ui/backend/main.py`:
    1. `config.py`: Dynamic toolchain locator finding `iverilog` and `vvp` via `shutil.which` on PATH or falling back to `C:\iverilog\bin`.
    2. `preprocessor.py`: Decoupled image resizing and Q7.8 fixed-point translation.
    3. `simulator.py`: Encapsulates Icarus Verilog compilation and execution, running inside `asyncio.to_thread` to preserve FastAPI concurrency.
    4. `main.py`: Clean, declarative FastAPI route (< 40 lines).
- **Step 3.3 (Hardware ROM Path Parameterization):**
  - Refactor `v2_top.v` and `mlp_head.v` to accept macro-defined ROM paths (`+define+WEIGHT_ROM_PATH="..."`) so tests can be run hermetically from any working directory without relative path hacks.

---

### Phase 4: Feature X — Mini Project Submission: Circuit Diagram & Architectural Specification of One Module
*Goal: Deliver the complete, publication-grade academic submission artifact as requested for the DLCD Mini Project.*
- **Selected Module:** **Conv1 Processing Element (`conv_pe.v`) and sequential Q7.8 MAC Engine (`mac_q7_8.v`)** *(with Systolic Processing Element `systolic_pe.v` as verified companion module)*.
- **Deliverables & Specifications to Include in `docs/mini_project_submission/`:**
  1. **Executive Module Overview:**
     - Purpose of the module in the DLCD CNN accelerator.
     - Operational frequency, cycle budget (9 cycles per window), and arithmetic precision (Q7.8).
  2. **Detailed Pinout & Interface Contract Table:**
     - Port name, direction, bit-width, active polarity, and timing behavior for all signals: `clk`, `reset`, `start`, `pixel_val` [15:0], `weight_val` [15:0], `out_val` [15:0], `valid_out`.
  3. **Register-Transfer-Level (RTL) Datapath Circuit Diagram:**
     - Gate- and register-level block schematic showing:
       - 16-bit signed input registers (Multiplier inputs $A$ and $B$).
       - $16\text{-bit} \times 16\text{-bit} \rightarrow 32\text{-bit}$ Signed Multiplier block.
       - Truncation Arithmetic Unit: Arithmetic right shift by 8 bits (`prod[23:8]`) for Q7.8 fixed-point alignment.
       - 16-bit Signed Accumulator Adder with feedback register.
       - Synchronous Reset / Clear multiplexer (`clr_acc`).
       - 4-bit Cycle Counter register (0 to 8) tracking the 9 kernel taps.
  4. **Control Unit & Finite State Machine (FSM):**
     - Detailed state transition graph:
       - `IDLE`: Awaiting start strobe.
       - `ACCUMULATE`: Cycling through tap 0 to 8, asserting MAC enable.
       - `VALID_PULSE`: Latching final sum to output register and asserting `valid_out`.
  5. **Q7.8 Fixed-Point Mathematical Proof & Error Bound:**
     - Formal proof of scaling: why multiplying two Q7.8 numbers yields Q14.16, why slicing bits [23:8] restores Q7.8 format, and bounding the maximum truncation error per tap ($\le 2^{-8} = 0.00390625$).
  6. **Timing Diagram / Waveform Trace:**
     - Cycle-accurate ASCII/Timing Diagram illustrating clock edges, counter progression, input streaming, multiplication latency, and the `valid_out` assertion.
  7. **Academic Mini-Project Submission Document:**
     - Synthesize into a comprehensive, ready-to-submit academic report markdown file: `docs/mini_project_submission/module_specification.md` along with structural Mermaid and ASCII circuit schematics.

---

## 7. Execution & Verification Checklist

- [ ] **Phase 1 Complete:** TypeScript compiles with `tsc --noEmit` clean; Pydantic models validate `/predict`.
- [ ] **Phase 2 Complete:** Git status shows zero untracked or modified binary files; duplicate MNIST folders removed.
- [ ] **Phase 3 Complete:** `App.jsx` split into modular components; backend uses non-blocking async executor; UI works end-to-end.
- [ ] **Phase 4 Complete:** Full Mini Project Submission artifact generated with circuit diagram, datapath schematic, FSM states, and math proofs.
- [ ] **Final Regression:** E2E hardware verification passes with 100% agreement against golden model.
