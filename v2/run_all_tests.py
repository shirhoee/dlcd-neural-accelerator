import os
import subprocess
import glob

v1_dir = "v1/verilog_src"
v2_dir = "v2/verilog_src"
iverilog = r"C:\iverilog\bin\iverilog.exe"
vvp = r"C:\iverilog\bin\vvp.exe"

testbenches = []

# Find all tb_*.v
v1_tbs = glob.glob(os.path.join(v1_dir, "tb_*.v"))
v2_tbs = glob.glob(os.path.join(v2_dir, "tb_*.v"))

def run_tb(tb_path):
    d = os.path.dirname(tb_path)
    f = os.path.basename(tb_path)
    out_bin = f.replace(".v", ".vvp")
    
    # Try to find what module it covers
    with open(tb_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We won't recompile if we don't have all source files easily.
    # We will just run the existing binary if it exists.
    # In V1, binaries are .vvp. In V2, they are _test or top_test etc.
    # But wait, let's just see if we can find existing binaries based on modified time or names.
    pass

# Instead of complex logic, I'll just look for known compiled files and run them.
print("--- V1 Tests ---")
for vvp_file in glob.glob(os.path.join(v1_dir, "*.vvp")):
    print(f"Running {os.path.basename(vvp_file)}...")
    res = subprocess.run([vvp, os.path.basename(vvp_file)], cwd=v1_dir, capture_output=True, text=True)
    out_lines = res.stdout.strip().split('\n')
    last_line = out_lines[-1] if out_lines else "NO OUTPUT"
    if len(out_lines) >= 2 and "$finish called" in last_line:
        last_line = out_lines[-2]
    print(f"Result: {last_line}")

print("\n--- V2 Tests ---")
# V2 compiled files don't have an extension, but they are known from list_dir:
v2_bins = [
    "chain_test", "conv1_array_test", "conv2_test", "conv_pe_test",
    "maxpool_pe_test", "pool_gen_test", "standalone_test", "top_test", "window_gen_test"
]
for b in v2_bins:
    bin_path = os.path.join(v2_dir, b)
    if os.path.exists(bin_path):
        print(f"Running {b}...")
        res = subprocess.run([vvp, b], cwd=v2_dir, capture_output=True, text=True)
        out_lines = res.stdout.strip().split('\n')
        last_line = out_lines[-1] if out_lines else "NO OUTPUT"
        if len(out_lines) >= 2 and "$finish called" in last_line:
            last_line = out_lines[-2]
        print(f"Result: {last_line}")
