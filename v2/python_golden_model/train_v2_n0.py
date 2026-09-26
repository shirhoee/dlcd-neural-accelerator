import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np

# Tradeoff (Rule 7): Epochs reduced to 20 instead of 300.
# Alternative not taken: 300 epochs (V1 default).
# Reason: CNNs converge much faster to >98% accuracy. Running 300 epochs locally 
# on CPU destroys iteration speed for N0. We can scale up later if needed.
EPOCHS = 20
BATCH_SIZE = 128
LR = 0.001

class ConvMLP_V2(nn.Module):
    def __init__(self):
        super(ConvMLP_V2, self).__init__()
        # Input: 1 x 20 x 20
        # Conv1: 1 -> 4 channels, 3x3 kernel, stride 1, padding 1 (Bias=False per spec)
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Conv2: 4 -> 8 channels, 3x3 kernel, stride 1, padding 1 (Bias=False per spec)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # After two 2x2 pools, 20x20 -> 10x10 -> 5x5. Channels = 8.
        # Flattened size = 8 * 5 * 5 = 200.
        self.flatten = nn.Flatten()
        
        self.fc1 = nn.Linear(200, 64, bias=False)
        self.fc2 = nn.Linear(64, 32, bias=False)
        self.fc3 = nn.Linear(32, 10, bias=False)
        
        self.relu = nn.ReLU()

    def forward(self, x, return_all_logits=False):
        # Forward pass tracking raw pre-activation values for headroom checks
        out_c1 = self.conv1(x)
        act1 = self.pool1(self.relu(out_c1))
        
        out_c2 = self.conv2(act1)
        act2 = self.pool2(self.relu(out_c2))
        
        flat = self.flatten(act2)
        
        out_fc1 = self.fc1(flat)
        act3 = self.relu(out_fc1)
        
        out_fc2 = self.fc2(act3)
        act4 = self.relu(out_fc2)
        
        out_fc3 = self.fc3(act4)
        
        if return_all_logits:
            return out_fc3, out_c1, out_c2, out_fc1, out_fc2
        return out_fc3

# Tradeoff (Rule 7): Translation implemented via F.pad + slicing.
# Alternative not taken: torch.roll
# Reason: torch.roll causes pixels shifted off one edge to wrap around to the other, 
# which creates unnatural edge artifacts that don't exist in human handwriting.
def augment_batch(x):
    # x shape: [B, 1, 20, 20]
    batch_size = x.size(0)
    
    # 1. Morphological Augmentation (Dilation/Erosion) - 30% chance per batch
    if torch.rand(1).item() < 0.30:
        is_dilation = torch.rand(1).item() > 0.5
        iters = torch.randint(1, 3, (1,)).item()
        for _ in range(iters):
            if is_dilation:
                x = F.max_pool2d(x, kernel_size=3, stride=1, padding=1)
            else:
                x = -F.max_pool2d(-x, kernel_size=3, stride=1, padding=1)
                
    # 2. Translation Augmentation (+/- 2px) - 50% chance to translate
    if torch.rand(1).item() < 0.50:
        shift_x = torch.randint(-2, 3, (1,)).item()
        shift_y = torch.randint(-2, 3, (1,)).item()
        padded = F.pad(x, (2, 2, 2, 2), mode='constant', value=0.0)
        start_y = 2 + shift_y
        start_x = 2 + shift_x
        x = padded[:, :, start_y:start_y+20, start_x:start_x+20]
        
    return x

def main():
    print("Initializing V2 N0 Training Pipeline...")
    
    transform = transforms.Compose([
        transforms.Resize((20, 20)),
        transforms.ToTensor()
    ])
    
    # Use V1's cached dataset
    train_dataset = datasets.MNIST(root='../../v1/data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='../../v1/data', train=False, download=True, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = ConvMLP_V2().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()
    
    print("\n--- Training Model ---")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            
            # Apply augmentations natively in PyTorch on the batch
            data = augment_batch(data)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        scheduler.step()
        print(f"Epoch {epoch}/{EPOCHS} - Loss: {total_loss/len(train_loader):.4f}")
    
    # Save the model
    torch.save(model.state_dict(), 'v2_n0_model.pt')
    print("\nModel saved to v2_n0_model.pt")

    print("\n--- Testing Model ---")
    model.eval()
    correct = 0
    
    # Headroom Sweep Trackers
    max_c1 = max_c2 = max_fc1 = max_fc2 = max_fc3 = 0.0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            out_fc3, out_c1, out_c2, out_fc1, out_fc2 = model(data, return_all_logits=True)
            
            pred = out_fc3.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            
            # Track max absolute logits per layer
            max_c1 = max(max_c1, out_c1.abs().max().item())
            max_c2 = max(max_c2, out_c2.abs().max().item())
            max_fc1 = max(max_fc1, out_fc1.abs().max().item())
            max_fc2 = max(max_fc2, out_fc2.abs().max().item())
            max_fc3 = max(max_fc3, out_fc3.abs().max().item())
            
    test_acc = 100. * correct / len(test_loader.dataset)
    print(f"Test Accuracy (Float32): {correct}/{len(test_loader.dataset)} ({test_acc:.2f}%)")
    
    print("\n--- Mandatory Max|Logit| Headroom Sweep (Test Set) ---")
    print(f"Conv1 Max|Logit|: {max_c1:.2f}")
    print(f"Conv2 Max|Logit|: {max_c2:.2f}")
    print(f"FC1   Max|Logit|: {max_fc1:.2f}")
    print(f"FC2   Max|Logit|: {max_fc2:.2f}")
    print(f"FC3   Max|Logit|: {max_fc3:.2f}")
    print("Note: Values > 127.99 will require post-training rescaling before Q7.8 export (Rule 1).")

    print("\n--- Domain Gap Sanity Check ---")
    # Generate synthetic thick blob test images
    blob_img = torch.zeros(1, 1, 20, 20)
    # Draw a dense center rectangle to simulate a very thick stroke
    blob_img[0, 0, 6:14, 6:14] = 1.0 
    blob_mean = blob_img.mean().item()
    blob_nz = (blob_img > 0.05).float().mean().item()
    
    # Grab a batch from training (with augmentation)
    aug_data, _ = next(iter(train_loader))
    aug_data = augment_batch(aug_data)
    aug_mean = aug_data.mean().item()
    aug_nz = (aug_data > 0.05).float().mean().item()
    
    print("Synthetic 'Thick Blob' stats:")
    print(f"  Mean Intensity: {blob_mean:.4f}")
    print(f"  Non-zero Frac:  {blob_nz:.4f}")
    
    print("Augmented Training Batch stats:")
    print(f"  Mean Intensity: {aug_mean:.4f}")
    print(f"  Non-zero Frac:  {aug_nz:.4f}")
    
    if aug_mean < blob_mean * 0.5:
        print("WARNING: Augmented training data is still significantly thinner/sparser than the thick blob.")
    else:
        print("SUCCESS: Augmented training distribution is physically thicker, helping close the domain gap.")

if __name__ == '__main__':
    main()
