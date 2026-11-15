@echo off
setlocal enabledelayedexpansion
mode con cols=100 lines=45

rem ---- Toolchain detection via `where` ----
where iverilog >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\iverilog\bin\iverilog.exe" (
        set "PATH=C:\iverilog\bin;%PATH%"
    ) else (
        echo [ERROR] iverilog not found on PATH or C:\iverilog\bin.
        pause
        exit /b 1
    )
)
where python >nul 2>&1
if %errorlevel% equ 0 (set PY=python) else (set PY=py)

set ROOT=%CD%
set VSRC=v2\verilog_src
set REG=v2\regression
set BUILD=..\..\docs\review\build

rem ================================================================================
rem  STEP 1: tb_submission - 10-Digit Hardware Verification (PES UE25CS251A)
rem ================================================================================
cls
echo ================================================================================
echo  STEP 1 OF 5 - tb_submission: 10-Digit Hardware Verification Suite
echo ================================================================================
echo  COMMAND: iverilog -g2001 -o docs\review\build\tb_submission.vvp [sources]
echo           vvp docs\review\build\tb_submission.vvp
echo --------------------------------------------------------------------------------
pushd "%VSRC%"
iverilog -g2001 -o "!BUILD!\tb_submission.vvp" tb_submission.v v2_top.v conv1_array.v window_gen.v conv_pe.v mac_q7_8.v maxpool_array.v pool_window_gen.v maxpool_pe.v relu_q7_8.v conv2_array.v conv2_window_gen.v conv2_pe.v maxpool2_array.v pool2_window_gen.v mlp_head.v systolic_array.v systolic_pe.v argmax.v >nul 2>&1
vvp "!BUILD!\tb_submission.vvp"
del /q /f *.vcd 2>nul
popd
echo.
echo [SCREENSHOT READY: Press Alt+PrtScn or Win+Shift+S to capture Fig 7.1]
echo.
pause

rem ================================================================================
rem  STEP 2: test_10.py - 10-Image RTL vs Q7.8 Emulator Hardware Regression
rem ================================================================================
cls
echo ================================================================================
echo  STEP 2 OF 5 - test_10.py: 10-Image RTL vs Q7.8 Emulator Hardware Regression
echo ================================================================================
echo  COMMAND: cd v2\regression ^&^& python test_10.py
echo --------------------------------------------------------------------------------
pushd "%REG%"
!PY! test_10.py
popd
echo.
echo [SCREENSHOT READY: Press Alt+PrtScn or Win+Shift+S to capture Fig 7.2]
echo.
pause

rem ================================================================================
rem  STEP 3: 10,000-Image Full Test Set Emulator & Float32 Baseline Summary
rem ================================================================================
cls
echo ================================================================================
echo  STEP 3 OF 5 - Full 10,000-Image Test Set Q7.8 Emulator Evaluation Summary
echo ================================================================================
echo  COMMAND: python docs\review\build\eval_emu_10k.py
echo --------------------------------------------------------------------------------
if exist "docs\review\build\emu_10k_results.json" (
    !PY! -c "import json; d=json.load(open('docs/review/build/emu_10k_results.json')); print('--- 10,000-IMAGE EVALUATION SUMMARY ---'); print('Total Test Images    :', d['total_images']); print('PyTorch Float32 Acc  :', d['pt_accuracy_pct'], f'({d[\"pt_correct\"]}/10000)'); print('Q7.8 Int Emulator Acc:', d['emu_accuracy_pct'], f'({d[\"emu_correct\"]}/10000)'); print('F32 vs Q7.8 Disagreed:', d['disagreements']); print('Confusion Matrix Saved: docs/review/confusion_matrix.png'); print('Per-Class Accuracy:'); [print(f'  Digit {r[\"class\"]}: {r[\"accuracy_pct\"]} ({r[\"correct\"]}/{r[\"total\"]})') for r in d['per_class']]"
) else (
    echo [Running 10,000-image evaluation across threads...]
    !PY! docs\review\build\eval_emu_10k.py
)
echo.
echo [SCREENSHOT READY: Press Alt+PrtScn or Win+Shift+S to capture Fig 7.3]
echo.
pause

rem ================================================================================
rem  STEP 4: run_all_tests.bat - All 13 Active Hardware Testbenches
rem ================================================================================
cls
echo ================================================================================
echo  STEP 4 OF 5 - run_all_tests.bat: Active Verilog Testbench Suite
echo ================================================================================
echo  COMMAND: run_all_tests.bat
echo --------------------------------------------------------------------------------
cmd /c "echo. | run_all_tests.bat"
echo.
echo [SCREENSHOT READY: Press Alt+PrtScn or Win+Shift+S to capture Fig 7.4]
echo.
pause

rem ================================================================================
rem  STEP 5: tb_mlp_head - Time-Multiplexed 16x16 Systolic Dense Head Unit Verification
rem ================================================================================
cls
echo ================================================================================
echo  STEP 5 OF 5 - tb_mlp_head: Time-Multiplexed Systolic Array Unit Verification
echo ================================================================================
echo  COMMAND: iverilog -g2001 -o docs\review\build\tb_mlp_head.vvp [sources]
echo           vvp docs\review\build\tb_mlp_head.vvp
echo --------------------------------------------------------------------------------
pushd "%VSRC%"
iverilog -g2001 -o "!BUILD!\tb_mlp_head.vvp" tb_mlp_head.v mlp_head.v systolic_array.v systolic_pe.v mac_q7_8.v relu_q7_8.v >nul 2>&1
vvp "!BUILD!\tb_mlp_head.vvp"
del /q /f *.vcd 2>nul
popd
echo.
echo [SCREENSHOT READY: Press Alt+PrtScn or Win+Shift+S to capture Fig 7.5]
echo.
pause
