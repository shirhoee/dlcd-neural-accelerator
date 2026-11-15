# Phase 2 execution harness: compile every V2 testbench with iverilog -g2001 -Wall
# .vvp outputs go to docs/review/build/ ; raw simulation output to docs/review/logs/
# Runs are executed from v2/verilog_src so that relative $readmemh paths resolve.
# This script creates ONLY new files under docs/review/. Existing repo files are never modified.

$ErrorActionPreference = "Continue"
$root = "C:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator"
$vsrc = Join-Path $root "v2\verilog_src"
$build = Join-Path $root "docs\review\build"
$logs  = Join-Path $root "docs\review\logs"
$iverilog = "C:\iverilog\bin\iverilog.exe"
$vvp      = "C:\iverilog\bin\vvp.exe"

Set-Location $vsrc

$common18 = @(
    "v2_top.v", "conv1_array.v", "window_gen.v", "conv_pe.v", "mac_q7_8.v",
    "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v", "relu_q7_8.v",
    "conv2_array.v", "conv2_window_gen.v", "conv2_pe.v",
    "maxpool2_array.v", "pool2_window_gen.v", "mlp_head.v",
    "systolic_array.v", "systolic_pe.v", "layer_relu.v", "argmax.v"
)

$tests = @{
    "tb_conv_pe"             = @("tb_conv_pe.v", "conv_pe.v", "mac_q7_8.v");
    "tb_window_gen"          = @("tb_window_gen.v", "window_gen.v");
    "tb_pool_window_gen"     = @("tb_pool_window_gen.v", "pool_window_gen.v");
    "tb_maxpool_pe"          = @("tb_maxpool_pe.v", "maxpool_pe.v");
    "tb_maxpool_array"       = @("tb_maxpool_array.v", "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v", "relu_q7_8.v");
    "tb_maxpool2_array"      = @("tb_maxpool2_array.v", "maxpool2_array.v", "pool2_window_gen.v", "maxpool_pe.v", "relu_q7_8.v");
    "tb_conv1_array"         = @("tb_conv1_array.v", "conv1_array.v", "window_gen.v", "conv_pe.v", "mac_q7_8.v");
    "tb_conv1_maxpool_chain" = @("tb_conv1_maxpool_chain.v", "conv1_array.v", "window_gen.v", "conv_pe.v", "mac_q7_8.v", "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v", "relu_q7_8.v");
    "tb_conv2_array"         = @("tb_conv2_array.v", "conv2_array.v", "conv2_window_gen.v", "conv2_pe.v", "mac_q7_8.v");
    "tb_mlp_head"            = @("tb_mlp_head.v", "mlp_head.v", "systolic_array.v", "systolic_pe.v", "mac_q7_8.v", "relu_q7_8.v", "layer_relu.v");
    "tb_argmax"              = @("tb_argmax.v", "argmax.v");
    "tb_dense_array"         = @("tb_dense_array.v", "dense_array.v", "dense_pe.v", "mac_q7_8.v");
    "tb_v2_top"              = $common18 + @("tb_v2_top.v");
    "tb_v2_top_fixed"        = $common18 + @("tb_v2_top_fixed.v");
    "tb_submission"          = $common18 + @("tb_submission.v");
}

function Compile-Testbench {
    param([string]$Name, [string[]]$Files)
    $vvpOut = Join-Path $build "$Name.vvp"
    $log    = Join-Path $logs "compile_$Name.txt"
    $args   = @("-g2001", "-Wall", "-o", $vvpOut) + $Files
    & $iverilog $args > $log 2>&1
    $rc = $LASTEXITCODE
    return @{ rc=$rc; vvp=$vvpOut; log=$log }
}

function Run-Vvp {
    param([string]$Name, [string]$VvpPath, [int]$TimeoutSec=60)
    $log = Join-Path $logs "$Name.txt"
    $tmp = Join-Path $logs "$Name.run.tmp"
    $p = Start-Process -FilePath $vvp -ArgumentList @(Resolve-Path $VvpPath) -WorkingDirectory $vsrc `
        -RedirectStandardOutput $tmp -RedirectStandardError "$tmp.err" -PassThru
    if (-not ($p.WaitForExit($TimeoutSec * 1000))) {
        $p.Kill()
        "*** SIMULATION TIMEOUT after $TimeoutSec s ***" | Out-File -FilePath $tmp -Append
        return @{ rc = -1; timedout = $true }
    }
    # Append run output after compile output in the same log file
    if (Test-Path $tmp) { Get-Content $tmp -Raw | Out-File -FilePath $log -Append }
    if (Test-Path "$tmp.err") { Get-Content "$tmp.err" -Raw | Out-File -FilePath $log -Append }
    Remove-Item $tmp -ErrorAction SilentlyContinue
    Remove-Item "$tmp.err" -ErrorAction SilentlyContinue
    return @{ rc = $p.ExitCode; timedout = $false }
}

$results = @{}
foreach ($name in $tests.Keys) {
    $files = $tests[$name]
    Write-Host "=== Compiling $name ==="
    $c = Compile-Testbench $name $files
    $results[$name] = $c
    if ($c.rc -ne 0) {
        Write-Host "COMPILE FAILED: $name`n" (Get-Content $c.log -Raw)
        continue
    }
    Write-Host "=== Running $name ==="
    $r = Run-Vvp $name $c.vvp 120
    $results[$name] | Add-Member -MemberType NoteProperty -Name run -Value $r -Force
    if ($r.timedout) { Write-Host "TIMEOUT: $name" }
    else { Write-Host "EXIT $($r.rc): $name" }
}

Write-Host "`n=== SUMMARY ==="
foreach ($name in $tests.Keys) {
    $c = $results[$name]
    $state = if ($c.rc -ne 0) { "COMPILE FAILED" } elseif ($c.run.timedout) { "RUN TIMEOUT" } else { "OK rc=$($c.run.rc)" }
    Write-Host "$name : $state"