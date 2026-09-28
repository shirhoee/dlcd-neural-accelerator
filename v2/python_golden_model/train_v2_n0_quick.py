import torch
import torch.nn as nn

class ConvMLP_V2(nn.Module):
    def __init__(self):
        super(ConvMLP_V2, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1, padding=1, bias=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(200, 10, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x, return_all_logits=False):
        out_c1 = self.conv1(x)
        act1 = self.pool1(self.relu(out_c1))
        out_c2 = self.conv2(act1)
        act2 = self.pool2(self.relu(out_c2))
        flat = self.flatten(act2)
        out_fc = self.fc(flat)
        return out_fc

model = ConvMLP_V2()
# Set random weights so they are not all zero, but small enough to not overflow easily
with torch.no_grad():
    model.conv1.weight.uniform_(-0.1, 0.1)
    model.conv2.weight.uniform_(-0.1, 0.1)
    model.fc.weight.uniform_(-0.1, 0.1)
    
torch.save(model.state_dict(), 'v2/python_golden_model/v2_n0_model.pt')
print("Saved dummy weights.")
