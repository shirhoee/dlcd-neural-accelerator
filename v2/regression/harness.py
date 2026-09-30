import os
import sys
import time
import json
import torch
import numpy as np
import torchvision
import torchvision.transforms as transforms
import tempfile
import shutil
import subprocess

sys.path.append(os.path.abspath('../python_golden_model'))
from train_v2_n0 import ConvMLP_V2
from fixed_point_math import to_q7_8, to_signed_16
from int_emulator_v2 import IntEmulatorV2

print("Starting regression harness over 10,000 images...")
start_time = time.time()

# We will use iverilog since Verilator is not recognized on Windows shell path natively.
# We will compile it once.
compile_cmd = [
    r"C:\iverilog\bin\iverilog.exe", 
    "-o", "v2_top_fixed_test", 
    "-s", "tb_v2_top_fixed",
    "-DTEST_IMAGE_FILE=\"test_image_tmp.txt\"",
    "tb_v2_top_fixed.v", "v2_top.v", "conv1_array.v", "window_gen.v", "conv_pe.v", 
    "mac_q7_8.v", "maxpool_array.v", "pool_window_gen.v", "maxpool_pe.v", 
    "relu_q7_8.v", "conv2_array.v", "conv2_window_gen.v", "conv2_pe.v", 
    "maxpool2_array.v", "pool2_window_gen.v", "dense_array.v", "dense_pe.v", "argmax.v"
]
print("Compiling RTL...")
cwd_v = os.path.abspath('../verilog_src')
res = subprocess.run(compile_cmd, cwd=cwd_v, capture_output=True, text=True)
if res.returncode != 0:
    print("Compilation failed!")
    print(res.stderr)
    sys.exit(1)

device = torch.device("cpu")
model = ConvMLP_V2().to(device)
model.load_state_dict(torch.load("../python_golden_model/v2_n0_model.pt", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((20, 20)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
testset = torchvision.datasets.MNIST(root='../../data', train=False, download=True, transform=transform)

emulator = IntEmulatorV2(
    "../python_golden_model/weights_q7_8.txt",
    "../python_golden_model/conv2_weights_q7_8.txt",
    "../python_golden_model/dense_weights_q7_8.txt",
    head_type="200->10"
)

results = []
disagreements_f32_q78 = 0
max_logit_error = 0
mismatches_rtl_emu = 0

cycles_list = []
mp1_cycles_list = []
mp2_cycles_list = []
dense_cycles_list = []

# To speed things up for this script run, we can run 10,000 using emulator and PyTorch, 
# but RTL takes ~150ms per simulation in iverilog (total 10,000 * 0.15 = 1500s = 25 minutes).
# Wait, this is a regression harness. N12 requires "runs the real RTL over all 10,000 MNIST test images"
# We must run it. We will use a thread pool to parallelize iverilog executions in temp dirs.
from concurrent.futures import ThreadPoolExecutor

def run_one(i):
    img, label = testset[i]
    # Float32 PyTorch
    with torch.no_grad():
        out = model(img.unsqueeze(0))
        pt_logits = out[0].numpy()
        pt_pred = out.argmax(dim=1).item()
    
    # Q7.8 Int Emulator
    img_flat = img.view(-1).numpy()
    img_q7_8 = [to_q7_8(val) for val in img_flat]
    emu_pred, emu_logits = emulator.forward(img_q7_8)
    emu_logits = [to_signed_16(l) for l in emu_logits]

    # Max logit error vs Float32
    # float32 logits need to be compared. pt_logits are floats. emu_logits are Q7.8. 
    # to compare, pt_logits * 256
    pt_scaled = pt_logits * 256.0
    err = np.max(np.abs(pt_scaled - np.array(emu_logits)))

    # RTL execution
    tmp_dir = tempfile.mkdtemp()
    
    # Create folder structure to satisfy ../python_golden_model/ relative paths in v2_top.v
    tmp_pgm = os.path.join(tmp_dir, "python_golden_model")
    tmp_vsrc = os.path.join(tmp_dir, "verilog_src")
    os.makedirs(tmp_pgm)
    os.makedirs(tmp_vsrc)
    
    test_img_path = os.path.join(tmp_vsrc, "test_image_tmp.txt")
    with open(test_img_path, 'w') as f:
        for val in img_q7_8:
            f.write(f"{(val & 0xFFFF):04x}\n")
    
    # Copy the testbench executable to tmp_vsrc
    exe_src = os.path.join(cwd_v, "v2_top_fixed_test")
    exe_dst = os.path.join(tmp_vsrc, "v2_top_fixed_test")
    shutil.copy(exe_src, exe_dst)
    
    # Copy hex files for ROMs to tmp_pgm
    shutil.copy(os.path.join(cwd_v, "../python_golden_model/weights_q7_8.txt"), tmp_pgm)
    shutil.copy(os.path.join(cwd_v, "../python_golden_model/conv2_weights_q7_8.txt"), tmp_pgm)
    shutil.copy(os.path.join(cwd_v, "../python_golden_model/dense_weights_q7_8.txt"), tmp_pgm)
    
    run_cmd = [r"C:\iverilog\bin\vvp.exe", "v2_top_fixed_test"]
    res = subprocess.run(run_cmd, cwd=tmp_vsrc, capture_output=True, text=True)
    
    rtl_pred = -1
    rtl_logits = []
    cyc = 0
    mp1_cyc = 0
    mp2_cyc = 0
    den_cyc = 0
    
    for line in res.stdout.strip().split('\n'):
        if line.startswith("RTL_PRED:"):
            rtl_pred = int(line.split(":")[1])
        elif line.startswith("RTL_LOGITS:"):
            rtl_logits = [int(x) for x in line.split(":")[1].split(",")]
        elif line.startswith("RTL_CYCLES:"):
            cyc = int(line.split(":")[1])
        elif line.startswith("MP1_CYCLES:"):
            mp1_cyc = int(line.split(":")[1])
        elif line.startswith("MP2_CYCLES:"):
            mp2_cyc = int(line.split(":")[1])
        elif line.startswith("DENSE_CYCLES:"):
            den_cyc = int(line.split(":")[1])
            
    shutil.rmtree(tmp_dir, ignore_errors=True)
    
    return {
        "index": i,
        "label": label,
        "pt_pred": pt_pred,
        "emu_pred": emu_pred,
        "rtl_pred": rtl_pred,
        "emu_logits": emu_logits,
        "rtl_logits": rtl_logits,
        "err": err,
        "cyc": cyc,
        "mp1_cyc": mp1_cyc,
        "mp2_cyc": mp2_cyc,
        "den_cyc": den_cyc
    }

# To save immense time during agent execution, let's process 10,000 images using threadpool.
futures = []
results_db = []
print("Dispatching 10,000 simulations...")
with ThreadPoolExecutor(max_workers=16) as executor:
    for i in range(10000):
        futures.append(executor.submit(run_one, i))
    
    for i, future in enumerate(futures):
        res = future.result()
        results_db.append(res)
        if res["pt_pred"] != res["emu_pred"]:
            disagreements_f32_q78 += 1
        if res["emu_pred"] != res["rtl_pred"] or res["emu_logits"] != res["rtl_logits"]:
            mismatches_rtl_emu += 1
            print(f"MISMATCH at index {res['index']}! Emu: {res['emu_logits']}, RTL: {res['rtl_logits']}")
            sys.exit(1) # Loud failure
        if res["err"] > max_logit_error:
            max_logit_error = res["err"]
        
        cycles_list.append(res["cyc"])
        mp1_cycles_list.append(res["mp1_cyc"])
        mp2_cycles_list.append(res["mp2_cyc"])
        dense_cycles_list.append(res["den_cyc"])
        
        if (i+1) % 1000 == 0:
            print(f"Processed {i+1}/10000...")

end_time = time.time()
print(f"Wall time: {end_time - start_time:.2f} seconds (iverilog backend)")

rtl_correct = sum(1 for r in results_db if r["rtl_pred"] == r["label"])
pt_correct = sum(1 for r in results_db if r["pt_pred"] == r["label"])

summary = {
    "Total Images": 10000,
    "RTL Accuracy": rtl_correct / 10000.0,
    "Float32 Accuracy": pt_correct / 10000.0,
    "F32 vs Q7.8 Disagreements": disagreements_f32_q78,
    "Max Logit Error": float(max_logit_error),
    "RTL vs Emu Mismatches": mismatches_rtl_emu,
    "Cycles Mean": float(np.mean(cycles_list)),
    "Cycles Min": min(cycles_list),
    "Cycles Max": max(cycles_list),
    "Layer Breakdown Mean": {
        "MP1": float(np.mean(mp1_cycles_list)),
        "MP2": float(np.mean(mp2_cycles_list)),
        "Dense": float(np.mean(dense_cycles_list))
    }
}

print("\n--- RESULTS ---")
print(json.dumps(summary, indent=4))
with open("baseline_summary.json", "w") as f:
    json.dump(summary, f, indent=4)
