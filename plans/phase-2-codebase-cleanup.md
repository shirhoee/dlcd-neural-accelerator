# Phase 2: Codebase Cleanup & Repository Sanitization Execution Plan

## Feature Description & User Stories
Phase 2 sanitizes the entire DLCD Neural Accelerator codebase by purging tracked build artifacts, obsolete boilerplate files, dead assets, and ephemeral test dumps. It hardens `.gitignore` to guarantee repository cleanliness against simulation outputs, verifies all verification tiers, and pushes all changes to the remote repository.

### User Stories:
- **US-2.1 (Repository Cleanliness):** As a hardware & software maintainer, I want tracked `.pyc` binaries, temporary test images, and obsolete generator scripts permanently removed from git, so that the repository stays clean, lightweight, and strictly aligned with Universal Invariant 5 in `AGENTS.md`.
- **US-2.2 (Frontend Asset Optimization):** As a frontend developer, I want dead Vite template scaffolding (`App.css`, `hero.png`, `react.svg`, `vite.svg`) removed and favicon references aligned with `public/favicon.svg`, so that our production bundle contains zero unused boilerplate.
- **US-2.3 (Robust Ignore Rules):** As a collaborator, I want `.gitignore` hardened against simulation logs, test vectors, and compiler caches, so that executing RTL regression and FastAPI servers never pollutes the git working tree.
- **US-2.4 (Remote Sync & Push):** As a team member, I want all completed milestones, documentation deliverables, and cleanup changes committed and pushed to `origin/main` without breaking existing hardware simulation baselines.

---

## Problem & Solution Statement
### The Problem:
1. **Tracked Python Bytecode:** `v1/python_golden_model/__pycache__/fixed_point_math.cpython-313.pyc` is tracked in git, violating clean repository hygiene.
2. **Tracked Ephemeral Test Image:** `v2/verilog_src/test_image_tmp.txt` was committed to git despite being a temporary artifact generated dynamically during test runs.
3. **Dead Frontend Boilerplate:** `v2/v2_ui/frontend/src/App.css` (185 lines of default Vite CSS), `src/assets/hero.png`, `src/assets/react.svg`, and `src/assets/vite.svg` are unused remnants of `npm create vite`. `index.html` references `/vite.svg` instead of the project's actual `favicon.svg`.
4. **Obsolete Submission Generator:** `docs/mini_project_submission/generate_waveform.py` is an obsolete matplotlib mock waveform script that was superseded by the authentic GTKWave screenshot (`conv_pe_waveform.png`).
5. **Permissive `.gitignore`:** Runtime files like `*test_image_tmp.txt`, `v2/v2_ui/backend/logs/*.txt`, and global bytecode patterns are not fully guarded.

### The Solution:
1. **Untrack & Delete Bytecode & Ephemeral Files:** Use `git rm -f` on `v1/python_golden_model/__pycache__/fixed_point_math.cpython-313.pyc` and `v2/verilog_src/test_image_tmp.txt`.
2. **Purge Dead Frontend Assets:** Delete `v2/v2_ui/frontend/src/App.css`, `src/assets/hero.png`, `src/assets/react.svg`, and `src/assets/vite.svg`. Update `v2/v2_ui/frontend/index.html` to reference `/favicon.svg`.
3. **Remove Obsolete Generator:** Delete `docs/mini_project_submission/generate_waveform.py`.
4. **Hardened `.gitignore`:** Add comprehensive ignore patterns for `*.pyc`, `__pycache__/`, `*test_image_tmp.txt`, `test_image_q7_8.txt`, and backend capture logs.
5. **Full Regression Verification:** Run `test_10.py` (RTL hardware verification), `oxlint` (frontend lint), `tsc --noEmit` (type check), and `npm run build` (production build).
6. **Git Commit & Git Push:** Commit the changes with descriptive Conventional Commits message and push all commits to `origin/main`.

---

## CONTEXT REFERENCES
- [AGENTS.md](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/AGENTS.md) — Universal Invariant 5 (Repository Cleanliness) and Section 6 (Regression Testing Protocol).
- [.gitignore](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/.gitignore) — Root git ignore rules.
- [test_10.py](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/regression/test_10.py) — 10-image sanity regression testbench.
- [index.html](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/v2_ui/frontend/index.html) — Frontend HTML shell.
- [App.tsx](file:///c:/Users/SHREYANSH%20RAJ/DLCD_Neural_Accelerator/v2/v2_ui/frontend/src/App.tsx) — Main dashboard UI component.

---

## Files to Remove, Update, or Create

### Files to Remove:
- `v1/python_golden_model/__pycache__/fixed_point_math.cpython-313.pyc` (Tracked Python bytecode)
- `v2/verilog_src/test_image_tmp.txt` (Stale simulation test image)
- `v2/v2_ui/frontend/src/App.css` (Unused Vite CSS)
- `v2/v2_ui/frontend/src/assets/hero.png` (Unused Vite asset)
- `v2/v2_ui/frontend/src/assets/react.svg` (Unused Vite asset)
- `v2/v2_ui/frontend/src/assets/vite.svg` (Unused Vite asset)
- `docs/mini_project_submission/generate_waveform.py` (Obsolete mock waveform generator)

### Files to Update:
- `.gitignore`: Add patterns for `*test_image_tmp.txt`, `test_image_q7_8.txt`, and backend logs.
- `v2/v2_ui/frontend/index.html`: Fix favicon link from `/vite.svg` to `/favicon.svg`.

---

## STEP-BY-STEP TASKS

### Task 1: Purge Tracked Bytecode and Stale Test Artifacts
- Remove `v1/python_golden_model/__pycache__/fixed_point_math.cpython-313.pyc` from git tracking and disk.
- Remove `v2/verilog_src/test_image_tmp.txt` from git tracking and disk.
- - **VALIDATE**: `git ls-files "*fixed_point_math*.pyc" "*test_image_tmp.txt"`

### Task 2: Purge Unused Frontend Boilerplate Assets & Fix Favicon
- Delete `v2/v2_ui/frontend/src/App.css`.
- Delete `v2/v2_ui/frontend/src/assets/hero.png`, `react.svg`, `vite.svg`.
- Update `v2/v2_ui/frontend/index.html` favicon link to `/favicon.svg`.
- - **VALIDATE**: `npm run lint` and `npm run build` in `v2/v2_ui/frontend`

### Task 3: Remove Obsolete Waveform Script in Submission Directory
- Delete `docs/mini_project_submission/generate_waveform.py`.
- Ensure `conv_pe_waveform.png` (GTKWave trace) and both submission PDFs remain intact.
- - **VALIDATE**: `python -c "import os; assert os.path.exists('docs/mini_project_submission/circuit_diagram_submission.pdf')"`

### Task 4: Hardened `.gitignore` Update
- Update `.gitignore` with comprehensive rules:
  - Global `__pycache__/` and `*.pyc`
  - Global `*.vcd`, `*.vvp`, `*.out`, `vvp_out`
  - Testbench temporary files: `*test_image_tmp.txt`, `*test_image_q7_8.txt`
  - Backend runtime logs: `v2/v2_ui/backend/logs/*.txt`
- - **VALIDATE**: `git status --ignored`

### Task 5: End-to-End Regression Verification
- Run full frontend linting and typecheck.
- Run frontend production build.
- Run 10-image sanity regression `python test_10.py` in `v2/regression`.
- - **VALIDATE**: `python v2/regression/test_10.py`

### Task 6: Git Commit & Git Push
- Stage all changes (`git add -A`).
- Create atomic commit: `chore: purge dead boilerplate, stale artifacts, and harden gitignore`.
- Push commits to remote: `git push origin main`.
- - **VALIDATE**: `git status`

---

## TESTING STRATEGY
1. **Frontend Verification:**
   - Run `oxlint` via `npm run lint`.
   - Run `tsc --noEmit` to confirm no broken import paths or missing types.
   - Run `npm run build` to confirm Vite bundles successfully without missing asset warnings.
2. **Hardware & Emulator Verification:**
   - Run `python test_10.py` to confirm RTL compilation (`tb_v2_top_fixed`) and simulation execution produce 10/10 matches against the PyTorch baseline with 0 errors.
3. **Repository Cleanliness Verification:**
   - Confirm `git status` shows no untracked or dirty files after test runs.

---

## ACCEPTANCE CRITERIA
- [ ] No `.pyc` files are tracked in git.
- [ ] No temporary `test_image_tmp.txt` or simulation outputs are tracked in git.
- [ ] Unused frontend files (`App.css`, `hero.png`, `react.svg`, `vite.svg`) are deleted.
- [ ] `index.html` correctly points to `/favicon.svg`.
- [ ] `.gitignore` contains rules for temporary images, simulation logs, and build artifacts.
- [ ] All frontend checks (`npm run lint`, `npx tsc --noEmit`, `npm run build`) pass with 0 errors.
- [ ] RTL simulation sanity regression (`python test_10.py`) passes 10/10 with 0 mismatches.
- [ ] All commits are pushed to `origin/main` successfully.
