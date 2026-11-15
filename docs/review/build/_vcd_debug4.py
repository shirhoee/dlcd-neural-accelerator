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

for probe in ["state","init_cnt","mac_cnt","done","prediction","layer","r_idx","c_idx","timer","clk","reset","valid_out"]:
    hits = [(vid,h,s) for vid,(h,s) in var_id.items() if h.split(".")[-1]==probe]
    print(f"--- {probe}: {len(hits)} vars ---")
    for vid,h,s in hits[:12]:
        print(f"    {vid:>4} [{s:3}] {h}")
