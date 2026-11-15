import re
from pathlib import Path
text = Path("docs/review/wave/wave.vcd").read_text()
scope_stack, var_id = [], {}
for tok in text.split("$end"):
    t = tok.strip()
    if t.startswith("$scope"):
        scope_stack.append(t.split()[2])
    elif t.startswith("$upscope") and scope_stack:
        scope_stack.pop()
    elif t.startswith("$var"):
        p = t.split()
        var_id[p[3]] = (".".join(scope_stack + p[4:]), int(p[2]))

print("=== paths under tb_wave.dut (first 60) ===")
n = 0
for vid,(h,s) in var_id.items():
    if h.startswith("tb_wave.dut."):
        print(f"  {vid:>4} [{s:3}] {h}")
        n += 1
        if n >= 60: break
print("total tb_wave.dut.*:", sum(1 for h in var_id.values() if h[0].startswith("tb_wave.dut.")))

print("\n=== root-level paths (no dots) ===")
for vid,(h,s) in var_id.items():
    if "." not in h:
        print(f"  {vid:>4} [{s:3}] {h}")

print("\n=== all .valid_out paths ===")
for vid,(h,s) in var_id.items():
    if h.endswith("valid_out"):
        print(f"  {vid:>4} [{s:3}] {h}")

print("\n=== all .done / .prediction / .state / .timer / .tap_idx / .start ===")
for vid,(h,s) in var_id.items():
    b = h.split(".")[-1]
    if b in ("done","prediction","state","timer","tap_idx","start","init_cnt","mac_cnt","layer","r_idx","c_idx"):
        print(f"  {vid:>4} [{s:3}] {h}")
