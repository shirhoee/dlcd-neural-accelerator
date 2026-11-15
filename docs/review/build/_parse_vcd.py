"""Minimal VCD parser: first-rise timestamps of named signals (ns)."""
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
        var_id[p[3]] = (".".join(scope_stack + p[4:]), int(p[2]))
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
            cur[mm.group(2)] = int(mm.group(1), 2); changes.append((ts, mm.group(2), cur[mm.group(2)]))
    elif line[0] in "01zx":
        cur[line[1:]] = 1 if line[0] == "1" else 0
        changes.append((ts, line[1:], cur[line[1:]]))

print(f"Value-change records: {len(changes)}")

by_hier = {h: (vid, s) for vid, (h, s) in var_id.items()}
def path(*parts):
    return ".".join(parts)

targets = {
    "start rising":                    path("tb_wave","start"),
    "c1_valid first rise":             path("tb_wave","dut","conv1_inst","valid_out"),
    "mp1_valid first rise":            path("tb_wave","dut","maxpool1_inst","valid_out"),
    "c2_valid first rise":             path("tb_wave","dut","conv2_inst","valid_out"),
    "mp2_valid first rise":            path("tb_wave","dut","maxpool2_inst","valid_out"),
    "d_valid rise":                    path("tb_wave","dut","dense_inst","valid_out"),
    "done rise":                       path("tb_wave","dut","argmax_inst","done"),
    "final prediction":                path("tb_wave","dut","argmax_inst","prediction"),
}
aux = {
    "conv1 state": path("tb_wave","dut","conv1_inst","state"),
    "conv1 init_cnt": path("tb_wave","dut","conv1_inst","init_cnt"),
    "conv1 mac_cnt": path("tb_wave","dut","conv1_inst","mac_cnt"),
    "pe0 tap_idx": path("tb_wave","dut","conv1_inst","pe0","tap_idx"),
    "pe0 valid_out": path("tb_wave","dut","conv1_inst","pe0","valid_out"),
    "dense state": path("tb_wave","dut","dense_inst","state"),
    "dense layer": path("tb_wave","dut","dense_inst","layer"),
    "dense r_idx": path("tb_wave","dut","dense_inst","r_idx"),
    "dense c_idx": path("tb_wave","dut","dense_inst","c_idx"),
    "dense timer": path("tb_wave","dut","dense_inst","timer"),
}

results = {}
for label, full in targets.items():
    if full not in by_hier:
        print(f"!! {label}: signal {full} NOT in VCD"); continue
    vid, size = by_hier[full]
    rises = [t for t,v,i in changes if i==vid and v==1]
    falls = [t for t,v,i in changes if i==vid and v==0]
    final = [v for t,v,i in changes if i==vid][-1] if any(i==vid for t,v,i in changes) else None
    results[label] = (rises[0] if rises else None, final)
    print(f"{label:28s} [{size}b] {full}")
    print(f"   first rise = {rises[0] if rises else None} ns   falls={len(falls)}   final={final}")

print("\n--- Auxiliary signals (first few transitions) ---")
for label, full in aux.items():
    if full not in by_hier:
        print(f"!! {label}: {full} NOT in VCD"); continue
    vid, size = by_hier[full]
    tr = [(t,v) for t,v,i in changes if i==vid][:8]
    print(f"{label:16s} [{size}b] {full}: {tr}")
