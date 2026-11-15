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

want = [
 "tb_wave.clk","tb_wave.reset","tb_wave.start",
 "tb_wave.dut.conv1_inst.state","tb_wave.dut.conv1_inst.init_cnt","tb_wave.dut.conv1_inst.mac_cnt",
 "tb_wave.dut.conv1_inst.valid_out","tb_wave.dut.conv2_inst.valid_out",
 "tb_wave.dut.dense_inst.state","tb_wave.dut.dense_inst.layer","tb_wave.dut.dense_inst.r_idx",
 "tb_wave.dut.dense_inst.c_idx","tb_wave.dut.dense_inst.timer",
 "tb_wave.dut.argmax_inst.done","tb_wave.dut.argmax_inst.prediction",
 "tb_wave.dut.maxpool1_inst.valid_out","tb_wave.dut.maxpool2_inst.valid_out",
 "tb_wave.dut.dense_inst.valid_out",
]
for w in want:
    print(f"{'FOUND' if w in {h for _,(h,_) in var_id.items()} else 'MISSING':7s} {w}")
print()
print("all tb_wave.* (non-dut) paths:")
for vid,(h,s) in var_id.items():
    if h.startswith("tb_wave.") and not h.startswith("tb_wave.dut."):
        print(f"  {vid:>4} [{s:3}] {h}")
