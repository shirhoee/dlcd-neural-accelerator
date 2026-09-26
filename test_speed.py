import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch
import time

def main():
    transform = transforms.Compose([
        transforms.Resize((10, 10)),
        transforms.ToTensor()
    ])

    print("Loading datasets...")
    train_dataset = datasets.MNIST(root='./data', train=True, download=False, transform=transform)
    
    print("Pre-processing datasets into memory...", flush=True)
    t0 = time.time()
    X_train_list = []
    
    # Just do a few batches to see speed
    loader = DataLoader(train_dataset, batch_size=1024)
    for i, (images, labels) in enumerate(loader):
        X_train_list.append(images)
        if i == 5:
            break
            
    t1 = time.time()
    print(f"Time for 6 batches (6144 images): {t1-t0:.2f}s")
    
if __name__ == "__main__":
    main()
