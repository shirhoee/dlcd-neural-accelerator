"""Bounded emulator evaluation: first 2,000 MNIST test images.
Runs the bit-exact Q7.8 IntEmulatorV2 head (200->64->32->10) and the
float32 PyTorch model (v2_n13_model.pt) in one batched pass.
Writes confusion_matrix.csv + confusion_matrix.png to docs/review/.
"""
import sys, time, json, csv
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent.parent  # repo root
sys.path.insert(0, str(root / "v2" / "python_golden_model"))

import torch
import torchvision
from torchvision import transforms
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fixed_point_math import to_q7_8
from int_emulator_v2 import IntEmulatorV2

N = 2000  # bounded by runtime (~148 ms/image pure-Python emulator)

emu = IntEmulatorV2(
    str(root / "v2/python_golden_model/weights_q7_8.txt"),
    str(root / "v2/python_golden_model/conv2_weights_q7_8.txt"),
    dense1_hex=str(root / "v2/python_golden_model/dense1_q7_8.txt"),
    dense2_hex=str(root / "v2/python_golden_model/dense2_q7_8.txt"),
    dense3_hex=str(root / "v2/python_golden_model/dense3_q7_8.txt"),
    head_type="200->64->32->10")

device = torch.device("cpu")
from train_mlp3 import ConvMLP_V2_TrueSpec
model = ConvMLP_V2_TrueSpec().to(device)
model.load_state_dict(torch.load(str(root / "v2/python_golden_model/v2_n13_model.pt"), map_location=device))
model.eval()

transform = transforms.Compose([transforms.Resize((20, 20)), transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
testset = torchvision.datasets.MNIST(root=str(root / "data"), train=False, download=True, transform=transform)

# Float32: batched inference over all N
all_imgs = torch.stack([testset[i][0] for i in range(N)])
all_labels = torch.tensor([testset[i][1] for i in range(N)])
with torch.no_grad():
    pt_logits = model(all_imgs).numpy()
pt_pred = pt_logits.argmax(axis=1)

emu_preds = []
t0 = time.time()
for i in range(N):
    img, label = testset[i]
    img_q7_8 = [to_q7_8(v) for v in img.view(-1).numpy()]
    p, _ = emu.forward(img_q7_8)
    emu_preds.append(p)
    if (i + 1) % 500 == 0:
        print(f"  emulator {i+1}/N ... {time.time()-t0:.1f}s", flush=True)
emu_preds = np.array(emu_preds)
emu_time = time.time() - t0

pt_correct = int((pt_pred == all_labels.numpy()).sum())
emu_correct = int((emu_preds == all_labels.numpy()).sum())
disagreements = int((pt_pred != emu_preds).sum())

conf = np.zeros((10, 10), dtype=int)
for t, p in zip(all_labels.numpy(), emu_preds):
    conf[t, p] += 1
per_class = conf.diagonal() / conf.sum(axis=1).clip(min=1)

print(f"Emulator (first {N} MNIST test images):")
print(f"  emulator accuracy : {emu_correct}/{N} = {emu_correct/N*100:.2f}%")
print(f"  float32 accuracy  : {pt_correct}/{N} = {pt_correct/N*100:.2f}%")
print(f"  pt-vs-emu disagreements: {disagreements}")
print(f"  emulator wall time: {emu_time:.1f}s ({emu_time/N*1000:.0f} ms/img)")
print(f"  per-class accuracy: " + ", ".join(f"{per_class[c]*100:.1f}%" for c in range(10)))
print("Confusion matrix (rows=true, cols=pred):")
for r in range(10):
    print(" ", conf[r].tolist())

# CSV
with open(str(root / "docs/review/confusion_matrix.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["true\\pred"] + [str(c) for c in range(10)] + ["total", "correct", "class_accuracy"])
    for r in range(10):
        w.writerow([r] + conf[r].tolist() + [int(conf[r].sum()), int(conf[r, r]), f"{per_class[r]*100:.2f}%"])
    w.writerow(["TOTAL"] + conf.sum(axis=0).tolist() + [N, emu_correct, f"{emu_correct/N*100:.2f}%"])

# PNG
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(conf, interpolation="nearest", cmap=plt.cm.Blues)
ax.set_title(f"Q7.8 Emulator Confusion Matrix — first {N} MNIST test images\naccuracy {emu_correct}/{N} = {emu_correct/N*100:.2f}%")
ax.set_xlabel("Predicted label"); ax.set_ylabel("True label")
ax.set_xticks(range(10)); ax.set_yticks(range(10))
for i in range(10):
    for j in range(10):
        ax.text(j, i, conf[i, j], ha="center", va="center", fontsize=8,
                color="white" if conf[i, j] > conf.max()/2 else "black")
fig.colorbar(im, ax=ax)
fig.tight_layout()
fig.savefig(str(root / "docs/review/confusion_matrix.png"), dpi=150)
print("Wrote docs/review/confusion_matrix.csv and docs/review/confusion_matrix.png")
print(json.dumps({
    "images": N, "emu_correct": emu_correct, "emu_accuracy": emu_correct / N,
    "pt_correct": pt_correct, "pt_accuracy": pt_correct / N,
    "disagreements": disagreements, "per_class": [float(x) for x in per_class]
}, indent=2))
