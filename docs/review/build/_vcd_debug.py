import re
from pathlib import Path
text = Path("docs/review/wave/wave.vcd").read_text()

# Build id->path using scope stack over $split("$end") tokens
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

# find ids for specific paths
want = ["tb_wave.start", "tb_wave.clk", "tb_wave.dut.conv1_inst.valid_out",
        "tb_wave.dut.maxpool1_inst.valid_out", "tb_wave.dut.argmax_inst.done",
        "tb_wave.dut.argmax_inst.prediction", "tb_wave.dut.conv1_inst.state",
        "tb_wave.dut.conv1_inst.pe0.tap_idx", "tb_wave.dut.dense_inst.timer"]
id_by_path = {h: vid for vid, (h, s) in var_id.items()}
for w in want:
    print(f"{w:55s} -> id={id_by_path.get(w)!r}")

# show paths that end with '.start'
print("\npaths ending in .start:")
for vid,(h,s) in var_id.items():
    if h.endswith(".start") or h == "start":
        print("  ", h, repr(vid))

# raw change records near the beginning of the value section
idx = text.index("$enddefinitions")
section = text[idx:]
lines = section.splitlines()
print("\nfirst 40 change lines:")
cnt = 0
for ln in lines:
    if ln.startswith("#"):
        continue
    if ln and not ln.startswith("$"):
        print("  ", repr(ln))
        cnt += 1
        if cnt >= 40: break
