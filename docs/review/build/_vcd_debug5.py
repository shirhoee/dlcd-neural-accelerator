from pathlib import Path
text = Path("docs/review/wave/wave.vcd").read_text()
scope_stack, out = [], []
targets = ("tb_wave","tb_wave.dut","tb_wave.dut.conv1_inst","tb_wave.dut.dense_inst","tb_wave.dut.argmax_inst")
for tok in text.split("$end"):
    t = tok.strip()
    if t.startswith("$scope"):
        scope_stack.append(t.split()[2])
    elif t.startswith("$upscope"):
        if scope_stack: scope_stack.pop()
    elif t.startswith("$var"):
        cur = ".".join(scope_stack)
        if any(cur == tg or cur.startswith(tg + ".") for tg in targets):
            p = t.split()
            out.append(f"{' '.join(scope_stack)} | {' '.join(p[1:])}")
for line in out:
    print(line)
