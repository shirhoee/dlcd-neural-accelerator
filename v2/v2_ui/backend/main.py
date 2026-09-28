from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def hex16(val):
    return f"{(val & 0xFFFF):04x}"

def parse_signed_hex(h):
    val = int(h, 16)
    return val if val < 32768 else val - 65536

def downsample_28_to_20(grid_28):
    grid_20 = []
    for y in range(20):
        row = []
        for x in range(20):
            orig_y = int(y * 28 / 20)
            orig_x = int(x * 28 / 20)
            row.append(grid_28[orig_y][orig_x])
        grid_20.append(row)
    return grid_20

@app.post("/predict")
async def predict(request: Request):
    data = await request.json()
    image_28 = data.get("image")
    
    image_20 = downsample_28_to_20(image_28)
    
    txt_path = os.path.join("..", "..", "python_golden_model", "test_image_q7_8.txt")
    with open(txt_path, "w") as f:
        for row in image_20:
            for val in row:
                q_val = int(round(val * 256.0))
                if q_val > 32767: q_val = 32767
                if q_val < -32768: q_val = -32768
                f.write(hex16(q_val) + "\n")
                
    v_dir = os.path.join("..", "..", "verilog_src")
    subprocess.run(["C:\\iverilog\\bin\\vvp.exe", "top_test"], cwd=v_dir)
    
    def read_hex_log(filename):
        path = os.path.join("logs", filename)
        if not os.path.exists(path): return []
        tokens = []
        with open(path, "r") as f:
            for line in f:
                line = line.split("//")[0]
                for token in line.split():
                    if token.startswith('@'): continue
                    tokens.append(token)
        return [parse_signed_hex(t) / 256.0 for t in tokens]

    mp1_raw = read_hex_log("mp1_cap.txt")
    mp2_raw = read_hex_log("mp2_cap.txt")
    logits_raw = read_hex_log("logits_cap.txt")
    
    mp1 = [[[0]*10 for _ in range(10)] for _ in range(4)]
    if mp1_raw:
        idx = 0
        for y in range(10):
            for x in range(10):
                for c in range(4):
                    mp1[c][y][x] = mp1_raw[idx]
                    idx += 1
                    
    mp2 = [[[0]*5 for _ in range(5)] for _ in range(8)]
    if mp2_raw:
        idx = 0
        for y in range(5):
            for x in range(5):
                for c in range(8):
                    mp2[c][y][x] = mp2_raw[idx]
                    idx += 1
                    
    pred = -1
    if logits_raw:
        pred = logits_raw.index(max(logits_raw))
        
    return {
        "prediction": pred,
        "logits": logits_raw,
        "input": image_20,
        "mp1": mp1,
        "mp2": mp2
    }
