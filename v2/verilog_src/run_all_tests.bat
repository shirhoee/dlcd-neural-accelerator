@echo off
setlocal enabledelayedexpansion

echo ========================================================================================
echo          PES UNIVERSITY - UE25CS251A DLCD LABORATORY END SEMESTER ASSESSMENT
echo                  AUTOMATED VERILOG TESTBENCH SUITE EXECUTOR
echo ========================================================================================
echo.

set FAIL_COUNT=0
set PASS_COUNT=0

call :run_test tb_conv_pe "tb_conv_pe.v conv_pe.v mac_q7_8.v"
call :run_test tb_window_gen "tb_window_gen.v window_gen.v"
call :run_test tb_pool_window_gen "tb_pool_window_gen.v pool_window_gen.v"
call :run_test tb_maxpool_pe "tb_maxpool_pe.v maxpool_pe.v"
call :run_test tb_maxpool_array "tb_maxpool_array.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v"
call :run_test tb_maxpool2_array "tb_maxpool2_array.v maxpool2_array.v pool2_window_gen.v maxpool_pe.v relu_q7_8.v"
call :run_test tb_conv1_array "tb_conv1_array.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v"
call :run_test tb_conv1_maxpool_chain "tb_conv1_maxpool_chain.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v"
call :run_test tb_conv2_array "tb_conv2_array.v conv2_array.v conv2_window_gen.v conv2_pe.v mac_q7_8.v"
call :run_test tb_mlp_head "tb_mlp_head.v mlp_head.v systolic_array.v systolic_pe.v mac_q7_8.v relu_q7_8.v layer_relu.v"
call :run_test tb_argmax "tb_argmax.v argmax.v"
call :run_test tb_v2_top "tb_v2_top.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v layer_relu.v argmax.v"
call :run_test tb_submission "tb_submission.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v layer_relu.v argmax.v"

echo ========================================================================================
echo  TESTBENCH RUNNER SUMMARY: %PASS_COUNT% PASSED, %FAIL_COUNT% FAILED
echo ========================================================================================
if %FAIL_COUNT% equ 0 (
    echo  ALL VERILOG HARDWARE TESTBENCHES PASSED CLEANLY!
) else (
    echo  SOME TESTS FAILED!
)
echo.

del /q /f sim_test.vvp *.vcd 2>nul
exit /b %FAIL_COUNT%

:run_test
set TB_NAME=%1
set SOURCES=%~2
echo ----------------------------------------------------------------------------------------
echo  [RUNNING] %TB_NAME% ...
iverilog -o sim_test.vvp %SOURCES%
if %errorlevel% neq 0 (
    echo  [FAILED COMPILATION] %TB_NAME%
    set /a FAIL_COUNT+=1
    del /q /f sim_test.vvp 2>nul
    exit /b 1
)

vvp sim_test.vvp > sim_test.log 2>&1
findstr /i "ALL TESTS PASSED T1 MATCH PASS: Output FINAL SCORECARD" sim_test.log >nul
if %errorlevel% equ 0 (
    echo  [PASSED] %TB_NAME%
    set /a PASS_COUNT+=1
) else (
    echo  [FAILED EXECUTION] %TB_NAME%
    type sim_test.log
    set /a FAIL_COUNT+=1
)
del /q /f sim_test.vvp sim_test.log *.vcd 2>nul
exit /b 0
