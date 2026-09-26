import torch
from test_headless_drawing import get_model

def find_max_L2_activation():
    model = get_model()
    # Optimize input to maximize L2 activation
    inp = torch.rand((1, 100), requires_grad=True)
    optimizer = torch.optim.Adam([inp], lr=0.01)
    
    max_l2_found = 0
    
    for step in range(5000):
        optimizer.zero_grad()
        out_fc1 = model.fc1(inp)
        out_relu1 = model.relu(out_fc1)
        out_fc2 = model.fc2(out_relu1)
        
        # Maximize the maximum absolute value in L2
        loss = -out_fc2.abs().max()
        loss.backward()
        optimizer.step()
        
        # Clamp input to [0, 1]
        with torch.no_grad():
            inp.clamp_(0, 1)
            
        if -loss.item() > max_l2_found:
            max_l2_found = -loss.item()
            
    print(f"Max achievable L2 activation via optimization: {max_l2_found:.2f}")

    # Optimize for L3
    inp2 = torch.rand((1, 100), requires_grad=True)
    optimizer2 = torch.optim.Adam([inp2], lr=0.01)
    max_l3_found = 0
    for step in range(5000):
        optimizer2.zero_grad()
        logits = model(inp2)
        loss = -logits.abs().max()
        loss.backward()
        optimizer2.step()
        with torch.no_grad():
            inp2.clamp_(0, 1)
        if -loss.item() > max_l3_found:
            max_l3_found = -loss.item()
    print(f"Max achievable L3 activation via optimization: {max_l3_found:.2f}")

if __name__ == "__main__":
    find_max_L2_activation()
