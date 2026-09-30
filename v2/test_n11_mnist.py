import os
import shutil
import subprocess
import torch
import torchvision
import torchvision.transforms as transforms
import sys

# Add python_golden_model to path to import fixed_point_math and model
sys.path.append(os.path.abspath('v2/python_golden_model'))
from train_v2_n0 import ConvMLP_V2
from fixed_point_math import to_q7_8

# Load PyTorch model
device = torch.device("cpu")
model = ConvMLP_V2().to(device)
model.load_state_dict(torch.load("v2/python_golden_model/v2_n0_model.pt", map_location=device))
model.eval()

# Load MNIST test set with same transform as train_v2_n0.py (Resize(20), ToTensor(), Normalize(0.5, 0.5))
transform = transforms.Compose([
    transforms.Resize((20, 20)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

# First test the N10 image
n10_img_path = "v2/temp_N10_image.txt"
tb_img_path = "v2/python_golden_model/test_image_q7_8.txt"
vvp = r"C:\iverilog\bin\vvp.exe"

print("--- N10 Test Image ---")
shutil.copy(n10_img_path, tb_img_path)
res = subprocess.run([vvp, "top_test"], cwd="v2/verilog_src", capture_output=True, text=True)
lines = [l for l in res.stdout.strip().split('\n') if "End-to-End Prediction:" in l]
if lines:
    print(f"RTL Prediction for N10 image: {lines[-1]}")
else:
    print("Could not parse RTL prediction for N10 image.")

# Now find one image for each digit 0-9
found_digits = {}
for i in range(len(testset)):
    img, label = testset[i]
    if label not in found_digits:
        found_digits[label] = img
    if len(found_digits) == 10:
        break

print("\n--- MNIST 0-9 Test ---")
print("Label | PyTorch Pred | RTL Pred")
for digit in range(10):
    img = found_digits[digit]
    
    # Get PyTorch prediction
    with torch.no_grad():
        out = model(img.unsqueeze(0))
        pt_pred = out.argmax(dim=1).item()
        
    # Write to test_image_q7_8.txt
    img_flat = img.view(-1).numpy()
    with open(tb_img_path, 'w') as f:
        for val in img_flat:
            q_val = to_q7_8(val)
            hex_val = f"{(q_val & 0xFFFF):04x}"
            f.write(hex_val + "\n")
            
    # Run RTL
    res = subprocess.run([vvp, "top_test"], cwd="v2/verilog_src", capture_output=True, text=True)
    rtl_pred_line = [l for l in res.stdout.strip().split('\n') if "End-to-End Prediction:" in l]
    rtl_pred = "N/A"
    if rtl_pred_line:
        rtl_pred = rtl_pred_line[-1].split(":")[-1].strip()
        
    print(f"  {digit}   |      {pt_pred}       |    {rtl_pred}")
