#!/usr/bin/env python3
"""
M16: Local Hand-Drawn Digit Testing
Draw digits on a pygame canvas, downsample to 10x10, run through golden model + Verilog pipeline.
Uses existing 93.06%-baseline weights (e2e_w1.hex/w2.hex/w3.hex) — no retraining.
"""

import pygame
import numpy as np
import torch
import torch.nn as nn
import subprocess
import os
import sys

# Use the correct Python for subprocess calls
PYTHON_EXE = r"C:\Users\SHREYANSH RAJ\AppData\Local\Programs\Python\Python312\python.exe"
IVERILOG_PATH = r"C:\iverilog\bin\iverilog.exe"
VVP_PATH = r"C:\iverilog\bin\vvp.exe"
VERILOG_SRC = "verilog_src"

# Canvas settings
CANVAS_SIZE = 280  # 280x280 drawing area (28px per 10x10 cell)
GRID_SIZE = 10     # Target 10x10 for model
CELL_SIZE = CANVAS_SIZE // GRID_SIZE  # 28px per cell

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)

class VerilogNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(100, 16, bias=False)
        self.fc2 = nn.Linear(16, 6, bias=False)
        self.fc3 = nn.Linear(6, 10, bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def load_model():
    """Load the 93.06% baseline model from cached Q7.8 hex weights."""
    model = VerilogNet()
    
    w1_path = os.path.join(VERILOG_SRC, "e2e_w1.hex")
    w2_path = os.path.join(VERILOG_SRC, "e2e_w2.hex")
    w3_path = os.path.join(VERILOG_SRC, "e2e_w3.hex")
    
    if not (os.path.exists(w1_path) and os.path.exists(w2_path) and os.path.exists(w3_path)):
        print("ERROR: Weight files not found. Run train_model.py first.")
        return None
    
    w1_flat = np.array([int(line.strip(), 16) for line in open(w1_path)])
    w2_flat = np.array([int(line.strip(), 16) for line in open(w2_path)])
    w3_flat = np.array([int(line.strip(), 16) for line in open(w3_path)])
    
    def to_signed(v): return v - 65536 if (v & 0x8000) else v
    w1 = np.array([to_signed(v) for v in w1_flat]).reshape(16, 100).astype(np.float32) / 256.0
    w2 = np.array([to_signed(v) for v in w2_flat]).reshape(6, 16).astype(np.float32) / 256.0
    w3 = np.array([to_signed(v) for v in w3_flat]).reshape(10, 6).astype(np.float32) / 256.0
    
    with torch.no_grad():
        model.fc1.weight.copy_(torch.from_numpy(w1))
        model.fc2.weight.copy_(torch.from_numpy(w2))
        model.fc3.weight.copy_(torch.from_numpy(w3))
    
    model.eval()
    return model

def downsample_to_10x10(surface, debug=False):
    """
    Downsample drawn canvas to 10x10 grayscale [0.0, 1.0].
    Preprocessing to match train_model.py:
    1. Find bounding box of non-white pixels
    2. Make crop square by expanding smaller dimension (centered), like sklearn digits
    3. Resize to 8x8
    4. Pad to 10x10 with 1px border
    5. Normalize to [0.0, 1.0]
    """
    # Get pixel array (280x280)
    arr = pygame.surfarray.array3d(surface)  # (W, H, 3)
    # FIX: transpose to (H, W, 3) for standard numpy image convention
    arr = arr.transpose(1, 0, 2)  # Now (H, W, 3) = (280, 280, 3)
    
    # Convert to grayscale (average RGB)
    gray = arr.mean(axis=2).astype(np.float32)  # (H, W) = (280, 280)
    
    # Invert: drawing is black on white, but model expects digit=high, background=low
    # So: white(255) -> 0.0, black(0) -> 1.0
    gray = 255.0 - gray
    
    if debug:
        print(f"DEBUG: gray shape = {gray.shape}, min={gray.min():.1f}, max={gray.max():.1f}")
    
    # Find bounding box of non-zero pixels
    rows = np.any(gray > 10, axis=1)  # axis=1 = along width (columns)
    cols = np.any(gray > 10, axis=0)  # axis=0 = along height (rows)
    
    if debug:
        print(f"DEBUG: rows any = {np.any(rows)}, cols any = {np.any(cols)}")
    
    if not np.any(rows) or not np.any(cols):
        # Empty canvas
        if debug:
            print("DEBUG: Empty canvas")
        return np.zeros((10, 10), dtype=np.float32)
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    if debug:
        print(f"DEBUG: raw bounding box: rows [{rmin}:{rmax+1}] (h={rmax-rmin+1}), cols [{cmin}:{cmax+1}] (w={cmax-cmin+1})")
    
    # Make crop square by expanding smaller dimension (centered)
    # This mimics sklearn digits which are centered in 8x8
    h = rmax - rmin + 1
    w = cmax - cmin + 1
    size = max(h, w)
    
    # Center the square crop
    r_center = (rmin + rmax) // 2
    c_center = (cmin + cmax) // 2
    half = size // 2
    
    rmin_sq = max(0, r_center - half)
    rmax_sq = min(gray.shape[0] - 1, r_center + half)
    cmin_sq = max(0, c_center - half)
    cmax_sq = min(gray.shape[1] - 1, c_center + half)
    
    # Adjust if we hit boundaries
    if rmax_sq - rmin_sq + 1 < size:
        if rmin_sq == 0:
            rmax_sq = min(gray.shape[0] - 1, rmin_sq + size - 1)
        elif rmax_sq == gray.shape[0] - 1:
            rmin_sq = max(0, rmax_sq - size + 1)
    if cmax_sq - cmin_sq + 1 < size:
        if cmin_sq == 0:
            cmax_sq = min(gray.shape[1] - 1, cmin_sq + size - 1)
        elif cmax_sq == gray.shape[1] - 1:
            cmin_sq = max(0, cmax_sq - size + 1)
    
    if debug:
        print(f"DEBUG: square crop: rows [{rmin_sq}:{rmax_sq+1}], cols [{cmin_sq}:{cmax_sq+1}], size={rmax_sq-rmin_sq+1}x{cmax_sq-cmin_sq+1}")
    
    # Crop to square bounding box
    cropped = gray[rmin_sq:rmax_sq+1, cmin_sq:cmax_sq+1]
    
    if debug:
        print(f"DEBUG: cropped shape = {cropped.shape}")
        print("DEBUG: cropped values (scaled to 0-9 for display):")
        for row in cropped:
            line = ''.join([' ' if v < 10 else str(min(9, int(v/25.5))) for v in row])
            print(f"  {line}")
    
    # Resize to 8x8 using block AVERAGE pooling (matches sklearn antialiased stroke distribution)
    h, w = cropped.shape
    out_h, out_w = 8, 8
    resized = np.zeros((out_h, out_w), dtype=np.float32)
    for i in range(out_h):
        for j in range(out_w):
            r_start = int(i * h / out_h)
            r_end = int((i + 1) * h / out_h)
            c_start = int(j * w / out_w)
            c_end = int((j + 1) * w / out_w)
            block = cropped[r_start:r_end, c_start:c_end]
            if block.size > 0:
                resized[i, j] = block.mean()
    
    if debug:
        print(f"DEBUG: resized 8x8 shape = {resized.shape}")
        print("DEBUG: resized 8x8 values:")
        for row in resized:
            line = ''.join([f'{v:5.1f}' for v in row])
            print(f"  {line}")
    
    # Pad to 10x10 with 1px border (matching train_model.py)
    padded = np.pad(resized, ((1, 1), (1, 1)), mode='constant', constant_values=0)
    
    if debug:
        print(f"DEBUG: padded 10x10 shape = {padded.shape}")
        print("DEBUG: padded 10x10 values:")
        for row in padded:
            line = ''.join([f'{v:5.1f}' for v in row])
            print(f"  {line}")
    
    # Normalize to [0.0, 1.0] - training used /16.0 on 0-16 data, so [0,1]
    # Our canvas is 0-255, so /255.0 gives [0,1] range
    normalized = padded / 255.0
    
    if debug:
        print("DEBUG: final normalized 10x10 (0.0-1.0):")
        for row in normalized:
            line = ''.join([f'{v:.3f}' for v in row])
            print(f"  {line}")
    
    return normalized

def to_q7_8_hex(val):
    v_int = int(val * 256)
    return f"{v_int & 0xFFFF:04x}"

def write_input_hex(img_10x10, filename):
    with open(filename, 'w') as f:
        for row in img_10x10:
            for val in row:
                f.write(to_q7_8_hex(val) + "\n")

def golden_predict_q7_8(model, img_10x10):
    """Run PyTorch float forward pass on the 10x10 input."""
    inp = torch.tensor(img_10x10.flatten(), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = model(inp)
        pred = torch.argmax(logits, dim=1).item()
        max_logit = logits.abs().max().item()
    return pred, max_logit

def run_verilog_sim():
    """Compile and run tb_accelerator_top.v, return predicted digit."""
    cmd_compile = [
        IVERILOG_PATH, "-o", "tb_top.vvp",
        "mac_q7_8.v", "systolic_pe.v", "systolic_array.v",
        "relu_q7_8.v", "layer_relu.v", "argmax.v",
        "accelerator_top.v", "tb_accelerator_top.v"
    ]
    result = subprocess.run(cmd_compile, capture_output=True, text=True, cwd=VERILOG_SRC)
    if result.returncode != 0:
        return None, f"Compile failed: {result.stderr}"
    
    cmd_run = [VVP_PATH, "tb_top.vvp"]
    result = subprocess.run(cmd_run, capture_output=True, text=True, cwd=VERILOG_SRC)
    if result.returncode != 0:
        return None, f"Sim failed: {result.stderr}"
    
    for line in result.stdout.split('\n'):
        if "Verilog Prediction: Digit" in line:
            try:
                return int(line.split("Digit")[-1].strip()), None
            except:
                pass
    return None, "No prediction in output"


# UI Colors (Modern Dark Theme)
BG_COLOR = (30, 30, 46)
PANEL_COLOR = (24, 24, 37)
TEXT_COLOR = (205, 214, 244)
ACCENT_COLOR = (137, 180, 250)
GREEN_COLOR = (166, 227, 161)
RED_COLOR = (243, 139, 168)
BTN_COLOR = (49, 50, 68)
BTN_HOVER = (69, 71, 90)

RENDER_SCALE = 2
VISUAL_SIZE = CANVAS_SIZE * RENDER_SCALE # 560

def draw_10x10_preview(screen, img_10x10, x, y, scale=20):
    """Draw a 10x10 preview of the downsampled input."""
    for i in range(10):
        for j in range(10):
            val = int(img_10x10[i, j] * 255)
            # Invert for dark theme visualization (higher value = brighter)
            color = (val, val, val)
            rect = pygame.Rect(x + j*scale, y + i*scale, scale, scale)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, PANEL_COLOR, rect, 1)

def draw_button(screen, font, rect, text, is_hover, color=BTN_COLOR):
    import pygame
    bg = BTN_HOVER if is_hover else color
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, (88, 91, 112), rect, 2, border_radius=8)
    surf = font.render(text, True, TEXT_COLOR)
    tr = surf.get_rect(center=rect.center)
    screen.blit(surf, tr)

def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((VISUAL_SIZE + 400, VISUAL_SIZE))
    pygame.display.set_caption("V1 Neural Accelerator: Hardware Digit Classification")
    clock = pygame.time.Clock()
    
    font_large = pygame.font.SysFont('segoeui,arial', 32, bold=True)
    font = pygame.font.SysFont('segoeui,arial', 20)
    font_small = pygame.font.SysFont('segoeui,arial', 16)
    font_huge = pygame.font.SysFont('segoeui,arial', 120, bold=True)
    
    # Mathematical drawing surface (STRICTLY 280x280, white bg, black stroke)
    math_canvas = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE))
    math_math_canvas.fill(WHITE)
                    ui_canvas.fill(WHITE)
    ui_canvas = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE))
    ui_math_canvas.fill(WHITE)
                    ui_canvas.fill(WHITE)
    
    # Load model
    model = load_model()
    if model is None:
        return
    
    drawing = False
    last_pos = None
    status_text = "Draw a digit and click Predict"
    golden_pred = None
    hw_pred = None
    max_logit = 0.0
    last_img_10x10 = None
    
    # Buttons
    btn_predict = pygame.Rect(VISUAL_SIZE + 40, VISUAL_SIZE - 120, 150, 50)
    btn_clear = pygame.Rect(VISUAL_SIZE + 210, VISUAL_SIZE - 120, 150, 50)
    
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        hover_predict = btn_predict.collidepoint(mx, my)
        hover_clear = btn_clear.collidepoint(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hover_clear:
                    math_canvas.fill(WHITE)
                    ui_canvas.fill(WHITE)
                    status_text = "Cleared. Draw a digit."
                    golden_pred = hw_pred = None
                    max_logit = 0.0
                    last_img_10x10 = None
                elif hover_predict:
                    img_10x10 = downsample_to_10x10(math_canvas, debug=False)
                    last_img_10x10 = img_10x10
                    
                    import os
                    write_input_hex(img_10x10, os.path.join(VERILOG_SRC, "e2e_input.hex"))
                    
                    golden_pred, max_logit = golden_predict_q7_8(model, img_10x10)
                    hw_pred, err = run_verilog_sim()
                    
                    if err:
                        status_text = f"Error: {err}"
                        hw_pred = None
                    else:
                        match = "MATCH" if golden_pred == hw_pred else "MISMATCH"
                        status_text = f"Prediction complete ({match})"
                
                elif mx < VISUAL_SIZE and my < VISUAL_SIZE:
                    drawing = True
                    last_pos = (mx // RENDER_SCALE, my // RENDER_SCALE)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                last_pos = None
            
            elif event.type == pygame.MOUSEMOTION and drawing:
                if mx < VISUAL_SIZE and my < VISUAL_SIZE:
                    curr_pos = (mx // RENDER_SCALE, my // RENDER_SCALE)
                    if last_pos:
                        pygame.draw.line(math_canvas, BLACK, last_pos, curr_pos, 36)
                        pygame.draw.line(ui_canvas, BLACK, last_pos, curr_pos, 12)
                    last_pos = curr_pos
        
        # Render App Background
        screen.fill(BG_COLOR)
        
        # Invert canvas for dark mode display
        display_surf = pygame.transform.scale(ui_canvas, (VISUAL_SIZE, VISUAL_SIZE))
        inv = pygame.Surface((VISUAL_SIZE, VISUAL_SIZE))
        inv.fill((255, 255, 255))
        inv.blit(display_surf, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
        screen.blit(inv, (0, 0))
        
        # Divider Line
        pygame.draw.line(screen, PANEL_COLOR, (VISUAL_SIZE, 0), (VISUAL_SIZE, VISUAL_SIZE), 4)
        
        # UI Panel
        panel_x = VISUAL_SIZE + 40
        title_surf = font_large.render("V1 Neural Accelerator", True, TEXT_COLOR)
        screen.blit(title_surf, (panel_x, 30))
        
        status_surf = font.render(status_text, True, ACCENT_COLOR)
        screen.blit(status_surf, (panel_x, 80))
        
        # Hardware Prediction Display
        if hw_pred is not None:
            pred_color = GREEN_COLOR if hw_pred == golden_pred else RED_COLOR
            # Box
            pygame.draw.rect(screen, PANEL_COLOR, (panel_x, 120, 320, 160), border_radius=12)
            lbl = font_small.render("Hardware Prediction", True, (166, 173, 200))
            screen.blit(lbl, (panel_x + 20, 130))
            
            huge = font_huge.render(str(hw_pred), True, pred_color)
            hr = huge.get_rect(center=(panel_x + 160, 200))
            screen.blit(huge, hr)
            
            # Sub-info
            match_txt = "Bit-Exact Match" if hw_pred == golden_pred else "Mismatch w/ PyTorch"
            sub = font_small.render(match_txt, True, pred_color)
            screen.blit(sub, (panel_x + 20, 250))
        
        # 10x10 Downsampled Preview
        if last_img_10x10 is not None:
            lbl = font_small.render("Model Input Space (10x10)", True, (166, 173, 200))
            screen.blit(lbl, (panel_x, 300))
            draw_10x10_preview(screen, last_img_10x10, panel_x, 325, scale=18)
            
            # Logits
            logit_color = GREEN_COLOR if max_logit < 100 else RED_COLOR if max_logit > 127 else (249, 226, 175)
            logit_text = font_small.render(f"Max Logit: {max_logit:.2f} (Q7.8 max: 127.99)", True, logit_color)
            screen.blit(logit_text, (panel_x, 515))
        
        # Draw Buttons
        draw_button(screen, font, btn_predict, "Predict", hover_predict, (69, 71, 90) if not hover_predict else (88, 91, 112))
        draw_button(screen, font, btn_clear, "Clear", hover_clear, (243, 139, 168) if hover_clear else (69, 71, 90))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
