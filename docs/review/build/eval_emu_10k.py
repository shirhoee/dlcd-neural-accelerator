import sys
import os
import time
import json
import csv
import threading
from pathlib import Path
import numpy as np
import torch
import torchvision
from torchvision import transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root / "v2" / "python_golden_model"))

from fixed_point_math import to_q7_8
from int_emulator_v2 import IntEmulatorV2
from train_mlp3 import ConvMLP_V2_TrueSpec

_tls = threading.local()

def get_emulator():
    if not hasattr(_tls, "emu"):
        _tls.emu = IntEmulatorV2(
            str(root / "v2/python_golden_model/weights_q7_8.txt"),
            str(root / "v2/python_golden_model/conv2_weights_q7_8.txt"),
            dense1_hex=str(root / "v2/python_golden_model/dense1_q7_8.txt"),
            dense2_hex=str(root / "v2/python_golden_model/dense2_q7_8.txt"),
            dense3_hex=str(root / "v2/python_golden_model/dense3_q7_8.txt"),
            head_type="200->64->32->10"
        )
    return _tls.emu

def eval_single(item):
    idx, img_flat_list, label = item
    emu = get_emulator()
    pred, logits = emu.forward(img_flat_list)
    return idx, pred, label, logits

def main():
    start_time = time.time()
    device = torch.device("cpu")
    model = ConvMLP_V2_TrueSpec().to(device)
    model.load_state_dict(torch.load(str(root / "v2/python_golden_model/v2_n13_model.pt"), map_location=device))
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    testset = torchvision.datasets.MNIST(root=str(root / "data"), train=False, download=True, transform=transform)

    N = len(testset) # 10000
    print(f"Loaded {N} MNIST test images. Running batched PyTorch float32 model...", flush=True)
    all_imgs = torch.stack([testset[i][0] for i in range(N)])
    all_labels = np.array([testset[i][1] for i in range(N)])
    
    with torch.no_grad():
        pt_logits = model(all_imgs).numpy()
    pt_preds = pt_logits.argmax(axis=1)
    pt_correct = int((pt_preds == all_labels).sum())
    print(f"PyTorch Float32: {pt_correct}/{N} = {pt_correct/N*100:.2f}%", flush=True)

    print("Preparing Q7.8 inputs...", flush=True)
    tasks = []
    for i in range(N):
        img_flat = testset[i][0].view(-1).numpy()
        img_q7_8 = [to_q7_8(v) for v in img_flat]
        tasks.append((i, img_q7_8, all_labels[i]))

    workers = 8
    print(f"Evaluating {N} images with Q7.8 IntEmulatorV2 across {workers} threads...", flush=True)
    t0 = time.time()
    
    emu_preds = [0] * N
    emu_logits_db = [None] * N
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for done_count, (idx, pred, label, logits) in enumerate(executor.map(eval_single, tasks), 1):
            emu_preds[idx] = pred
            emu_logits_db[idx] = logits
            if done_count % 500 == 0 or done_count == N:
                print(f"  Processed {done_count}/{N} images ({time.time()-t0:.1f}s)...", flush=True)

    emu_preds = np.array(emu_preds)
    emu_time = time.time() - t0
    emu_correct = int((emu_preds == all_labels).sum())
    disagreements = int((pt_preds != emu_preds).sum())
    
    print(f"Done in {emu_time:.2f}s!", flush=True)
    print(f"Emulator Accuracy: {emu_correct}/{N} = {emu_correct/N*100:.2f}%", flush=True)
    print(f"Disagreements (F32 vs Q7.8): {disagreements}", flush=True)

    # Confusion matrix
    conf = np.zeros((10, 10), dtype=int)
    for t, p in zip(all_labels, emu_preds):
        conf[t, p] += 1
    per_class = conf.diagonal() / conf.sum(axis=1).clip(min=1)

    # Per class summary
    per_class_list = []
    for c in range(10):
        tot_c = int(conf[c].sum())
        cor_c = int(conf[c, c])
        acc_c = cor_c / tot_c if tot_c > 0 else 0.0
        per_class_list.append({
            "class": c,
            "total": tot_c,
            "correct": cor_c,
            "accuracy": round(acc_c, 4),
            "accuracy_pct": f"{acc_c*100:.2f}%"
        })

    # Save CSV
    csv_path = root / "docs/review/confusion_matrix.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["true\\pred"] + [str(c) for c in range(10)] + ["total", "correct", "class_accuracy"])
        for r in range(10):
            w.writerow([r] + conf[r].tolist() + [int(conf[r].sum()), int(conf[r, r]), f"{per_class[r]*100:.2f}%"])
        w.writerow(["TOTAL"] + conf.sum(axis=0).tolist() + [N, emu_correct, f"{emu_correct/N*100:.2f}%"])
    print(f"Wrote {csv_path}", flush=True)

    # Save PNG
    png_path = root / "docs/review/confusion_matrix.png"
    fig, ax = plt.subplots(figsize=(8.5, 7), dpi=300)
    im = ax.imshow(conf, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title(f"Q7.8 Integer Emulator Confusion Matrix — Full MNIST Test Set (N=10,000)\nAccuracy: {emu_correct}/{N} ({emu_correct/N*100:.2f}%) | PyTorch Float32: {pt_correct}/{N} ({pt_correct/N*100:.2f}%)", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Label", fontsize=10, fontweight="bold")
    ax.set_ylabel("True Ground-Truth Label", fontsize=10, fontweight="bold")
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    for i in range(10):
        for j in range(10):
            val = conf[i, j]
            ax.text(j, i, f"{val}", ha="center", va="center", fontsize=8.5,
                    color="white" if val > conf.max() / 2 else "black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(png_path, dpi=300)
    plt.close(fig)
    print(f"Wrote {png_path}", flush=True)

    results = {
        "total_images": N,
        "pt_correct": pt_correct,
        "pt_accuracy": pt_correct / float(N),
        "pt_accuracy_pct": f"{pt_correct/float(N)*100:.2f}%",
        "emu_correct": emu_correct,
        "emu_accuracy": emu_correct / float(N),
        "emu_accuracy_pct": f"{emu_correct/float(N)*100:.2f}%",
        "disagreements": disagreements,
        "wall_time_s": round(time.time() - start_time, 2),
        "per_class": per_class_list,
        "confusion_matrix": conf.tolist()
    }
    
    with open(root / "docs/review/build/emu_10k_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved emu_10k_results.json", flush=True)

if __name__ == "__main__":
    main()
