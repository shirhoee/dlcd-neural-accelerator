# Phase 1: Linting & Type Safety Execution Plan

## Feature Description & User Stories
Phase 1 establishes absolute type safety, static boundary validation, and linting enforcement across all tiers of the DLCD Neural Accelerator platform (Frontend, Backend, and RTL).

### User Stories:
- **US-1.1 (Frontend Type Safety):** As a frontend developer, I want the React application migrated to strict TypeScript (`.tsx`) with explicit interfaces for component props and API payloads, so that invalid data shapes and prop mismatches are caught at compile time.
- **US-1.2 (Backend Boundary Validation):** As a backend engineer, I want incoming `/predict` requests validated by Pydantic v2 schemas and all helper functions typed, so that malformed requests return structured 422 HTTP errors instead of crashing the server.
- **US-1.3 (RTL Net Safety):** As a digital hardware designer, I want Verilog testbenches to enforce `` `default_nettype none `` and clean port bit-widths, so that single-bit typos do not silently synthesize into floating wires.

---

## Problem & Solution Statement
### The Problem:
1. **Frontend:** `v2/v2_ui/frontend` contains pure JavaScript (`.jsx`) files with no `tsconfig.json`, no TypeScript compiler checks, and no type declarations for simulation responses or canvas interactions.
2. **Backend:** `v2/v2_ui/backend/main.py` parses untyped raw dictionaries via `await request.json()`, does not validate array dimensions (accepting any arbitrary JSON structure), and helper functions lack type hints.
3. **Hardware:** Implicit net declarations in Verilog testbenches can hide wiring bugs during simulation.

### The Solution:
1. **Frontend:** Add `typescript` to `devDependencies`, configure strict `tsconfig.json` targeting ES2022 and React 19 JSX, create `src/types/api.ts` with explicit interfaces, and convert `main.jsx` and `App.jsx` to `.tsx`. Enforce validation with `npx tsc --noEmit` and `npm run lint` (`oxlint`).
2. **Backend:** Create `schemas.py` declaring `PredictRequest` (with custom validator verifying a $28 \times 28$ matrix) and `PredictResponse` Pydantic models. Update `main.py` endpoint signature to `async def predict(req: PredictRequest) -> PredictResponse`. Annotate all helper functions with Python 3.10+ type hints.
3. **Hardware:** Add `` `default_nettype none `` to `tb_v2_top_fixed.v` with explicit wire declarations for all signals. Run baseline regression to verify zero compilation or regression failures.

---

## CONTEXT REFERENCES
- [PRD.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/PRD.md) — Section 6, Phase 1 (Linting & Type Safety).
- [AGENTS.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/AGENTS.md) — Universal Code Patterns and Essential Commands.
- [.agents/rules/frontend.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/.agents/rules/frontend.md) — Frontend Architecture & TypeScript Guidelines.
- [.agents/rules/backend.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/.agents/rules/backend.md) — Backend Pydantic Schemas & Error Handling.
- [.agents/rules/hardware.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/.agents/rules/hardware.md) — RTL Standards & `default_nettype` Discipline.
- [main.py](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/v2_ui/backend/main.py) — Existing backend entry point.
- [App.jsx](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/v2_ui/frontend/src/App.jsx) — Existing React dashboard.
- [tb_v2_top_fixed.v](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/verilog_src/tb_v2_top_fixed.v) — Top-level simulation testbench.

---

## New Files to Create

### API & Schemas:
- `v2/v2_ui/backend/schemas.py`: Pydantic v2 models for `PredictRequest` and `PredictResponse`.

### Types & Frontend Configuration:
- `v2/v2_ui/frontend/tsconfig.json`: Strict TypeScript compiler configuration.
- `v2/v2_ui/frontend/tsconfig.node.json`: TypeScript configuration for Vite tooling.
- `v2/v2_ui/frontend/src/types/api.ts`: TypeScript interfaces for simulation payloads, feature map channels, and drawing coordinates.

### Converted Source Files:
- `v2/v2_ui/frontend/src/main.tsx` (migrated from `main.jsx`)
- `v2/v2_ui/frontend/src/App.tsx` (migrated from `App.jsx`)

---

## STEP-BY-STEP TASKS

### Task 1: Frontend TypeScript Configuration
- Install `typescript` in `v2/v2_ui/frontend`.
- Create `tsconfig.json` with strict mode (`strict: true`, `noImplicitAny: true`, `jsx: "react-jsx"`).
- Create `tsconfig.node.json` for Vite configuration.
- Update `package.json` to include `"typecheck": "tsc --noEmit"`.
- **VALIDATE**: `cd "v2/v2_ui/frontend" && npx tsc --version`

### Task 2: API Contract Type Definitions
- Create `v2/v2_ui/frontend/src/types/api.ts`.
- Define `PredictResponse`, `PredictRequest`, `FeatureGridProps`, and `Coordinate` types.
- Ensure all multi-channel feature maps (`mp1`: $4 \times 10 \times 10$, `mp2`: $8 \times 5 \times 5$, `dense1`, `dense2`) are strictly typed as numeric multidimensional arrays.
- **VALIDATE**: `cd "v2/v2_ui/frontend" && npm run lint`

### Task 3: Migrate Frontend Components to TypeScript
- Rename `v2/v2_ui/frontend/src/main.jsx` to `main.tsx` and ensure DOM container element is non-null asserted.
- Rename `v2/v2_ui/frontend/src/App.jsx` to `App.tsx`.
- Annotate `canvasRef`, `isDrawing`, `lastPos`, `result`, `loading`, and helper functions (`getCoordinates`, `extract28x28`, `FeatureGrid`).
- Fix `index.html` script tag to reference `/src/main.tsx`.
- **VALIDATE**: `cd "v2/v2_ui/frontend" && npx tsc --noEmit && npm run lint`

### Task 4: Backend Pydantic v2 Schema Creation
- Create `v2/v2_ui/backend/schemas.py`.
- Define `PredictRequest` with strict dimension validator checking that `image` is a $28 \times 28$ nested list of floats in range $[0.0, 1.0]$.
- Define `PredictResponse` model capturing `prediction`, `logits`, `dense1`, `dense2`, `input`, `mp1`, and `mp2`.
- Update `v2/v2_ui/backend/requirements.txt` to include `pydantic>=2.0`.
- **VALIDATE**: `python -c "from v2.v2_ui.backend.schemas import PredictRequest, PredictResponse; print('Schemas imported clean')"`

### Task 5: Backend Refactoring with Type Hints & Validation
- Update `v2/v2_ui/backend/main.py` route handler:
  - Replace raw `Request` body parsing with `req: PredictRequest`.
  - Type-hint helper functions: `hex16(val: int) -> str`, `parse_signed_str(s: str) -> int`, `downsample_28_to_20(grid_28: list[list[float]]) -> list[list[float]]`.
  - Set response model to `response_model=PredictResponse`.
- Add test script to verify that invalid inputs trigger HTTP 422 Unprocessable Entity while valid arrays succeed.
- **VALIDATE**: `python -c "import py_compile; py_compile.compile('v2/v2_ui/backend/main.py', doraise=True); print('Backend compiles clean')"`

### Task 6: Hardware Testbench Net Safety & Sanity Regression
- Check `v2/verilog_src/tb_v2_top_fixed.v` for explicit net and wire declarations.
- Enforce `` `default_nettype none `` in `tb_v2_top_fixed.v` and restore `` `default_nettype wire `` at EOF.
- Verify simulation compiles cleanly under Icarus Verilog.
- Run the 10-image sanity regression script to confirm zero hardware logic regressions.
- **VALIDATE**: `cd "v2/regression" && python test_10.py`

---

## TESTING STRATEGY
1. **Frontend Type Check:** `npx tsc --noEmit` verifies that all components, hooks, canvas event handlers, and API payloads comply with TypeScript 5+ strict type checking.
2. **Frontend Linter:** `oxlint` verifies zero syntax or styling violations.
3. **Backend Schema Validation Test:** A synthetic Python test script will send:
   - Valid $28 \times 28$ image: Expects HTTP 200 and schema-compliant response.
   - Invalid $10 \times 10$ image: Expects validation error (HTTP 422).
   - Empty payload: Expects validation error (HTTP 422).
4. **Hardware Baseline Regression:** Run `v2/regression/test_10.py` verifying that all 10 hardware simulation predictions match the Q7.8 ground truth bit-for-bit.

---

## ACCEPTANCE CRITERIA
- [ ] `v2/v2_ui/frontend` compiles cleanly with `npx tsc --noEmit` (0 errors).
- [ ] `npm run lint` executes with 0 warnings/errors.
- [ ] `v2/v2_ui/backend` validates request payloads using Pydantic v2 schemas.
- [ ] Backend helper functions have complete type annotations.
- [ ] Verilog testbench compiles with `` `default_nettype none `` without undeclared wire warnings.
- [ ] Full regression suite (`test_10.py`) runs with 100% hardware agreement.
