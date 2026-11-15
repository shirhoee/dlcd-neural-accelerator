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

for key_id in ["l&","@(","V-","i&","j&",";(","O&","Z","[","R-","T-","Q-","W-"]:
    if key_id in var_id:
        print(key_id, "->", var_id[key_id][0])
    else:
        print(key_id, "-> MISSING from builder paths")
