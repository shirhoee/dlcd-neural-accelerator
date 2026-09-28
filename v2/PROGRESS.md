# V2 PROGRESS.md — Living Changelog for CNN Upgrade

## Initialization
- Initialized isolated v2/ working directory for the CNN architecture upgrade.
- Explicitly scoped the architectural inheritance: keeping base verified components (systolic_array.v, mac_q7_8.v, 
elu_q7_8.v, layer_relu.v) from V1.
- Staged development plan for new V2 components: convolutions, pooling, line buffers, and an expanded MLP head.

## N0: PyTorch Golden Model
- **Status:** Completed
- Built 	rain_v2_n0.py defining the baseline CNN+MLP model in pure PyTorch.
- Implemented morphological augmentations (dilation/erosion) and achieved 97.93% accuracy.
- Conducted the mandatory max|logit| sweep (peaked at 36.55, well below the 127.99 Q7.8 ceiling limit).

## N1: Conv1 PE
- **Status:** Completed
- Copied mac_q7_8.v and ixed_point_math.py to v2/ to ensure standalone compilation.
- Designed conv_pe.v (9-tap sequential MAC, weight-stationary).
- Verified via 	b_conv_pe.v and python golden model conv1_layer_golden_model.py.

## N2: MaxPool PE
- **Status:** Completed
- Designed maxpool_pe.v as a purely combinational block taking 4 parallel inputs.
- Ensured strictly signed Q7.8 16-bit comparisons matching V1's rgmax.v pattern to prevent 2's-complement comparison bugs.
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
