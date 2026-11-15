from pathlib import Path
import re
text = Path("docs/review/wave/wave.vcd").read_text()
idx = text.index("$enddefinitions")
section = text[idx:]
lines = section.splitlines()
ts = 0
mult = 0.001  # 1ps -> ns
records = []
for ln in lines:
    if ln.startswith("#"):
        ts = int(ln[1:]) * mult
    elif ln.startswith("b") or ln == "" or ln.startswith("$"):
        continue
    elif ln[0] in "01zx":
        records.append((ts, ln[1:], ln[0]))
# id t = maxpool1_inst.valid_out
rt = [(ts_, v) for ts_, i, v in records if i == "t"]
print("id t records (first 12):", rt[:12])
print("id t total:", len(rt), "ones:", sum(1 for _,v in rt if v=="1"))
# first rise
rise = next((ts_ for ts_,v in rt if v=="1"), None)
print("first rise of t (ns):", rise)
# timestamp of first # line
first_hash = next((ln for ln in lines if ln.startswith("#")), None)
print("first # line:", first_hash)
print("ts value at end:", ts)
