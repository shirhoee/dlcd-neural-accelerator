# AGENTS.md (Global Rules & Architecture Invariants)

**Goal:** Establish the absolute invariant rules, core architecture, tech stack standards, and operational commands for the DLCD Neural Network Accelerator project. This file is "Always On" and loaded into every context window.

---

## 1. Core Engineering Philosophy
* **Simplicity & Readability:** Write modular, declarative code. Keep components, state machines, and mathematical utilities small and single-purpose.
* **System Evolution Mindset:** When encountering a bug or hallucination, do not just fix the code. Update the relevant `.agents/rules/` file so the mistake is never repeated.
* **Progressive Disclosure:** Context is our most precious resource. Rely on domain-specific rules only when actively working in that domain (`.agents/rules/frontend.md`, `.agents/rules/backend.md`, `.agents/rules/hardware.md`).

---

## 2. Tech Stack & Architecture (from PRD)
* **Frontend:** React 19 (`react`, `react-dom`), TypeScript (`.tsx`), Vite 8, Oxlint 1.81, CSS Modules.
* **Backend:** Python 3.10+, FastAPI, Pydantic v2 schemas (`PredictRequest`, `PredictResponse`), Uvicorn server, `asyncio.to_thread`.
* **Hardware RTL:** Verilog-2001 (IEEE 1364-2001), Icarus Verilog (`iverilog`, `vvp`), GTKWave (`.vcd`).
* **Machine Learning & Golden Models:** PyTorch (`torch`, `torchvision`), custom bit-exact Python Q7.8 integer emulator (`fixed_point_math.py`, `int_emulator_v2.py`).
* **Arithmetic Precision:** Q7.8 signed fixed-point format (16-bit 2's complement: 1 sign bit, 7 integer bits, 8 fractional bits; multiplier = 256), strictly bias-free, sequential MAC with per-step truncation (`product[23:8]`).

---

## 3. Essential Terminal Commands

### Run Application Services
* **All-in-one launcher (Windows):**
  ```cmd
  run_v2_ui.bat
  ```
* **FastAPI Backend:**
  ```cmd
  cd v2\v2_ui\backend
  uvicorn main:app --reload --host 127.0.0.1 --port 8000
  ```
* **React Frontend:**
  ```cmd
  cd v2\v2_ui\frontend
  npm run dev
  ```

### Build & Lint
* **Frontend Lint:**
  ```cmd
  cd v2\v2_ui\frontend
  npm run lint
  ```
* **Frontend Type-Check:**
  ```cmd
  cd v2\v2_ui\frontend
  npx tsc --noEmit
  ```
* **Frontend Production Build:**
  ```cmd
  cd v2\v2_ui\frontend
  npm run build
  ```

### Hardware Verification & Regression
* **Quick 10-image Sanity Regression:**
  ```cmd
  cd v2\regression
  python test_10.py
  ```
* **Fast Q7.8 Emulator Batch Verification:**
  ```cmd
  cd v2\regression
  python harness_emu_new_head.py
  ```
* **Full 10,000-Image Parallel Hardware Regression:**
  ```cmd
  cd v2\regression
  python harness.py
  ```

---

## 4. Universal Code Patterns & Invariants

1. **Strict Validation at System Boundaries:**
   * Backend routes MUST validate payloads using Pydantic v2 models. Never read raw untyped dictionaries from client requests.
   * Frontend components MUST define explicit TypeScript interfaces for all props and API responses.
   * Testbenches must enforce `` `default_nettype none `` to prevent silent single-bit wire bugs.
2. **Non-Blocking Subprocess Execution:**
   * Never run synchronous `subprocess.run` directly on FastAPI's main event loop. Always offload execution to a worker thread via `await asyncio.to_thread(...)`.
3. **Dynamic Toolchain Detection:**
   * Do not hardcode absolute executable paths (e.g. `C:\iverilog\bin\iverilog.exe`). Use `shutil.which("iverilog")` with fallback to `C:\iverilog\bin\` to guarantee portability.
4. **Hardware Golden Alignment:**
   * Sequential multiply-accumulate must truncate at every step matching RTL (`product[23:8]`), never using wide floating-point accumulations that drift from hardware behavior.
   * Training exports must pass the Q7.8 Headroom Gate ($|logit| < 128$) before generating hex ROM files.
5. **Repository Cleanliness:**
   * Simulation build outputs (`*.out`, `*.vvp`, `*.vcd`, `vvp_out`) must never be committed to git. Always output to ignored temporary directories.

---

## 5. On-Demand Context Triggers
* **Frontend/UI:** When modifying React components, canvas drawing, hooks, or styling, read `.agents/rules/frontend.md`.
* **Backend/API:** When modifying FastAPI routes, Pydantic schemas, or simulation wrappers, read `.agents/rules/backend.md`.
* **Hardware/RTL:** When modifying Verilog datapath modules, testbenches, or fixed-point models, read `.agents/rules/hardware.md`.

---

## 6. Regression Testing Protocol
* Before completing any execution phase, verify that existing features remain intact.
* Run `npm run lint` and `npx tsc --noEmit` on the frontend.
* Run `python test_10.py` in `v2/regression` to confirm zero regressions against the RTL simulation baseline.
