import re
for f in ["v2/v2_ui/frontend/src/hooks/usePredict.ts",
          "v2/v2_ui/frontend/src/App.tsx",
          "v2/v2_ui/frontend/src/utils/downsample.ts",
          "v2/v2_ui/frontend/src/components/CanvasBoard.tsx"]:
    print("=" * 20, f)
    t = open(f).read()
    for i, ln in enumerate(t.splitlines(), 1):
        if any(k in ln for k in ["predict", "image", "grid_28", "fillRect", "0.0", "blank", "clear", "CANVAS_SIZE", "downsample", "toDataURL", "getImageData"]):
            print(f"{i:4d}: {ln.rstrip()}")
