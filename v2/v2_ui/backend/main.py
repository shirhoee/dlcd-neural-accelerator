from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import tempfile
import asyncio
from typing import List

from schemas import PredictRequest, PredictResponse

app = FastAPI(
    title="DLCD Neural Accelerator API",
    description="Backend API for hardware-in-the-loop digit classification via Icarus Verilog",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def hex16(val: int) -> str:
    """Format signed 16-bit integer into 4-character hex string."""
    return f"{(val & 0xFFFF):04x}"

def parse_signed_str(s: str) -> int:
    """Safely parse signed integer string."""
    try:
        return int(s.strip())
    except ValueError:
        return 0

def downsample_28_to_20(grid_28: List[List[float]]) -> List[List[float]]:
    """Downsample a 28x28 normalized image to 20x20 using nearest-neighbor mapping."""
    grid_20: List[List[float]] = []
    for y in range(20):
        row: List[float] = []
        for x in range(20):
            orig_y = int(y * 28 / 20)
            orig_x = int(x * 28 / 20)
            row.append(grid_28[orig_y][orig_x])
        grid_20.append(row)
    return grid_20

@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest) -> PredictResponse:
    """Run Verilog hardware simulation for the drawn digit."""
    image_28 = payload.image
    image_20 = downsample_28_to_20(image_28)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        txt_path = os.path.join(tmpdir, "test_image_q7_8.txt")
        vvp_path = os.path.join(tmpdir, "vvp_out")
        
        # Write normalized Q7.8 hex test vector
        with open(txt_path, "w") as f:
            for row in image_20:
                for val in row:
                    norm_val = (val - 0.1307) / 0.3081
                    q_val = int(round(norm_val * 256.0))
                    if q_val > 32767:
                        q_val = 32767
                    if q_val < -32768:
                        q_val = -32768
                    f.write(hex16(q_val) + "\n")
                    
        v_dir = os.path.abspath(os.path.join("..", "..", "verilog_src"))
        
        # Compile
        compile_cmd = [
            r"C:\iverilog\bin\iverilog.exe", "-o", vvp_path, "-s", "tb_v2_top_fixed",
            f'-DTEST_IMAGE_FILE="{txt_path.replace(os.sep, "/")}"',
            "tb_v2_top_fixed.v", "v2_top.v", "conv1_array.v", "window_gen.v", "conv_pe.v", 
            "mac_q7_8.v", "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v", 
            "relu_q7_8.v", "conv2_array.v", "conv2_window_gen.v", "conv2_pe.v", 
            "maxpool2_array.v", "pool2_window_gen.v", "mlp_head.v", "systolic_array.v", "systolic_pe.v", "layer_relu.v", "argmax.v"
        ]
        
        comp_res = subprocess.run(
            compile_cmd,
            cwd=v_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if comp_res.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Verilog compilation failed: {comp_res.stderr.decode('utf-8', errors='ignore')}"
            )
        
        # Run
        run_cmd = [r"C:\iverilog\bin\vvp.exe", vvp_path]
        process = subprocess.run(
            run_cmd,
            cwd=v_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Simulation runtime error: {process.stderr.decode('utf-8', errors='ignore')}"
            )
        
        output = process.stdout.decode("utf-8", errors="ignore")
        
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
        input=image_20,
        mp1=mp1,
        mp2=mp2
    )
