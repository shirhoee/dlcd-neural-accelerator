import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from test_headless_drawing import get_model

def evaluate_mnist_accuracy():
    model = get_model() # This loads from the current rescaled hex files!
    
    transform = transforms.Compose([
        transforms.Resize((10, 10)),
        transforms.ToTensor()
    ])
    
    print("Loading MNIST test set...")
    test_dataset = datasets.MNIST(root='./data', train=False, download=False, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1024, shuffle=False)
    
    correct = 0
    total = 0
    
    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.view(-1, 100)
            logits = model(images)
            pred = torch.argmax(logits, dim=1)
            correct += (pred == labels).sum().item()
            total += labels.size(0)
            
    acc = 100.0 * correct / total
    print(f"Post-rescale PyTorch Float Accuracy (with quantized hex weights) on MNIST: {acc:.2f}%")

if __name__ == "__main__":
    evaluate_mnist_accuracy()
