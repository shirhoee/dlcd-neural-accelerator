@echo off
:: Recompile tb_v2_top_fixed with TEST_IMAGE_FILE pointing to a copy of the
:: golden test image placed alongside the RTL (relative path, no spaces).
iverilog -g2001 -Wall -DTEST_IMAGE_FILE="""test_image_tmp.txt""" -o "..\..\docs\review\build\tb_v2_top_fixed.vvp" tb_v2_top_fixed.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v argmax.v
