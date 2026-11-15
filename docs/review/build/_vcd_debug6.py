t = open("docs/review/wave/wave.vcd").read()
vs = [l for l in t.split("\n") if l.startswith("$var")]
for key in ["state","init_cnt","mac_cnt","layer","r_idx","c_idx","timer","prediction","clk","reset","start","valid_out"]:
    hits = [l for l in vs if (" "+key+" ") in l or l.endswith(" "+key+" $end")]
    print(key, len(hits))
    for l in hits[:8]:
        print("   ", l.strip()[:120])
