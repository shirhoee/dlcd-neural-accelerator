========================================================================================
     PES UNIVERSITY - UE25CS251A DLCD LABORATORY END SEMESTER ASSESSMENT
                  SCREENSHOT CAPTURE SPECIFICATION & MAPPING GUIDE
========================================================================================

The final project report generator automatically embeds the following 9 screenshot figures 
from this directory (`docs/review/screenshots/`). 

If any screenshot file is not yet placed here, the report generator inserts a clear 
placeholder box ("SCREENSHOT MISSING: <filename>") so the document compiles cleanly.

----------------------------------------------------------------------------------------
TERMINAL DEMONSTRATION FIGURES (Run: docs\review\run_for_screenshots.bat)
----------------------------------------------------------------------------------------

1. Figure 7.1: tb_submission.png
   - Filename: fig7_1_tb_submission.png
   - Command: vvp docs\review\build\tb_submission.vvp
   - Source: Screen 1 of `run_for_screenshots.bat`
   - Content: Shows the 10 hardware test rows (Digit 0..9), each showing True Digit, 
     Predicted Digit, Latency (9,116 cycles), and Result: PASS, culminating in the 
     10/10 PASSED (100.0% Hardware Accuracy) scorecard.

2. Figure 7.2: test10.png
   - Filename: fig7_2_test10.png
   - Command: python v2\regression\test_10.py
   - Source: Screen 2 of `run_for_screenshots.bat`
   - Content: Shows the 10-image RTL vs bit-exact Q7.8 integer emulator regression, 
     reporting 10/10 matched, RTL Accuracy: 1.0, and Layer Breakdown Mean: MP1 4894, 
     MP2 1072, Dense 2977 cycles.

3. Figure 7.3: emu_harness.png
   - Filename: fig7_3_emu_harness.png
   - Command: python docs\review\build\eval_emu_10k.py
   - Source: Screen 3 of `run_for_screenshots.bat`
   - Content: Shows the full 10,000-image evaluation summary of the bit-exact Q7.8 
     integer emulator and float32 PyTorch model on the full MNIST test set.

4. Figure 7.4: all_testbenches.png
   - Filename: fig7_4_all_testbenches.png
   - Command: run_all_tests.bat
   - Source: Screen 4 of `run_for_screenshots.bat`
   - Content: Shows the complete test runner summary verifying all 13 active hardware 
     testbenches (13 PASSED, 0 FAILED).

5. Figure 7.5: mlp_head_tb.png
   - Filename: fig7_5_mlp_head_tb.png
   - Command: vvp docs\review\build\tb_mlp_head.vvp
   - Source: Screen 5 of `run_for_screenshots.bat`
   - Content: Shows the unit verification line:
     "ALL TESTS PASSED: 10/10 MLP Head output logits matched in 2978 cycles."

----------------------------------------------------------------------------------------
GTKWAVE LOGIC ANALYZER TIMING FIGURES (Run GTKWave commands below)
----------------------------------------------------------------------------------------

6. Figure 7.6: gtkwave_full.png
   - Filename: fig7_6_gtkwave_full.png
   - Command: gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_full.gtkw
   - Time Window: 0 ns to 91,205 ns (Full Run)
   - Content: Shows global execution spanning start assertion (30 ns), Conv1/MP1 
     streaming (to 48,965 ns), Conv2/MP2 streaming (to 61,405 ns), MLP head systolic 
     execution (to 91,175 ns), and done strobe with prediction at 91,185 ns.

7. Figure 7.7: gtkwave_conv1_mac.png
   - Filename: fig7_7_gtkwave_conv1_mac.png
   - Command: gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_conv1_mac.gtkw
   - Time Window: 500 ns to 1,500 ns
   - Content: Detailed inspection of the 9-cycle MAC accumulation sequence across 
     Conv1 PEs showing `init_cnt`, `mac_cnt` (0..8), `tap_idx` (0..8), and `valid_out`.

8. Figure 7.8: gtkwave_mlp_fsm.png
   - Filename: fig7_8_gtkwave_mlp_fsm.png
   - Command: gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_mlp_fsm.gtkw
   - Time Window: 61,350 ns to 63,000 ns (first tiles) or 86,200 ns to 86,500 ns (Layer 1->2)
   - Content: Shows `mlp_head` 4-state FSM transitions (LOAD_WEIGHT -> COMPUTE), 
     the 48-cycle tile counter (`timer` 0..47), and layer progression.

9. Figure 7.9: gtkwave_end.png
   - Filename: fig7_9_gtkwave_end.png
   - Command: gtkwave docs\review\wave\wave.vcd docs\review\wave\wave_end.gtkw
   - Time Window: 91,000 ns to 91,300 ns
   - Content: Final stage completion showing `d_valid` assertion at 91,175 ns, 
     combinational argmax resolution, and `done` rising with valid digit `prediction` 
     at 91,185 ns (Cycle 9,116).
