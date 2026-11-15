"""VCD parser for the review waveform: first-rise timestamps (ns)."""
import re
from pathlib import Path

text = Path("docs/review/wave/wave.vcd").read_text()

m = re.search(r"\$timescale\s+(\S+)\s+(\S+)\s*\$end", text)
num, unit = (m.group(1), m.group(2)) if m else ("1", "ns")
mult = {"s":1e9,"ms":1e6,"us":1e3,"ns":1.0,"ps":0.001,"fs":1e-6}.get(unit.lower(), 1.0)
print(f"Timescale: {num} {unit}  (1 timestamp unit = {mult} ns)")

scope_stack, var_id, order = [], {}, []
for tok in text.split("$end"):
    t = tok.strip()
    if t.startswith("$scope"):
        scope_stack.append(t.split()[2])
    elif t.startswith("$upscope") and scope_stack:
        scope_stack.pop()
    elif t.startswith("$var"):
        p = t.split()
        # p = [$var, type, size, id, name, [range]?]
        name = p[4]
        var_id[p[3]] = (".".join(scope_stack + [name]), int(p[2]))
        order.append(p[3])

print(f"Signals dumped: {len(order)}")

cur, changes, ts = {}, [], 0
in_changes = False
for line in text.splitlines():
    line = line.rstrip("\r")
    if line.startswith("$enddefinitions"):
        in_changes = True; continue
    if not in_changes: continue
    if line.startswith("#"):
        ts = int(line[1:]) * mult; continue
    if not line or line.startswith("$"): continue
    if line.startswith("b"):
        mm = re.match(r"b([01xz]+)\s+(\S+)", line)
        if mm and set(mm.group(1)) <= set("01"):
            vid = mm.group(2)
            cur[vid] = int(mm.group(1), 2); changes.append((ts, vid, cur[vid]))
    elif line[0] in "01zx":
        vid = line[1:]
        cur[vid] = 1 if line[0] == "1" else 0
        changes.append((ts, vid, cur[vid]))

print(f"Value-change records: {len(changes)}")

by_hier = {h: (vid, s) for vid, (h, s) in var_id.items()}
def path(*parts):
    return ".".join(parts)

targets = {
    "start rising":                    path("tb_wave","dut","start"),
    "c1_valid first rise (pe0.valid_out == c1_valid)": path("tb_wave","dut","conv1_inst","pe0","valid_out"),
    "mp1_valid first rise":            path("tb_wave","dut","maxpool1_inst","valid_out"),
    "c2_valid first rise (pe[0].valid_out == c2_valid)": path("tb_wave","dut","conv2_inst","gen_pe[0]","pe","valid_out"),
    "mp2_valid first rise":            path("tb_wave","dut","maxpool2_inst","valid_out"),
    "d_valid rise":                    path("tb_wave","dut","dense_inst","valid_out"),
    "done rise":                       path("tb_wave","dut","argmax_inst","valid_out"),
    "final prediction":                path("tb_wave","dut","argmax_inst","prediction"),
    "pixel_addr":                      path("tb_wave","pixel_addr"),
}
aux = {
    "clk (top)":                       path("tb_wave","clk"),
    "reset (top)":                     path("tb_wave","reset"),
    "conv1 state": path("tb_wave","dut","conv1_inst","state"),
    "conv1 init_cnt": path("tb_wave","dut","conv1_inst","init_cnt"),
    "conv1 mac_cnt": path("tb_wave","dut","conv1_inst","mac_cnt"),
    "pe0 tap_idx": path("tb_wave","dut","conv1_inst","pe0","tap_idx"),
    "dense state": path("tb_wave","dut","dense_inst","state"),
    "dense layer": path("tb_wave","dut","dense_inst","layer"),
    "dense r_idx": path("tb_wave","dut","dense_inst","r_idx"),
    "dense c_idx": path("tb_wave","dut","dense_inst","c_idx"),
    "dense timer": path("tb_wave","dut","dense_inst","timer"),
}

results = {}
for label, full in targets.items():
    if full not in by_hier:
        print(f"!! {label}: {full} NOT in VCD"); continue
    vid, size = by_hier[full]
    rises = [t for t,v,i in changes if i==vid and v==1]
    falls = [t for t,v,i in changes if i==vid and v==0]
    allv = [v for t,v,i in changes if i==vid]
    results[label] = (rises[0] if rises else None, allv[-1] if allv else None)
    print(f"{label:45s} [{size}b] {full}")
    print(f"   first rise = {rises[0] if rises else None} ns   #falls={len(falls)}   final={allv[-1] if allv else None}")

print("\n--- Auxiliary: first transitions ---")
for label, full in aux.items():
    if full not in by_hier:
        print(f"!! {label}: {full} NOT in VCD"); continue
    vid, size = by_hier[full]
    tr = [(t,v) for t,v,i in changes if i==vid][:10]
    print(f"{label:18s} [{size}b] {full}: {tr}")
