# CURRENT_STATE.md — DLCD Neural Accelerator Repository Audit

**Audit Date:** October 2026  
**Project:** Digital Logic & Computer Design (DLCD) Neural Accelerator  
**Target:** Hardware Neural Network Accelerator for Handwritten Digit Recognition (MNIST)  

---

## 1. Executive Summary & System Architecture

The **DLCD Neural Accelerator** is a hardware-software co-design project implementing custom digital ASIC/FPGA datapath logic in Verilog to perform neural network inference on handwritten digits (MNIST dataset, 0–9). The project bridges software machine learning (PyTorch) with digital hardware design (Verilog-2001) using exact fixed-point arithmetic, verified against cycle-accurate testbenches, bit-exact integer emulators, and an interactive full-stack "Glass Box" web visualizer.

The codebase encompasses two complete architectural generations:
1. **Version 1 (V1) — Baseline Multi-Layer Perceptron (MLP):**
   - **Topology:** 100-input (10×10 image) $\rightarrow$ 16 (Hidden 1) $\rightarrow$ 6 (Hidden 2) $\rightarrow$ 10 (Output logits) $\rightarrow$ Argmax.
   - **Math Engine:** 16×16 unrolled 2D systolic array core utilizing weight-stationary dataflow.
   - **Arithmetic:** Q7.8 signed fixed-point format (1 sign bit, 7 integer bits, 8 fractional bits; multiplier = 256), strictly bias-free, sequential MAC with per-step truncation.
   - **Performance:** 93.06% accuracy on 10,000 MNIST test images (Milestone M12/M17 ceiling).

2. **Version 2 (V2) — Convolutional Neural Network (CNN) + Systolic MLP Head:**
   - **Topology:** 400-input (20×20 image) $\rightarrow$ Conv1 ($1 \rightarrow 4$ ch, $3\times 3$, valid) $\rightarrow$ MaxPool1 ($2\times 2$, stride 2, $4$ ch, $10\times 10$) $\rightarrow$ Conv2 ($4 \rightarrow 8$ ch, $3\times 3$, valid) $\rightarrow$ MaxPool2 ($2\times 2$, stride 2, $8$ ch, $5\times 5$) $\rightarrow$ MLP Head ($200 \rightarrow 64 \rightarrow 32 \rightarrow 10$) $\rightarrow$ Argmax.
   - **Frontend Hardware:** Streaming shift-register line buffers (`window_gen.v`, `pool_window_gen.v`), 9-tap sequential convolutional PEs (`conv_pe.v`), parallel multi-channel adder trees (`conv2_pe.v`), and fused MaxPool+ReLU units (`maxpool_pe.v`, `relu_q7_8.v`).
   - **Backend MLP Head Optimization (Time-Multiplexing):** Rather than instantiating 15,168 parallel multipliers in silicon, the design imports V1's verified 16×16 systolic array (256 MACs) and time-multiplexes it across the $200 \rightarrow 64 \rightarrow 32 \rightarrow 10$ layers via a 4-state Finite State Machine (`mlp_head.v`) and dual ping-pong RAMs (`ram_A` [208 words], `ram_B` [64 words]).
   - **Latency Hiding:** The MLP head computes all three dense layers in ~2,900 clock cycles, which runs entirely in parallel with the 6,139-cycle MaxPool2 streaming arrival, achieving an optimal area reduction with **zero throughput penalty**.
   - **Verification & Performance:** 98.83% test accuracy on 10,000 MNIST test images with **zero bit-level mismatches** between the Verilog RTL and the bit-exact Q7.8 Python integer emulator.

3. **Interactive "Glass Box" Full-Stack Platform:**
   - **Frontend:** React 19 + Vite dashboard featuring an HTML5 drawing canvas with 10× supersampling and instant visualization of intermediate hardware feature maps (Conv/MaxPool/Dense layers).
   - **Backend:** FastAPI service that downsamples drawings to 20×20, scales them via PyTorch standard normalization, generates Q7.8 hex vectors, compiles and executes Icarus Verilog simulation hermetically, and streams hardware cycle traces back to the UI.

---

## 2. Mapped Repository Directory Tree

```
c:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator\
│
├── .agents/                               # Development tracking and process rules
│   ├── skills/
│   │   ├── architecture_rules_skill.md    # V1 invariant architecture rules
│   │   └── project_progress_skill.md      # V1 living milestone tracking (M0–M17)
│   ├── v2_agents.md                       # V2 process rules, interface contracts & tradeoffs
│   ├── v2_audit_report.md                 # V2 audit gap analysis & testbench ledger
│   └── v2_progress.md                     # V2 living changelog (N0–N15)
│
├── data/                                  # Raw dataset storage
│   └── MNIST/raw/                         # Downloaded MNIST ubyte binaries & gz archives (19 MB)
│
├── v1/                                    # Version 1 (MLP 100->16->6->10) Subproject
│   ├── data/MNIST/raw/                    # [DEBT: Redundant duplicate of MNIST raw files]
│   ├── python_golden_model/               # Golden math references
│   │   ├── fixed_point_math.py            # Q7.8 quantization math primitives
│   │   └── weight_manager.py              # Hex weight exporter
│   ├── test_vectors/                      # Generated test vectors (.hex)
│   ├── verilog_src/                       # V1 Verilog RTL and Testbenches
│   │   ├── accelerator_top.v              # V1 Top-level datapath wrapper
│   │   ├── systolic_array.v               # Parameterized 2D systolic array
│   │   ├── systolic_pe.v                  # Weight-stationary processing element
│   │   ├── mac_q7_8.v                     # Sequential Q7.8 MAC
│   │   ├── relu_q7_8.v                    # Combinational Q7.8 ReLU
│   │   ├── argmax.v                       # 4-stage binary comparator
│   │   ├── tb_*.v                         # Testbenches for all V1 modules
│   │   ├── *.out, *.vvp, *.vcd            # [DEBT: Large compiled binaries & waveforms committed]
│   │   └── *.hex                          # Pre-generated input & weight vectors
│   ├── weights_hex/                       # Trained V1 Q7.8 weight hex files
│   └── *.py                               # V1 test generators, trainers, and regression scripts
│
├── v2/                                    # Version 2 (CNN + Systolic MLP) Subproject
│   ├── antigravity_global_boilerplate/    # [DEBT: Unintegrated global template files]
│   │   ├── .agents/                       # Template rules and skills (including audit_brownfield)
│   │   └── AGENTS.md                      # Template global rules
│   │
│   ├── python_golden_model/               # V2 Training, Emulation & ROM Exporters
│   │   ├── train_mlp3.py                  # PyTorch 50-epoch trainer for 200->64->32->10 head
│   │   ├── train_and_export_all.py        # Automated training, headroom gate & hex generator
│   │   ├── int_emulator_v2.py             # Bit-exact Python integer emulator of V2 RTL
│   │   ├── fixed_point_math.py            # [DEBT: Duplicated from v1/]
│   │   ├── export_tiled_roms.py           # Packs dense weights into 992-word 256-bit ROMs
│   │   ├── fix_export.py                  # PyTorch CHW -> Hardware HWC permutation fix
│   │   ├── evaluate_hw_accuracy.py        # Evaluates accuracy over 10k test set
│   │   ├── golden_model_*.py              # Layer-specific golden models
│   │   ├── v2_n0_model.pt, v2_n13_model.pt # Trained PyTorch state dicts
│   │   ├── *.txt, *.hex                   # Exported weights and intermediate vectors
│   │   └── data/MNIST/raw/                # [DEBT: Third redundant copy of MNIST dataset]
│   │
│   ├── regression/                        # Full-System Automated Verification
│   │   ├── harness.py                     # Parallel 10,000-image regression runner (iverilog vs emu)
│   │   ├── harness_emu_new_head.py        # Fast emulator-only batch verification
│   │   ├── baseline_summary.json          # Hardware cycle count and accuracy benchmarks
│   │   └── test_10.py                     # Quick 10-image sanity regression
│   │
│   ├── v2_ui/                             # Full-Stack Interactive "Glass Box" Dashboard
│   │   ├── backend/                       # Python FastAPI Backend
│   │   │   ├── main.py                    # API entry point (/predict), downsampler & iverilog runner
│   │   │   ├── requirements.txt           # Minimal pip dependencies (fastapi, uvicorn)
│   │   │   └── logs/                      # [DEBT: Intermediate capture logs written to disk]
│   │   └── frontend/                      # React 19 + Vite Frontend
│   │       ├── src/
│   │       │   ├── App.jsx                # [DEBT: 306-line monolithic UI component]
│   │       │   ├── App.module.css         # Component styling
│   │       │   ├── main.jsx               # React DOM entry point
│   │       │   └── assets/                # UI icons and hero image
│   │       ├── package.json               # Node dependencies (react 19, vite 8, oxlint)
│   │       └── vite.config.js             # Vite bundler config
│   │
│   └── verilog_src/                       # V2 Verilog RTL and Testbenches
│       ├── v2_top.v                       # V2 Top-level datapath wrapper
│       ├── window_gen.v                   # 22x22 padded 3x3 sliding window generator (Conv1)
│       ├── conv_pe.v                      # 9-tap sequential MAC processing element
│       ├── conv1_array.v                  # 4-channel Conv1 array controller
│       ├── pool_window_gen.v              # 2x2 stride-2 pooling window generator (MaxPool1)
│       ├── maxpool_pe.v                   # Pure combinational 4-input signed max comparator
│       ├── maxpool_array.v                # 4-channel MaxPool1 + fused ReLU array
│       ├── conv2_window_gen.v             # 10x10 sliding window generator (Conv2)
│       ├── conv2_pe.v                     # 4-input parallel multiplier + adder tree PE
│       ├── conv2_array.v                  # 8-channel Conv2 array controller
│       ├── pool2_window_gen.v             # 11-stage gated shift register pooling generator
│       ├── maxpool2_array.v               # 8-channel MaxPool2 + fused ReLU array
│       ├── mlp_head.v                     # 16x16 tiled systolic MLP controller with ping-pong RAMs
│       ├── systolic_array.v               # 16x16 2D systolic array core [copied from v1/]
│       ├── systolic_pe.v                  # Systolic processing element [copied from v1/]
│       ├── mac_q7_8.v                     # Q7.8 MAC [copied from v1/]
│       ├── relu_q7_8.v                    # Q7.8 ReLU [copied from v1/]
│       ├── layer_relu.v                   # Parameterized layer ReLU [copied from v1/]
│       ├── argmax.v                       # 4-stage binary comparator tree
│       ├── tb_v2_top_fixed.v              # Hermetic testbench with cycle profiler & stdout snooper
│       ├── tb_*.v                         # Testbenches for all intermediate modules
│       ├── vvp_out                        # [DEBT: 1.7 MB compiled simulation binary tracked in git]
│       └── *.vcd, *_test                  # [DEBT: Lingering simulation waveforms and executables]
│
├── .gitignore                             # Git exclusion rules
├── dlcd_presentation.md                   # Presentation slide deck and academic talking points
├── run_v2_ui.bat                          # One-click Windows batch launcher for FastAPI + Vite
└── v2.zip                                 # [DEBT: Untracked root zip archive]
```

---

## 3. Technology Stack & Toolchain Inventory

| Domain | Technology / Tool | Version | Purpose & Usage in Codebase |
|---|---|---|---|
| **Hardware RTL** | Verilog-2001 | IEEE 1364-2001 | Core digital accelerator logic, PEs, systolic arrays, FSM controllers. |
| **Simulation** | Icarus Verilog (`iverilog`, `vvp`) | 12.0+ | RTL compilation and execution engine invoked both in CI/scripts and dynamically by UI. |
| **Waveforms** | GTKWave (`.vcd`) | 3.3+ | Signal tracing, timing verification, and cycle debugging. |
| **Machine Learning** | PyTorch (`torch`, `torchvision`) | 2.0+ | Golden network training, floating-point baseline, headroom analysis, MNIST loader. |
| **Fixed-Point Emulation** | Custom Python Engine | Python 3.10–3.13 | `fixed_point_math.py`, `int_emulator_v2.py` mimicking exact RTL truncation and saturation. |
| **Backend Framework** | FastAPI + Uvicorn | 0.115+ | REST API server (`main.py`) serving the `/predict` endpoint and orchestrating `iverilog`. |
| **Frontend Framework** | React 19 (`react`, `react-dom`) | 19.2.8 | Declarative UI for user drawing canvas and hardware feature map visualization. |
| **Build Tooling & Bundler** | Vite | 8.3.0 | Modern frontend dev server and fast HMR bundler. |
| **Linter / Formatter** | Oxlint | 1.81.0 | Fast Rust-based JavaScript linter configured in `package.json`. |
| **Styling** | CSS Modules | Standard | Scoped component styling (`App.module.css`). |
| **Scripting & Automation** | PowerShell & Windows Batch | Windows 10/11 | Batch runners (`run_v2_ui.bat`) and testing scripts. |

---

## 4. Core Entry Points & System Walkthrough

### 4.1 Digital Datapath (RTL) Entry Points
- **Top-Level Module (`v2/verilog_src/v2_top.v`):**
  - **Interface:** `clk`, `reset`, `start`, `pixel_addr` [8:0], `pixel_in` [15:0], `prediction` [3:0], `done`.
  - **Execution Flow:** Asserting `start` latches `run_latch`. `conv1_array` sweeps through the 400 pixels of the 20×20 image by issuing `pixel_addr` combinationally. The datapath streams tokens through Conv1 $\rightarrow$ MaxPool1 $\rightarrow$ Conv2 $\rightarrow$ MaxPool2 $\rightarrow$ MLP Head $\rightarrow$ Argmax. When classification finishes, `done` pulses high and `prediction` holds the 4-bit digit (0–9).
- **Hermetic Testbench (`v2/verilog_src/tb_v2_top_fixed.v`):**
  - Injects test image path via the `-DTEST_IMAGE_FILE` compile-time macro.
  - Profiles exact layer cycle counts (`mp1_cycles`, `mp2_cycles`, `dense_cycles`, `total_cycles`).
  - Sits as a non-intrusive snooper on internal registers and streams formatted output tokens (`RTL_PRED:X`, `RTL_LOGITS:A,B,...`, `RTL_MP1:...`, `RTL_MP2:...`, `RTL_DENSE1:...`, `RTL_DENSE2:...`) to `stdout`.

### 4.2 Machine Learning & Golden Models
- **True-Spec Trainer (`v2/python_golden_model/train_mlp3.py`):**
  - Defines `ConvMLP_V2_TrueSpec`: Conv2d(1, 4, 3) $\rightarrow$ MaxPool2d(2, 2) $\rightarrow$ Conv2d(4, 8, 3) $\rightarrow$ MaxPool2d(2, 2) $\rightarrow$ Flatten $\rightarrow$ Linear(200, 64) $\rightarrow$ Linear(64, 32) $\rightarrow$ Linear(32, 10).
  - Normalizes input images using standard MNIST statistics: $\mu = 0.1307, \sigma = 0.3081$.
  - Enforces mandatory Q7.8 Headroom Gate check: maximum absolute logit across all layers must remain $< 127.99$.
- **Bit-Exact Integer Emulator (`v2/python_golden_model/int_emulator_v2.py`):**
  - Mirrors hardware bit-slicing: converts weights and inputs to signed 16-bit integers, applies sequential multiplication with `val >> 8` truncation, simulates dual ping-pong RAM accumulation, and reproduces the exact 4-stage binary comparator tree.
- **ROM Packing Exporter (`v2/python_golden_model/export_tiled_roms.py` & `fix_export.py`):**
  - Transposes PyTorch's channel-first flattened weights to match the hardware's streaming Height-Width-Channel (HWC) arrival order from MaxPool2.
  - Formats 64×200, 32×64, and 10×32 weights into 992 words of 256-bit hexadecimal strings for direct `$readmemh` into `weight_rom` inside `mlp_head.v`.

### 4.3 Full-Stack Visualizer Pipeline
- **FastAPI Service (`v2/v2_ui/backend/main.py`):**
  - Exposes `POST /predict`.
  - Accepts a 28×28 grayscale drawing array.
  - Downsamples via nearest-neighbor grid interpolation to 20×20 (`downsample_28_to_20`).
  - Scales: $\text{norm} = (\text{val} - 0.1307) / 0.3081$, converts to Q7.8 integer: $\text{round}(\text{norm} \times 256.0)$, clamped to $[-32768, 32767]$.
  - Creates an isolated `tempfile.TemporaryDirectory` to prevent race conditions during concurrent requests.
  - Invokes `C:\iverilog\bin\iverilog.exe` and `C:\iverilog\bin\vvp.exe` targeting `tb_v2_top_fixed`.
  - Parses `stdout` lines and returns structured JSON containing `prediction`, `logits`, `dense1`, `dense2`, `input`, `mp1`, and `mp2`.
- **React Frontend (`v2/v2_ui/frontend/src/App.jsx`):**
  - Renders an HTML5 Canvas scaled 10× (280×280 pixels) with a 24px circular brush.
  - Downsamples drawing on submit by block-averaging 10×10 pixel blocks to 28×28 grayscale.
  - Sends payload to `http://127.0.0.1:8000/predict`.
  - Renders feature maps using dynamically calculated opacity grids (`FeatureGrid`), and visualizes raw logits with dynamic temperature-scaled bar charts.

---

## 5. Major Technical Debt & Vulnerabilities

### 5.1 Critical Codebase Debt

1. **Monolithic Frontend Component (`App.jsx` — 306 Lines):**
   - Combines 7 distinct concerns in a single file:
     - HTML5 canvas pointer and touch event handling.
     - Coordinate transformations and viewport scaling.
     - 280×280 $\rightarrow$ 28×28 spatial block-averaging downsampler.
     - Network fetching and error handling.
     - Feature map grid rendering component (`FeatureGrid`).
     - Logit calculation and dynamic temperature scaling logic.
     - Full page dashboard UI layout and state.
   - Zero unit testing, zero component modularity, no custom hooks.

2. **Lack of Type Safety Across Stack:**
   - **Frontend:** Entire frontend is written in vanilla JavaScript (`.jsx`). No TypeScript definitions, no prop validation, no schema for API responses.
   - **Backend:** `main.py` does not use Pydantic models for request validation (`data = await request.json()`, `data.get("image")`). A malformed JSON or invalid array dimension crashes the endpoint with an unhandled 500 error.

3. **Blocking Synchronous Subprocess in Async Route (`main.py`):**
   - The route handler is declared `async def predict(request: Request)`, but it runs synchronous, blocking calls:
     ```python
     subprocess.run(compile_cmd, cwd=v_dir, ...)
     process = subprocess.run(run_cmd, cwd=v_dir, ...)
     ```
   - This blocks FastAPI's asyncio event loop during the 150–300 ms Icarus Verilog compilation and execution, degrading throughput under any concurrent requests.

4. **Hardcoded Toolchain Paths & Machine Dependencies:**
   - Both `main.py` and `regression/harness.py` hardcode:
     `C:\iverilog\bin\iverilog.exe` and `C:\iverilog\bin\vvp.exe`.
   - If the project is run on a machine where Icarus Verilog is on system `PATH` or installed on Linux/macOS, all scripts and the UI backend instantly crash.

5. **Hardcoded Relative Paths in Verilog Modules:**
   - `v2/verilog_src/v2_top.v` lines 31–32:
     ```verilog
     $readmemh("../python_golden_model/weights_q7_8.txt", conv1_rom);
     $readmemh("../python_golden_model/conv2_weights_q7_8.txt", conv2_rom);
     ```
   - `v2/verilog_src/mlp_head.v` line 39:
     ```verilog
     $readmemh("../python_golden_model/mlp_rom.txt", weight_rom);
     ```
   - These hardcoded relative paths make compilation brittle: compiling from any directory other than `v2/verilog_src` causes silent `$readmemh` failures where ROMs remain uninitialized ($0$).

### 5.2 Git Repository Hygiene & Storage Bloat

1. **Large Tracked Binaries and Simulation Waveforms:**
   - `v2/verilog_src/vvp_out`: **1.7 MB** compiled binary actively tracked in Git!
   - `v1/verilog_src/tb_array.vcd`: **16 MB** simulation waveform committed to Git.
   - `v1/verilog_src/tb_accelerator_top.out`: **7.3 MB** binary committed.
   - `v1/verilog_src/tb_top.out`: **7.3 MB** binary committed.
   - `v1/verilog_src/tb_array.out`: **6.6 MB** binary committed.
   - Untracked artifacts floating in root: `v2.zip`, `DLCD_Neural_Accelerator.lnk`.

2. **Triplicate Storage of MNIST Datasets (~50 MB):**
   - `data/MNIST/raw/` (19 MB)
   - `v1/data/MNIST/raw/` (19 MB)
   - `v2/python_golden_model/data/MNIST/raw/` (12 MB)
   - The same dataset is checked in or duplicated across three separate directories.

3. **Duplicated Verilog Modules Between V1 and V2:**
   - `mac_q7_8.v`, `relu_q7_8.v`, `systolic_array.v`, `systolic_pe.v`, and `layer_relu.v` were physically copied from `v1/verilog_src` into `v2/verilog_src`.
   - While done intentionally to decouple V2, there is no shared package boundary or unified library, leading to code duplication.

4. **Incomplete `.gitignore`:**
   - Does not ignore top-level zip files, compiled `vvp_out`, `.out` files, or local Windows shortcuts (`.lnk`).
