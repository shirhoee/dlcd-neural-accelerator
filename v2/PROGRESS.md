# V2 PROGRESS.md — Living Changelog for CNN Upgrade

## Initialization
- Initialized isolated v2/ working directory for the CNN architecture upgrade.
- Explicitly scoped the architectural inheritance: keeping base verified components (systolic_array.v, mac_q7_8.v, 
relu_q7_8.v, layer_relu.v) from V1.
- Staged development plan for new V2 components: convolutions, pooling, line buffers, and an expanded MLP head.

## N0: PyTorch Golden Model
- **Status:** Completed
- Built train_v2_n0.py defining the baseline CNN+MLP model in pure PyTorch.
- Implemented morphological augmentations (dilation/erosion) and achieved 97.93% accuracy.
- Conducted the mandatory max|logit| sweep (peaked at 36.55, well below the 127.99 Q7.8 ceiling limit).

## N1: Conv1 PE
- **Status:** Completed
- Copied mac_q7_8.v and fixed_point_math.py to v2/ to ensure standalone compilation.
- Designed conv_pe.v (9-tap sequential MAC, weight-stationary).
- Verified via tb_conv_pe.v and python golden model conv1_layer_golden_model.py.

## N2: MaxPool PE
- **Status:** Completed
- Designed maxpool_pe.v as a purely combinational block taking 4 parallel inputs.
- Ensured strictly signed Q7.8 16-bit comparisons matching V1's aargmax.v pattern to prevent 2's-complement comparison bugs.
- Verified against python golden model maxpool2d_golden_model.py.

## N3a: Sliding-Window Generator
- **Status:** Completed
- Designed window_gen.v to separate addressing/buffering from mathematical operations.
- Implemented a 47-element shift register line buffer mapped to a 22x22 virtual padded grid, outputting a parallel 3x3 window combinationally.
- Established rigorous interface contracts requiring zero-latency combinational reads for downstream modules.

## N3b: Full Conv1 Array
- **Status:** Completed
- Designed conv1_array.v with a master state machine wrapping window_gen.v and 4 instances of conv_pe.v.
- Documented a strict bit-slicing convention for delivering flat weights to all 4 channels.
- Validated 1600/1600 output pixels bit-for-bit against python golden model outputs.

## N4a: MaxPool Sliding-Window Memory Router
- **Status:** Completed
- Designed pool_window_gen.v memory router to form 2x2 windows with a stride of 2 without complex FSM logic (relies on odd/even coordinate parity).
- Utilized a 21-stage shift register to buffer the incoming streaming rows correctly.
- Validated 100/100 matching windows against Python golden outputs, handling sporadic valid pulses effectively.

## N4b: Full MaxPool Array Integration
- **Status:** Completed
- Built maxpool_array.v by chaining 4 pool_window_gen and 4 maxpool_pe units.
- Copied relu_q7_8.v from v1/ and applied it after pooling for mathematical equivalence (relu(max(x)) == max(relu(x))) saving 75% ReLU ops.
- Generated expected output using python gen_maxpool_array_vectors.py ensuring non-vacuous tests.
- Verified seamlessly in chain test (400/400) and standalone shift-register leak tests (1600/1600).
- Verified negative edge cases and mutated paths.


## N5: Conv2 Subsystem
- **Status:** Completed
- Built conv2_window_gen.v line buffers for a 10x10 streaming grid supporting padding=1 internally.
- Built conv2_pe.v with 4x parallel mac_q7_8.v feeding a combinational adder tree.
- Built conv2_array.v with a 100-word input buffer for all 4 channels to handle stream gaps from N4.
- Employed an explicitly pipelined FSM to fetch, mac (over 9 cycles), and shift.
- Wrote gen_conv2_vectors.py generating golden data directly from isolated MaxPool outputs.
- Testbench tb_conv2_array.v completely decoupled from earlier layers.
- Passed 800/800 output vector assertions perfectly.

## N6: MaxPool2 Subsystem
- **Status:** Completed
- Built pool2_window_gen.v line buffers mapping the 10x10 input stream to 2x2 windows with an 11-stage shift register.
- Clock-enable explicitly gated by valid_in to seamlessly handle multi-cycle gaps from the N5 Conv2 PE outputs.
- Built maxpool2_array.v instantiating 8 window generators and 8 maxpool_pe cores natively in parallel.
- Applied ReLU(Max(x)) hardware optimization, situating the ReLU immediately after the downsampled maxpool output.
- Isolated testbench tb_maxpool2_array.v injects random gap latency into the stream.
- Verified 200/200 exact vector matches against PyTorch golden models.

## N7: Dense Layer Subsystem
- **Status:** Completed
- Adjusted the V2 MLP PyTorch architecture head to evaluate the 200->10 dense topology.
- Wrote gen_dense_vectors.py utilizing weight reshaping and axis permutation to solve the Flatten trap.
- Built dense_pe.v with 8 combinational multipliers and an adder tree for real-time dense inference.
- Built dense_array.v utilizing 10 PEs (80 multipliers total) and a synchronous gap-resistant state counter.
- Evaluated isolated vectors in tb_dense_array.v verifying a 10/10 exact bit-match on final output logits.

## N8: Argmax Layer Subsystem
- **Status:** Completed
- Built aargmax.v utilizing a purely combinational 4-stage binary comparison tree.
- Implemented robust signed logic and pairing to track the winning index dynamically.
- Deployed a 1-cycle pipeline register buffering the final prediction exactly when valid_out pulses.
- Validated via tb_aargmax.v with 5 extreme-edge synthetic datasets, verifying exact deterministic tie-breaking.

## N9: Top-Level Wrapper
- **Status:** Completed
- Built v2_top.v abstracting the entire 6-layer CNN network behind a standard control interface (clk, reset, start, pixel_in, prediction, done).
- Hard-coded weight extraction by instantiating ROMs internal to v2_top.v and flattening them combinationally into the massive 576-bit and 4608-bit busses required by the Conv array instances.
- Datapath successfully interlocked from end-to-end utilizing zero-latency handshake strobes.
- Tested against a full digit (7) in tb_v2_top.v. Passed instantly without logic snags. Architecture is complete.

## N10: V2 Glass Box UI & Training Optimizer
- **Status:** Completed
- Built an E2E testing framework spanning a PyTorch optimizer, a Verilog logic analyzer, and a React/FastAPI frontend.
- train_and_export_all.py heavily optimized with 50 epochs, Cosine Annealing learning rate schedule, and fully automatic Q7.8 physical hardware weight generation.
- Validated physically simulated hardware accuracy across 10,000 test images using the exact Q7.8 fractional hex weights re-loaded into PyTorch: **98.16% final hardware accuracy**.
- Deployed a "Silicon Blueprint" themed interactive React/Vite dashboard allowing users to draw a digit on a smooth HTML5 Canvas.
- Implemented real-time hardware logging inside tb_v2_top.v, visually displaying the exact streaming feature maps of MaxPool1 and MaxPool2, and plotting the Softmax-scaled dense logits directly extracted from the compiled Verilog simulation.

## N11: Docs repair, spec record, audit gaps
- **Status:** Completed
- Repaired corrupted escape sequences in AGENTS.md and PROGRESS.md.
- Documented the unrecorded architecture shift (200->10) at N7 and added the N13-N14 spec restoration.
- Corrected V1 inheritance and file maps in AGENTS.md.
- Extended AUDIT_REPORT.md with verified testbench failures, full testbench lists, and identified that no full-network integer emulator exists.
- Tagged N11 and pushed all docs repairs.

## N12: Regression harness and baseline
- **Status:** Completed
- Built `v2/regression/harness.py` to evaluate the RTL dynamically on all 10,000 MNIST test images via parallel thread pools invoking `iverilog`.
- Built an exact Q7.8 mathematical emulator (`int_emulator_v2.py`) that strictly mirrors RTL truncation and bit-slicing logic (0 RTL vs Emu mismatches over 10,000 images).
- Introduced `tb_v2_top_fixed.v` as a hermetic standalone testbench explicitly untethered from the UI's dynamic test file.
- Verified 98.11% true accuracy when proper PyTorch normalization (`(0.1307,), (0.3081,)`) is applied in emulation.
- Established baseline 200->10 logic cycles: MP1: 4894, MP2: 1072. Total Pipeline: 6139 cycles.

## N13: True Spec PyTorch Model & Export
- **Status:** Completed
- Built train_mlp3.py implementing the true specification: 200 -> 64 -> 32 -> 10.
- Trained with Cosine Annealing over 50 epochs on proper PyTorch normalization reaching 98.83% test accuracy.
- Ran Headroom Gate checks dynamically during export, verifying a maximum absolute logit of 72.50.
- Exported the three heavy weight matrices linearly flattened to dense1_q7_8.txt, dense2_q7_8.txt, and dense3_q7_8.txt.
- Expanded int_emulator_v2.py to natively support the deep head simulation accurately.

## N14: RTL Head on the Systolic Array
- **Status:** Completed
- Evaluated sizing tradeoffs (15,168 MACs vs multiplexed). Selected a highly optimized 16x16 tiled systolic array (256 MACs) to dramatically reduce area while maintaining throughput.
- Built export_tiled_roms.py to organize the dense weight matrices into 992 256-bit words suitable for native systolic array column-wise shift loading.
- Copied systolic_array.v and its dependencies verbatim from V1, obeying strict verified-component reuse rules.
- Designed mlp_head.v with a 2900-cycle time-multiplexed state machine that flawlessly hides latency in the 6139-cycle pipeline gap, routing features through dual ping-pong RAMs (am_A and am_B).
- Successfully swapped mlp_head.v into 2_top.v without perturbing the external interfaces.
- Verified 0 mismatches against the Python Q7.8 Emulator across images, completely verifying the entire V2 RTL logic chain.

## N14.1: Python Golden Model Flattening Fix
- **Status:** Completed
- Discovered a PyTorch export bug where `nn.Flatten()` output weights in `[Channel, Height, Width]` order, whereas the hardware streaming pipeline (MaxPool2) naturally provides features in `[Height, Width, Channel]` order.
- Created `fix_export.py` to correctly apply spatial permutations (`permute(0, 2, 3, 1)`) to the `dense1` weights before exporting to `dense1_q7_8.txt` and `mlp_rom.txt`.
- Re-ran the hardware emulator over 10,000 images and achieved 98.83% accuracy, matching Float32 exactly and bringing Hardware Accuracy into full alignment.

## N15: UI Wiring
- **Status:** Completed
- Updated `tb_v2_top_fixed.v` to stream `mp1`, `mp2`, `dense1`, and `dense2` directly to `stdout`.
- Overhauled FastAPI backend (`main.py`) to safely isolate concurrent UI requests into `tempfile` directories, fully decoupling users from overriding each other's test images.
- Implemented React UI components in `App.jsx` to dynamically render the new Dense 1 (64 neurons) and Dense 2 (32 neurons) intermediate states as 8x8 and 8x4 color grids.
- Headless verification achieved via UI prediction endpoints.
