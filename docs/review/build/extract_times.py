"""Extract review waveform timestamps from docs/review/wave/wave.vcd (timescale 1ps)."""
from pathlib import Path
import re, json

text = Path("docs/review/wave/wave.vcd").read_text()
idx = text.index("$enddefinitions")
lines = text[idx:].splitlines()

MULT = 0.001  # 1ps -> ns
ts = 0
cur = {}          # id -> current value
records = []      # (ts_ns, id, value)
for ln in lines:
    if ln.startswith("#"):
        ts = int(ln[1:]) * MULT
    elif not ln or ln.startswith("$"):
        continue
    elif ln[0] in "01zx":
        vid = ln[1:]
        cur[vid] = 1 if ln[0] == "1" else 0
        records.append((ts, vid, cur[vid]))
    elif ln.startswith("b"):
        mm = re.match(r"b([01xz]+)\s+(\S+)", ln)
        if mm and set(mm.group(1)) <= set("01"):
            vid = mm.group(2)
            cur[vid] = int(mm.group(1), 2)
            records.append((ts, vid, cur[vid]))

by_id = {}
for ts_, vid, v in records:
    by_id.setdefault(vid, []).append((ts_, v))

# id -> signal (from $var parsing)
scope_stack, var_id = [], {}
for tok in text.split("$end"):
    t = tok.strip()
    if t.startswith("$scope"):
        scope_stack.append(t.split()[2])
    elif t.startswith("$upscope") and scope_stack:
        scope_stack.pop()
    elif t.startswith("$var"):
        p = t.split()
        var_id[p[3]] = (".".join(scope_stack + [p[4]]), int(p[2]))
id2path = {vid: h for vid, (h, s) in var_id.items()}

def first_transition(vid, to_val):
    for ts_, v in by_id.get(vid, []):
        if v == to_val:
            return ts_
    return None

def last_value(vid):
    vals = by_id.get(vid, [])
    return vals[-1][1] if vals else None

# id lookup by path
path2id = {h: vid for vid, h in id2path.items()}

ids = {
    "start":        path2id.get("tb_wave.dut.start"),
    "reset":        path2id.get("tb_wave.dut.reset"),
    "c1_valid":     path2id.get("tb_wave.dut.conv1_inst.pe0.valid_out"),  # == conv1_inst.valid_out
    "mp1_valid":    path2id.get("tb_wave.dut.maxpool1_inst.valid_out"),
    "c2_valid":     path2id.get("tb_wave.dut.conv2_inst.gen_pe[0].pe.valid_out"),  # == conv2_inst.valid_out
    "mp2_valid":    path2id.get("tb_wave.dut.maxpool2_inst.valid_out"),
    "d_valid":      path2id.get("tb_wave.dut.dense_inst.valid_out"),
    "done":         path2id.get("tb_wave.dut.argmax_inst.valid_out"),
    "prediction":   path2id.get("tb_wave.dut.argmax_inst.prediction"),
    "pixel_addr":   path2id.get("tb_wave.pixel_addr"),
    "conv1_state":  path2id.get("tb_wave.dut.conv1_inst.state"),
    "conv1_init_cnt": path2id.get("tb_wave.dut.conv1_inst.init_cnt"),
    "pe0_tap_idx":  path2id.get("tb_wave.dut.conv1_inst.pe0.tap_idx"),
    "dense_state":  path2id.get("tb_wave.dut.dense_inst.state"),
    "dense_layer":  path2id.get("tb_wave.dut.dense_inst.layer"),
    "dense_timer":  path2id.get("tb_wave.dut.dense_inst.timer"),
}
for name, vid in ids.items():
    if vid is None:
        print(f"!! {name}: path not found in VCD")

out = {}
out["start_rising_ns"]   = first_transition(ids["start"], 1)
out["reset_first_rise_ns"] = first_transition(ids["reset"], 1)  # reset asserted at t=0
out["c1_valid_first_rise_ns"] = first_transition(ids["c1_valid"], 1)
out["mp1_valid_first_rise_ns"] = first_transition(ids["mp1_valid"], 1)
out["c2_valid_first_rise_ns"] = first_transition(ids["c2_valid"], 1)
out["mp2_valid_first_rise_ns"] = first_transition(ids["mp2_valid"], 1)
out["d_valid_first_rise_ns"]  = first_transition(ids["d_valid"], 1)
out["done_first_rise_ns"]     = first_transition(ids["done"], 1)
pred = last_value(ids["prediction"])
out["final_prediction_raw"] = pred
out["final_prediction_decimal"] = int(pred) if pred is not None else None
out["sim_end_ns"] = records[-1][0]
out["pixel_addr_first_changes"] = by_id.get(ids["pixel_addr"], [])[:6]

# auxiliary FSM/counter snapshots: first few transitions
for name in ["conv1_state","conv1_init_cnt","pe0_tap_idx","dense_state","dense_layer","dense_timer"]:
    vid = ids[name]
    out[name + "_first_transitions"] = by_id.get(vid, [])[:8]

print(json.dumps({k: v for k, v in out.items() if not k.endswith("_first_transitions") and k != "pixel_addr_first_changes"}, indent=2))
print("\nAuxiliary first transitions:")
for name in ["conv1_state","conv1_init_cnt","pe0_tap_idx","dense_state","dense_layer","dense_timer"]:
    print(name, out[name + "_first_transitions"])
print("pixel_addr first changes:", out["pixel_addr_first_changes"])
Path("docs/review/build/wave_times.json").write_text(json.dumps(out, indent=2))
print("\nsaved docs/review/build/wave_times.json")
