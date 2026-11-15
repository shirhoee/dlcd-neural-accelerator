import sys, time, os
from pathlib import Path
root = Path(__file__).resolve().parent.parent.parent.parent  # repo root
sys.path.insert(0, str(root / "v2" / "python_golden_model"))
from fixed_point_math import to_q7_8
from int_emulator_v2 import IntEmulatorV2
import torchvision, torch
from torchvision import transforms

emu = IntEmulatorV2(
    str(root / "v2/python_golden_model/weights_q7_8.txt"),
    str(root / "v2/python_golden_model/conv2_weights_q7_8.txt"),
    dense1_hex=str(root / "v2/python_golden_model/dense1_q7_8.txt"),
    dense2_hex=str(root / "v2/python_golden_model/dense2_q7_8.txt"),
    dense3_hex=str(root / "v2/python_golden_model/dense3_q7_8.txt"),
    head_type="200->64->32->10")

transform = transforms.Compose([transforms.Resize((20,20)), transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
ts = torchvision.datasets.MNIST(root=str(root / "data"), train=False, download=True, transform=transform)

t0 = time.time()
for i in range(100):
    img, label = ts[i]
    img_q7_8 = [to_q7_8(v) for v in img.view(-1).numpy()]
    emu.forward(img_q7_8)
dt = time.time() - t0
print(f"100 images in {dt:.2f}s -> {dt/100*1000:.1f} ms/img -> est 10k: {dt/100*10:.0f}s")
