import os
import subprocess
import tempfile
import asyncio
from typing import List

from config import get_iverilog_executable, get_vvp_executable, VERILOG_SRC_DIR
from preprocessor import quantize_to_q7_8_lines, parse_signed_str
from schemas import PredictResponse

def _run_verilog_simulation_sync(grid_20: List[List[float]]) -> PredictResponse:
    """Synchronous simulation worker executing Icarus Verilog hermetically in tempdir."""
    iverilog_bin = get_iverilog_executable()
    vvp_bin = get_vvp_executable()
    v_dir = str(VERILOG_SRC_DIR)

    with tempfile.TemporaryDirectory() as tmpdir:
        txt_path = os.path.join(tmpdir, "test_image_q7_8.txt")
        vvp_path = os.path.join(tmpdir, "vvp_out")

        hex_lines = quantize_to_q7_8_lines(grid_20)
        with open(txt_path, "w") as f:
            for line in hex_lines:
                f.write(line + "\n")

        compile_cmd = [
            iverilog_bin, "-o", vvp_path, "-s", "tb_v2_top_fixed",
            f'-DTEST_IMAGE_FILE="{txt_path.replace(os.sep, "/")}"',
            "tb_v2_top_fixed.v", "v2_top.v", "conv1_array.v", "window_gen.v", "conv_pe.v",
            "mac_q7_8.v", "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v",
            "relu_q7_8.v", "conv2_array.v", "conv2_window_gen.v", "conv2_pe.v",
            "maxpool2_array.v", "pool2_window_gen.v", "mlp_head.v", "systolic_array.v",
            "systolic_pe.v", "layer_relu.v", "argmax.v"
        ]

        comp_res = subprocess.run(
            compile_cmd,
            cwd=v_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if comp_res.returncode != 0:
            err_msg = comp_res.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Verilog compilation failed: {err_msg}")

        run_cmd = [vvp_bin, vvp_path]
        proc = subprocess.run(
            run_cmd,
            cwd=v_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Simulation runtime execution failed: {err_msg}")

        output = proc.stdout.decode("utf-8", errors="ignore")

        mp1_raw: List[float] = []
        mp2_raw: List[float] = []
        dense1_raw: List[float] = []
        dense2_raw: List[float] = []
        logits_raw: List[float] = []
        pred: int = -1

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("RTL_PRED:"):
                pred = int(line.split(":")[1])
            elif line.startswith("RTL_LOGITS:"):
                logits_str = line.split(":")[1].split(",")
                logits_raw = [parse_signed_str(x) / 256.0 for x in logits_str if x.strip()]
            elif line.startswith("RTL_MP1:"):
                vals = line.split(":")[1].split(",")
                mp1_raw = [parse_signed_str(x) / 256.0 for x in vals if x.strip()]
            elif line.startswith("RTL_MP2:"):
                vals = line.split(":")[1].split(",")
                mp2_raw = [parse_signed_str(x) / 256.0 for x in vals if x.strip()]
            elif line.startswith("RTL_DENSE1:"):
                vals = line.split(":")[1].split(",")
                dense1_raw = [parse_signed_str(x) / 256.0 for x in vals if x.strip()]
            elif line.startswith("RTL_DENSE2:"):
                vals = line.split(":")[1].split(",")
                dense2_raw = [parse_signed_str(x) / 256.0 for x in vals if x.strip()]

    mp1: List[List[List[float]]] = [[[0.0]*10 for _ in range(10)] for _ in range(4)]
    if mp1_raw and len(mp1_raw) >= 400:
        idx = 0
        for y in range(10):
            for x in range(10):
                for c in range(4):
                    mp1[c][y][x] = mp1_raw[idx]
                    idx += 1

    mp2: List[List[List[float]]] = [[[0.0]*5 for _ in range(5)] for _ in range(8)]
    if mp2_raw and len(mp2_raw) >= 200:
        idx = 0
        for y in range(5):
            for x in range(5):
                for c in range(8):
                    mp2[c][y][x] = mp2_raw[idx]
                    idx += 1

    return PredictResponse(
        prediction=pred,
        logits=logits_raw,
        dense1=dense1_raw,
        dense2=dense2_raw,
        input=grid_20,
        mp1=mp1,
        mp2=mp2
    )

async def run_simulation_async(grid_20: List[List[float]]) -> PredictResponse:
    """Non-blocking async runner dispatching simulation execution to worker thread."""
    return await asyncio.to_thread(_run_verilog_simulation_sync, grid_20)
