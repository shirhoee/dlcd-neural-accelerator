# V2 Architecture Rules & Guidelines

## Project Summary
Hardware neural network accelerator, V2. Adds a convolutional frontend (2x Conv+ReLU+MaxPool) ahead of an MLP head, targeting 20x20 input resolution, digits 0-9 only (MNIST). Q7.8 fixed-point arithmetic, bias-free throughout, reusing V1's verified systolic_array.v / mac_q7_8.v / relu_q7_8.v / layer_relu.v for the MLP portion.

## Inherited from V1 (reused as-is)
- `systolic_array.v` (parameterized ROWS/COLS systolic MAC array)
- `mac_q7_8.v` (Q7.8 sequential MAC with truncation)
- `relu_q7_8.v` / `layer_relu.v` (parameterized ReLU)

**Do not modify without strong reason — these are already verified.**

## New for V2
- Conv2D hardware module(s) + line buffers / sliding window logic
- MaxPool hardware module
- Wider/reconfigured systolic array dimensions for the new MLP head (200->64->32->10)

## Process Rules (Lessons from V1 — non-negotiable)
1. Every training run must pass a mandatory Q7.8 headroom check (max|logit| per layer, with realistic margin, not just theoretical worst-case) before hex export is allowed. No exceptions.
2. The regression harness must validate against BOTH the Q7.8 integer emulator AND true Float32 logits from its very first version, flagging any divergence — not retrofitted after a bug is found.
3. Any live/interactive Tkinter UI testing must be preceded by a synthetic/headless test using the identical preprocessing code path, and that headless test must be verified to actually exercise the preprocessing logic being tested (no silent no-ops that give false confidence).
4. A milestone is not marked complete based on synthetic/simulated results alone if live/interactive testing is part of its definition. Real testing required before tagging.
5. After every milestone, check `git status` and unpushed commit/tag count as a standing step; push before moving to the next milestone. Do not let commits sit local-only for multiple milestones.
6. The core architecture spec (input resolution: 20x20, layer dimensions, dataset: MNIST digits only, fixed-point format: Q7.8) is locked once N0 is validated, and is not changed without an explicit, justified proposal — not casual mid-project scope changes.
7. Any agent decision involving a real tradeoff (parameter choice, file move/rename, preprocessing method, which layer to rescale) must be reported along with the alternative not taken, before proceeding to the next step.
8. File and directory names, once established for V2, are not renamed mid-project.
9. Milestones are tagged in Git (N0, N1, N2...) representing verified working states — never tag with a known bug present (same discipline as V1's M-series).

## Directory / File Map
- `v2/verilog_src/`
- `v2/python_golden_model/`
- `v2/*.py` (generators)
- `v2/AGENTS.md`
- `v2/PROGRESS.md`

## Milestone Plan (not yet started)
- **N0**: PyTorch golden model - Conv+MLP architecture, MNIST digits, float32 validation only
- **N1**: Conv layer hardware + testbench
- **N2**: Pooling hardware + testbench
- **N3**: Resized L1-equivalent systolic array for post-conv MLP head, reverified against golden
- **N4**: L2/L3 arrays reused from V1 design (reparameterized dimensions)
- **N5**: Full pipeline integration + regression harness (Float32-divergence check built in from the start)
- **N6**: Train on MNIST-with-augmentation, headroom sweep as mandatory gate before export
- **N7**: Live hand-drawn Tkinter demo — the real final-stage test
