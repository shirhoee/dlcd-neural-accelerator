@echo off
setlocal EnableDelayedExpansion

echo ========================================================================================
echo          PES UNIVERSITY - UE25CS251A DLCD LABORATORY END SEMESTER ASSESSMENT
echo                  AUTOMATED VERILOG TESTBENCH SUITE EXECUTOR
echo ========================================================================================
echo.

where iverilog >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\iverilog\bin\iverilog.exe" (
        set "PATH=C:\iverilog\bin;%PATH%"
    ) else (
        echo [ERROR] iverilog not found in PATH or C:\iverilog\bin.
        pause
        exit /b 1
    )
)

if not exist "docs\review\build" mkdir docs\review\build
if not exist "docs\review\logs" mkdir docs\review\logs

set FAIL_COUNT=0
set PASS_COUNT=0
set V_DIR=v2\verilog_src

call :test_one tb_conv_pe "tb_conv_pe.v conv_pe.v mac_q7_8.v" "ALL TESTS PASSED"
call :test_one tb_window_gen "tb_window_gen.v window_gen.v" "ALL TESTS PASSED"
call :test_one tb_pool_window_gen "tb_pool_window_gen.v pool_window_gen.v" "ALL TESTS PASSED"
call :test_one tb_maxpool_pe "tb_maxpool_pe.v maxpool_pe.v" "ALL TESTS PASSED"
call :test_one tb_maxpool_array "tb_maxpool_array.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v" "matches"
call :test_one tb_maxpool2_array "tb_maxpool2_array.v maxpool2_array.v pool2_window_gen.v maxpool_pe.v relu_q7_8.v" "matches"
call :test_one tb_conv1_array "tb_conv1_array.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v" "ALL TESTS PASSED"
call :test_one tb_conv1_maxpool_chain "tb_conv1_maxpool_chain.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v" "matches"
call :test_one tb_conv2_array "tb_conv2_array.v conv2_array.v conv2_window_gen.v conv2_pe.v mac_q7_8.v" "matches"
call :test_one tb_mlp_head "tb_mlp_head.v mlp_head.v systolic_array.v systolic_pe.v mac_q7_8.v relu_q7_8.v" "ALL TESTS PASSED"
call :test_one tb_argmax "tb_argmax.v argmax.v" "PASS"
call :test_one tb_v2_top_fixed "tb_v2_top_fixed.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v argmax.v" "RTL_CYCLES"
call :test_one tb_submission "tb_submission.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v argmax.v" "FINAL SCORECARD: 10/10 PASSED"

echo ========================================================================================
echo  TESTBENCH RUNNER SUMMARY: %PASS_COUNT% PASSED, %FAIL_COUNT% FAILED
echo ========================================================================================
if %FAIL_COUNT% equ 0 (
    echo  ALL 13 ACTIVE VERILOG HARDWARE TESTBENCHES PASSED CLEANLY!
) else (
    echo  WARNING: SOME TESTS FAILED!
)
echo.

pause
exit /b %FAIL_COUNT%

:test_one
set "TB_NAME=%~1"
set "SOURCES=%~2"
set "PASS_PATTERN=%~3"
set "VVP_OUT=docs\review\build\%TB_NAME%.vvp"
set "LOG_OUT=docs\review\logs\%TB_NAME%.txt"

set "FULL_SOURCES="
for %%s in (%SOURCES%) do (
    set "FULL_SOURCES=!FULL_SOURCES! %V_DIR%\%%s"
)

iverilog -g2001 -o "%VVP_OUT%" !FULL_SOURCES! > "%LOG_OUT%" 2>&1
if !errorlevel! neq 0 (
    echo  [FAILED COMPILATION] %TB_NAME%
    set /a FAIL_COUNT+=1
    exit /b 1
)

pushd %V_DIR%
vvp "..\..\%VVP_OUT%" > "..\..\%LOG_OUT%" 2>&1
del /q /f *.vcd 2>nul
popd

findstr /c:"%PASS_PATTERN%" "%LOG_OUT%" >nul
if !errorlevel! equ 0 (
    echo  [PASSED] %TB_NAME%
    set /a PASS_COUNT+=1
) else (
    echo  [FAILED] %TB_NAME%
    set /a FAIL_COUNT+=1
)
exit /b 0
