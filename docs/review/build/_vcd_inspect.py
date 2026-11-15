import re
t = open("docs/review/wave/wave.vcd").read()
scopes = re.findall(r"\$scope\s+(\S+)\s+(\S+)\s*\$end", t)
print("num scopes:", len(scopes))
print("first 30 scopes:", scopes[:30])
tops = [s for s in scopes if s[1] == "module"]
print("module scopes first 50:", tops[:50])
# do the expected paths exist?
vars_found = re.findall(r"\$var\s+\S+\s+\d+\s+(\S+)\s+([^\s$]+)\s*\$end", t)
names = [n for _, n in vars_found]
print("num vars:", len(names))
for probe in ["tb_wave", "dut", "conv1_inst", "maxpool1_inst", "conv2_inst", "maxpool2_inst",
              "dense_inst", "argmax_inst", "clk", "reset", "start", "pixel_addr", "done",
              "prediction", "valid_out"]:
    hits = [n for n in names if n == probe]
    print(f"{probe:18s} exact-name vars: {len(hits)}")
