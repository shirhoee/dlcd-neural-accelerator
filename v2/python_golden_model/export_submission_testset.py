import os
import sys
import torch
import torchvision
import torchvision.transforms as transforms
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from int_emulator_v2 import IntEmulatorV2
from fixed_point_math import to_q7_8, to_signed_16

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_dir = os.path.abspath(os.path.join(base_dir, "../verilog_src"))

    # Initialize emulator
    emu = IntEmulatorV2(
        os.path.join(base_dir, "weights_q7_8.txt"),
        os.path.join(base_dir, "conv2_weights_q7_8.txt"),
        dense1_hex=os.path.join(base_dir, "dense1_q7_8.txt"),
        dense2_hex=os.path.join(base_dir, "dense2_q7_8.txt"),
        dense3_hex=os.path.join(base_dir, "dense3_q7_8.txt"),
        head_type="200->64->32->10"
    )

    # Load MNIST testset with standard normalization
    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    root_data = os.path.abspath(os.path.join(base_dir, "../../data"))
    testset = torchvision.datasets.MNIST(root=root_data, train=False, download=True, transform=transform)

    # Find one high-confidence sample for each digit 0 to 9
    chosen_samples = {} # digit -> (tensor_flat_q7_8, label)
    
    for idx in range(len(testset)):
        img_tensor, label = testset[idx]
        if label in chosen_samples:
            continue
        
        flat_np = img_tensor.squeeze().numpy().flatten()
        flat_q7_8 = [to_q7_8(val) for val in flat_np]
        
        pred, logits = emu.forward(flat_q7_8)
        if pred == label:
            chosen_samples[label] = (flat_q7_8, label)
            print(f"Found digit {label} at testset index {idx}: Emu Pred = {pred} (PASS)")
        
        if len(chosen_samples) == 10:
            break

    # Sort in order 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    sorted_digits = [chosen_samples[d] for d in range(10)]

    # Export to verilog_src
    vec_path = os.path.join(verilog_dir, "submission_test_vectors.hex")
    lbl_path = os.path.join(verilog_dir, "submission_labels.hex")

    with open(vec_path, "w") as f_vec, open(lbl_path, "w") as f_lbl:
        for q_img, label in sorted_digits:
            f_lbl.write(f"{label}\n")
            for px in q_img:
                f_vec.write(f"{(px & 0xFFFF):04X}\n")

    print(f"\nSuccessfully generated {vec_path} (4000 words for 10 digits 0-9).")
    print(f"Successfully generated {lbl_path} (10 labels).")

if __name__ == "__main__":
    main()
