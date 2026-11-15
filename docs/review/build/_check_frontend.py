t = open("v2/v2_ui/frontend/src/components/CanvasBoard.tsx").read()
for ln in t.splitlines():
    if any(k in ln for k in ["predict", "fetch", "image", "clear", "blank", "downsample", "grid_28", "fillRect", "createImageData"]):
        print(ln.rstrip())
