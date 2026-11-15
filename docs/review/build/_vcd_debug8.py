from pathlib import Path
text = Path("docs/review/wave/wave.vcd").read_text()
idx = text.index("$enddefinitions")
section = text[idx:]
lines = section.splitlines()
# find first # timestamp
print("first 15 lines after $enddefinitions:")
for ln in lines[:15]:
    print(repr(ln))
# count changes per id for a few ids of interest, scanning raw
import collections
cnt = collections.Counter()
cur_id = None
for ln in lines:
    if ln.startswith("#"):
        continue
    if not ln or ln.startswith("$"):
        continue
    if ln.startswith("b"):
        mm = __import__("re").match(r"b[01xz]+\s+(\S+)", ln)
        if mm: cnt[mm.group(1)] += 1
    elif ln[0] in "01zx":
        cnt[ln[1:]] += 1
for q in ["t","y","k","W","[","t&","l&","i&","O&","V","U","Z","X"]:
    print(q, cnt.get(q, 0))
