import torch
import os
from train_mlp3 import ConvMLP_V2_TrueSpec, hex16, to_q7_8

device = torch.device("cpu")
model = ConvMLP_V2_TrueSpec().to(device)
model.load_state_dict(torch.load("v2_n13_model.pt", map_location=device))

base_dir = os.path.dirname(os.path.abspath(__file__))

# Re-export dense1 with permutation
with open(os.path.join(base_dir, "dense1_q7_8.txt"), "w") as f:
    w = model.fc1.weight.detach() # [64, 200]
    w = w.view(64, 8, 5, 5)
    w = w.permute(0, 2, 3, 1).reshape(64, 200).numpy()
    for val in w.flatten():
        f.write(f"{hex16(to_q7_8(val))}\n")

# dense2 and dense3 don't need permutation
with open(os.path.join(base_dir, "dense2_q7_8.txt"), "w") as f:
    w = model.fc2.weight.detach().numpy() # [32, 64]
    for val in w.flatten():
        f.write(f"{hex16(to_q7_8(val))}\n")
        
with open(os.path.join(base_dir, "dense3_q7_8.txt"), "w") as f:
    w = model.fc3.weight.detach().numpy() # [10, 32]
    for val in w.flatten():
        f.write(f"{hex16(to_q7_8(val))}\n")

print("Re-exported dense weights successfully!")
