t = open("docs/review/wave/wave.vcd").read()
idx = t.index("$enddefinitions")
sec = t[idx:]
cnt = 0
for ln in sec.splitlines():
    if "O&" in ln:
        if cnt < 15:
            print(repr(ln))
        cnt += 1
print("lines with O&:", cnt)
cnt2 = 0
for ln in sec.splitlines():
    if ln.startswith("b") and ln.strip().endswith("O&"):
        cnt2 += 1
print("vector lines ending O&:", cnt2)
