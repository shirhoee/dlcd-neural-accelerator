import glob, re

def uses(path, name):
    t = open(path).read()
    # strip comments roughly
    t = re.sub(r"//.*", "", t)
    return name in t

print("layer_relu (v2) instantiated anywhere?", [p for p in glob.glob("v2/verilog_src/*.v") if uses(p, "layer_relu")])
print("dense_array instantiated anywhere?", [p for p in glob.glob("v2/verilog_src/*.v") if uses(p, "dense_array")])
print("dense_pe instantiated anywhere?", [p for p in glob.glob("v2/verilog_src/*.v") if uses(p, "dense_pe")])
print("mac_q6_9 used in v1?", [p for p in glob.glob("v1/verilog_src/*.v") if uses(p, "mac_q6_9")])
print("v2 systolic_array instantiated?", [p for p in glob.glob("v2/verilog_src/*.v") if uses(p, "systolic_array")])

# roms vs python_golden_model duplication
import filecmp
for f in ["weights_q7_8.txt", "conv2_weights_q7_8.txt", "mlp_rom.txt", "dense_weights_q7_8.txt"]:
    a = f"v2/verilog_src/roms/{f}"
    b = f"v2/python_golden_model/{f}"
    try:
        print(f"roms/{f} == python_golden_model/{f}: {filecmp.cmp(a, b, shallow=False)}")
    except FileNotFoundError as e:
        print(f"roms/{f} vs {b}: missing file {e}")
