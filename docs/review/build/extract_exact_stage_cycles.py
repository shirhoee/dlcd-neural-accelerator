import re
from pathlib import Path

text = Path("docs/review/wave/wave.vcd").read_text()
m = re.search(r"\$timescale\s+(\S+)\s+(\S+)\s*\$end", text)
num, unit = (m.group(1), m.group(2)) if m else ("1", "ns")
mult = {"s":1e9,"ms":1e6,"us":1e3,"ns":1.0,"ps":0.001,"fs":1e-6}.get(unit.lower(), 1.0)

scope_stack, var_id = [], {}
for tok in text.split("$end"):
    t = tok.strip()
    if t.startswith("$scope"):
        scope_stack.append(t.split()[2])
    elif t.startswith("$upscope") and scope_stack:
        scope_stack.pop()
    elif t.startswith("$var"):
        p = t.split()
        name = p[4]
        var_id[p[3]] = (".".join(scope_stack + [name]), int(p[2]))

by_hier = {h: vid for vid, (h, s) in var_id.items()}

signals = {
    "start": by_hier.get("tb_wave.dut.start"),
    "c1_valid": by_hier.get("tb_wave.dut.conv1_inst.pe0.valid_out"),
    "mp1_valid": by_hier.get("tb_wave.dut.maxpool1_inst.valid_out"),
    "c2_valid": by_hier.get("tb_wave.dut.conv2_inst.gen_pe[0].pe.valid_out"),
    "mp2_valid": by_hier.get("tb_wave.dut.maxpool2_inst.valid_out"),
    "d_valid": by_hier.get("tb_wave.dut.dense_inst.valid_out"),
    "done": by_hier.get("tb_wave.dut.done"),
    "dense_state": by_hier.get("tb_wave.dut.dense_inst.state")
}

first_rise = {}
last_rise = {}
last_fall = {}

in_changes = False
ts = 0
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
            val = int(mm.group(1), 2)
            if vid == signals["dense_state"] and val == 1 and "dense_state_1" not in first_rise:
                first_rise["dense_state_1"] = ts
    elif line[0] in "01":
        val = int(line[0])
        vid = line[1:]
        for signame, svid in signals.items():
            if vid == svid:
                if val == 1:
                    if signame not in first_rise:
                        first_rise[signame] = ts
                    last_rise[signame] = ts
                elif val == 0:
                    last_fall[signame] = ts

start_ts = first_rise.get("start", 25.0)
print(f"Base start_ts: {start_ts} ns")
for k in ["start", "c1_valid", "mp1_valid", "c2_valid", "mp2_valid", "dense_state_1", "d_valid", "done"]:
    fr = first_rise.get(k, 0)
    lr = last_rise.get(k, 0)
    lf = last_fall.get(k, 0)
    print(f"{k:15}: first_rise={fr:7.1f} ns (cyc={(fr-start_ts)/10:6.1f}) | last_rise={lr:7.1f} ns (cyc={(lr-start_ts)/10:6.1f}) | last_fall={lf:7.1f} ns (cyc={(lf-start_ts)/10:6.1f})")
