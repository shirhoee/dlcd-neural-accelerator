#!/usr/bin/env python3
"""
M16: Local Hand-Drawn Digit Testing — Tkinter UI
Clean, modern drawing canvas with live prediction display.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import torch
import torch.nn as nn
import subprocess
import os
import sys
from PIL import Image, ImageDraw, ImageTk

# Use the correct Python for subprocess calls
PYTHON_EXE = r"C:\Users\SHREYANSH RAJ\AppData\Local\Programs\Python\Python312\python.exe"
IVERILOG_PATH = r"C:\iverilog\bin\iverilog.exe"
VVP_PATH = r"C:\iverilog\bin\vvp.exe"
VERILOG_SRC = "verilog_src"

# Canvas settings
CANVAS_SIZE = 400  # Larger canvas for comfortable drawing
GRID_SIZE = 10     # Target 10x10 for model
STROKE_WIDTH = 24  # Thicker stroke for better downsampling

# Colors (modern palette)
BG_COLOR = "#f5f5f5"
CANVAS_BG = "#ffffff"
CANVAS_BORDER = "#cccccc"
PRIMARY_BLUE = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
DANGER_RED = "#dc2626"
DANGER_HOVER = "#b91c1c"
SECONDARY_GRAY = "#6b7280"
SECONDARY_HOVER = "#4b5563"
TEXT_DARK = "#1f2937"
TEXT_MEDIUM = "#4b5563"
TEXT_LIGHT = "#9ca3af"
PREVIEW_CELL_SIZE = 28  # Each 10x10 cell rendered at 28px = 280px preview

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

class HandDrawnApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M16: Hand-Drawn Digit Classifier")
        self.root.geometry("900x550")
        self.root.minsize(850, 500)
        self.root.configure(bg=BG_COLOR)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        
        # Model (loaded lazily on first predict)
        self.model = None
        
        # Drawing state
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
        # PIL image for drawing (better quality than tkinter canvas)
        self.pil_image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
        self.draw = ImageDraw.Draw(self.pil_image)
        
        # UI state
        self.golden_pred = None
        self.hw_pred = None
        self.max_logit = 0.0
        self.last_img_10x10 = None
        
        self._build_ui()
        
    def _configure_styles(self):
        self.style.configure('Primary.TButton',
            font=('Segoe UI', 11, 'bold'),
            foreground='white',
            background=PRIMARY_BLUE,
            borderwidth=0,
            focusthickness=0,
            padding=(20, 10))
        self.style.map('Primary.TButton',
            background=[('active', PRIMARY_HOVER), ('pressed', PRIMARY_BLUE)])
        
        self.style.configure('Danger.TButton',
            font=('Segoe UI', 11, 'bold'),
            foreground='white',
            background=DANGER_RED,
            borderwidth=0,
            focusthickness=0,
            padding=(20, 10))
        self.style.map('Danger.TButton',
            background=[('active', DANGER_HOVER), ('pressed', DANGER_RED)])
        
        self.style.configure('Secondary.TButton',
            font=('Segoe UI', 11),
            foreground='white',
            background=SECONDARY_GRAY,
            borderwidth=0,
            focusthickness=0,
            padding=(20, 10))
        self.style.map('Secondary.TButton',
            background=[('active', SECONDARY_HOVER), ('pressed', SECONDARY_GRAY)])
        
        self.style.configure('Title.TLabel',
            font=('Segoe UI', 18, 'bold'),
            foreground=TEXT_DARK,
            background=BG_COLOR)
        
        self.style.configure('Subtitle.TLabel',
            font=('Segoe UI', 11),
            foreground=TEXT_MEDIUM,
            background=BG_COLOR)
        
        self.style.configure('Prediction.TLabel',
            font=('Segoe UI', 32, 'bold'),
            foreground=TEXT_DARK,
            background=BG_COLOR)
        
        self.style.configure('Detail.TLabel',
            font=('Segoe UI', 11),
            foreground=TEXT_MEDIUM,
            background=BG_COLOR)
        
        self.style.configure('Card.TFrame',
            background='white',
            borderwidth=1,
            relief='solid')
    
    def _build_ui(self):
        # Main container with padding
        main = ttk.Frame(self.root, padding=20, style='Card.TFrame')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = ttk.Frame(main, style='Card.TFrame')
        header.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header, text="Hand-Drawn Digit Classifier", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header, text="Draw a digit (0-9) on the canvas, then click PREDICT", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(4, 0))
        
        # Content area: canvas left, results right
        content = ttk.Frame(main, style='Card.TFrame')
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Canvas
        left_panel = ttk.Frame(content, style='Card.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Canvas wrapper with border
        canvas_wrapper = tk.Frame(left_panel, bg=CANVAS_BORDER, bd=0)
        canvas_wrapper.pack(pady=(0, 16))
        
        self.canvas = tk.Canvas(
            canvas_wrapper,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=CANVAS_BG,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(padx=2, pady=2)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self._on_draw_start)
        self.canvas.bind('<B1-Motion>', self._on_draw_motion)
        self.canvas.bind('<ButtonRelease-1>', self._on_draw_end)
        
        # Canvas buttons
        canvas_btns = ttk.Frame(left_panel, style='Card.TFrame')
        canvas_btns.pack(fill=tk.X)
        
        ttk.Button(canvas_btns, text="Clear Canvas", style='Secondary.TButton',
            command=self._clear_canvas).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(canvas_btns, text="Predict", style='Primary.TButton',
            command=self._on_predict).pack(side=tk.LEFT)
        
        # Right panel - Results
        right_panel = ttk.Frame(content, style='Card.TFrame', width=380)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Prediction display
        pred_card = ttk.Frame(right_panel, style='Card.TFrame', padding=20)
        pred_card.pack(fill=tk.X, pady=(0, 16))
        
        ttk.Label(pred_card, text="PREDICTION", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 8))
        
        self.pred_var = tk.StringVar(value="—")
        self.pred_label = ttk.Label(pred_card, textvariable=self.pred_var, style='Prediction.TLabel')
        self.pred_label.pack(anchor=tk.W)
        
        self.detail_var = tk.StringVar(value="Draw a digit and click PREDICT")
        ttk.Label(pred_card, textvariable=self.detail_var, style='Detail.TLabel').pack(anchor=tk.W, pady=(8, 0))
        
        # 10x10 Preview
        preview_card = ttk.Frame(right_panel, style='Card.TFrame', padding=20)
        preview_card.pack(fill=tk.X, pady=(0, 16))
        
        ttk.Label(preview_card, text="10×10 DOWNSAMPLED INPUT", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 12))
        
        self.preview_canvas = tk.Canvas(
            preview_card,
            width=PREVIEW_CELL_SIZE * 10,
            height=PREVIEW_CELL_SIZE * 10,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=CANVAS_BORDER
        )
        self.preview_canvas.pack()
        
        # Logit info
        logit_card = ttk.Frame(right_panel, style='Card.TFrame', padding=20)
        logit_card.pack(fill=tk.X)
        
        self.logit_var = tk.StringVar(value="Max |logit|: — (Q7.8 limit: ±127.99)")
        self.logit_label = ttk.Label(logit_card, textvariable=self.logit_var, style='Detail.TLabel')
        self.logit_label.pack(anchor=tk.W)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Model loads on first prediction.")
        status_bar = ttk.Label(main, textvariable=self.status_var, style='Detail.TLabel', anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(16, 0))
    
    def _load_model(self):
        """Load the 93.06% baseline model from cached Q7.8 hex weights."""
        if self.model is not None:
            return True
            
        w1_path = os.path.join(VERILOG_SRC, "e2e_w1.hex")
        w2_path = os.path.join(VERILOG_SRC, "e2e_w2.hex")
        w3_path = os.path.join(VERILOG_SRC, "e2e_w3.hex")
        
        if not (os.path.exists(w1_path) and os.path.exists(w2_path) and os.path.exists(w3_path)):
            self.status_var.set("ERROR: Weight files not found. Run train_model.py first.")
            return False
        
        self.model = VerilogNet()
        
        w1_flat = np.array([int(line.strip(), 16) for line in open(w1_path)])
        w2_flat = np.array([int(line.strip(), 16) for line in open(w2_path)])
        w3_flat = np.array([int(line.strip(), 16) for line in open(w3_path)])
        
        def to_signed(v): return v - 65536 if (v & 0x8000) else v
        w1 = np.array([to_signed(v) for v in w1_flat]).reshape(16, 100).astype(np.float32) / 256.0
        w2 = np.array([to_signed(v) for v in w2_flat]).reshape(6, 16).astype(np.float32) / 256.0
        w3 = np.array([to_signed(v) for v in w3_flat]).reshape(10, 6).astype(np.float32) / 256.0
        
        with torch.no_grad():
            self.model.fc1.weight.copy_(torch.from_numpy(w1))
            self.model.fc2.weight.copy_(torch.from_numpy(w2))
            self.model.fc3.weight.copy_(torch.from_numpy(w3))
        
        self.model.eval()
        self.status_var.set("Model loaded (93.06% baseline). Ready.")
        return True
    
    def _on_draw_start(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
    
    def _on_draw_motion(self, event):
        if not self.drawing or self.last_x is None:
            return
        
        # Draw on tkinter canvas (for visual feedback)
        self.canvas.create_line(
            self.last_x, self.last_y, event.x, event.y,
            fill='black', width=STROKE_WIDTH,
            capstyle=tk.ROUND, smooth=True, splinesteps=12
        )
        
        # Draw on PIL image (for actual processing)
        self.draw.line(
            [self.last_x, self.last_y, event.x, event.y],
            fill='black', width=STROKE_WIDTH,
            joint='curve'
        )
        
        self.last_x = event.x
        self.last_y = event.y
    
    def _on_draw_end(self, event):
        self.drawing = False
        self.last_x = None
        self.last_y = None
    
    def _clear_canvas(self):
        self.canvas.delete("all")
        self.pil_image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
        self.draw = ImageDraw.Draw(self.pil_image)
        self.golden_pred = None
        self.hw_pred = None
        self.max_logit = 0.0
        self.last_img_10x10 = None
        self.pred_var.set("—")
        self.detail_var.set("Draw a digit and click PREDICT")
        self.logit_var.set("Max |logit|: — (Q7.8 limit: ±127.99)")
        self._clear_preview()
        self.status_var.set("Canvas cleared. Draw a digit and click PREDICT.")
    
    def _clear_preview(self):
        self.preview_canvas.delete("all")
    
    def _downsample_to_10x10(self, pil_img):
        """
        Preprocessing: PIL image (400x400) -> 10x10 normalized [0,1]
        1. Convert to grayscale, invert
        2. Find bounding box, square crop (centered)
        3. Average-pool resize to 8x8
        4. Pad to 10x10
        5. Normalize /255
        """
        # Convert to grayscale array
        gray = np.array(pil_img.convert('L'), dtype=np.float32)  # (H, W)
        
        # Invert: white(255) -> 0.0, black(0) -> 1.0 (before normalize)
        gray = 255.0 - gray
        
        # Find bounding box of non-zero pixels
        rows = np.any(gray > 10, axis=1)
        cols = np.any(gray > 10, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return np.zeros((10, 10), dtype=np.float32)
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # Square crop (centered, like sklearn digits)
        h = rmax - rmin + 1
        w = cmax - cmin + 1
        size = max(h, w)
        r_center = (rmin + rmax) // 2
        c_center = (cmin + cmax) // 2
        half = size // 2
        
        rmin_sq = max(0, r_center - half)
        rmax_sq = min(gray.shape[0] - 1, r_center + half)
        cmin_sq = max(0, c_center - half)
        cmax_sq = min(gray.shape[1] - 1, c_center + half)
        
        # Adjust boundaries
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
        
        cropped = gray[rmin_sq:rmax_sq+1, cmin_sq:cmax_sq+1]
        
        # Average-pool resize to 8x8
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
        
        # Pad to 10x10 with 1px border
        padded = np.pad(resized, ((1, 1), (1, 1)), mode='constant', constant_values=0)
        
        # Normalize to [0.0, 1.0]
        normalized = padded / 255.0
        
        return normalized
    
    def _render_preview(self, img_10x10):
        """Render 10x10 grid as scaled-up image on preview canvas."""
        self.preview_canvas.delete("all")
        for i in range(10):
            for j in range(10):
                val = img_10x10[i, j]
                # Map 0.0-1.0 to 255-0 (white to black)
                intensity = int((1.0 - val) * 255)
                color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                x1 = j * PREVIEW_CELL_SIZE
                y1 = i * PREVIEW_CELL_SIZE
                x2 = x1 + PREVIEW_CELL_SIZE
                y2 = y1 + PREVIEW_CELL_SIZE
                self.preview_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#e5e7eb")
                # Add value text for non-zero cells
                if val > 0.05:
                    text_color = "white" if val > 0.5 else "black"
                    self.preview_canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text=f"{val:.2f}", fill=text_color, font=('Segoe UI', 8)
                    )
    
    def _to_q7_8_hex(self, val):
        v_int = int(val * 256)
        return f"{v_int & 0xFFFF:04x}"
    
    def _write_input_hex(self, img_10x10, filename):
        with open(filename, 'w') as f:
            for row in img_10x10:
                for val in row:
                    f.write(self._to_q7_8_hex(val) + "\n")
    
    def _golden_predict(self, img_10x10):
        inp = torch.tensor(img_10x10.flatten(), dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(inp)
            pred = torch.argmax(logits, dim=1).item()
            max_logit = logits.abs().max().item()
        return pred, max_logit
    
    def _run_verilog_sim(self):
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
    
    def _on_predict(self):
        if not self._load_model():
            return
        
        self.status_var.set("Processing...")
        self.root.update()
        
        # Downsample
        img_10x10 = self._downsample_to_10x10(self.pil_image)
        self.last_img_10x10 = img_10x10
        
        # Write input hex
        self._write_input_hex(img_10x10, os.path.join(VERILOG_SRC, "e2e_input.hex"))
        
        # Golden prediction
        self.golden_pred, self.max_logit = self._golden_predict(img_10x10)
        
        # Verilog simulation
        self.hw_pred, err = self._run_verilog_sim()
        if err:
            self.detail_var.set(f"Error: {err}")
            self.hw_pred = None
            self.status_var.set("Simulation error")
            return
        
        # Update UI
        match = "✓ MATCH" if self.golden_pred == self.hw_pred else "✗ MISMATCH"
        self.pred_var.set(str(self.golden_pred))
        self.detail_var.set(f"Golden: {self.golden_pred}  |  Hardware: {self.hw_pred}  |  {match}")
        self.logit_var.set(f"Max |logit|: {self.max_logit:.2f} (Q7.8 limit: ±127.99)")
        
        # Render preview
        self._render_preview(img_10x10)
        
        self.status_var.set("Prediction complete. Draw another or clear.")
    
    def run(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = HandDrawnApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()