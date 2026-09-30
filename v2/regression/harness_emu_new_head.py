import sys
import os
import json
import torch
import numpy as np
import torchvision
import torchvision.transforms as transforms
import time

sys.path.append(os.path.abspath('../python_golden_model'))
from train_mlp3 import ConvMLP_V2_TrueSpec
from fixed_point_math import to_q7_8, to_signed_16
from int_emulator_v2 import IntEmulatorV2

start_time = time.time()
device = torch.device("cpu")
model = ConvMLP_V2_TrueSpec().to(device)
model.load_state_dict(torch.load("../python_golden_model/v2_n13_model.pt", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((20, 20)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
testset = torchvision.datasets.MNIST(root='../../data', train=False, download=True, transform=transform)

emulator = IntEmulatorV2(
    "../python_golden_model/weights_q7_8.txt",
    "../python_golden_model/conv2_weights_q7_8.txt",
    dense1_hex="../python_golden_model/dense1_q7_8.txt",
    dense2_hex="../python_golden_model/dense2_q7_8.txt",
    dense3_hex="../python_golden_model/dense3_q7_8.txt",
    head_type="200->64->32->10"
)

pt_correct = 0
emu_correct = 0
disagreements = 0
max_logit_error = 0

print("Running Emu-only harness (New Head) over 10,000 images...")
for i in range(10000):
    img, label = testset[i]
    with torch.no_grad():
        out = model(img.unsqueeze(0))
        pt_logits = out[0].numpy()
        pt_pred = out.argmax(dim=1).item()
        
    img_flat = img.view(-1).numpy()
    img_q7_8 = [to_q7_8(val) for val in img_flat]
    emu_pred, emu_logits = emulator.forward(img_q7_8)
    
    if pt_pred == label: pt_correct += 1
    if emu_pred == label: emu_correct += 1
    if pt_pred != emu_pred: disagreements += 1
    
    pt_scaled = pt_logits * 256.0
    err = np.max(np.abs(pt_scaled - np.array(emu_logits)))
    if err > max_logit_error:
        max_logit_error = err
        
    if (i+1) % 1000 == 0:
        print(f"Processed {i+1}/10000...")

end_time = time.time()
print(f"Wall time: {end_time - start_time:.2f} seconds")

summary = {
    "Total Images": 10000,
    "Emu Accuracy": emu_correct / 10000.0,
    "Float32 Accuracy": pt_correct / 10000.0,
    "F32 vs Q7.8 Disagreements": disagreements,
    "Max Logit Error": float(max_logit_error)
}

print("\n--- RESULTS ---")
print(json.dumps(summary, indent=4))
