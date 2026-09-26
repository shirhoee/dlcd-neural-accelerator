import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as ndimage

CANVAS_SIZE = 400
STROKE_WIDTH = 32  # Made thicker to match theoretical ~0.24 mean

def generate_thick_digits():
    images = []
    # Digit '0'
    img0 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d0 = ImageDraw.Draw(img0)
    d0.ellipse([100, 100, 300, 300], outline='black', width=STROKE_WIDTH)
    images.append(img0)
    
    # Digit '8'
    img8 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d8 = ImageDraw.Draw(img8)
    d8.ellipse([120, 80, 280, 190], outline='black', width=STROKE_WIDTH)
    d8.ellipse([120, 190, 280, 320], outline='black', width=STROKE_WIDTH)
    images.append(img8)
    
    # Digit '3'
    img3 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d3 = ImageDraw.Draw(img3)
    d3.arc([100, 80, 280, 200], start=270, end=90, fill='black', width=STROKE_WIDTH)
    d3.arc([100, 200, 280, 320], start=270, end=90, fill='black', width=STROKE_WIDTH)
    images.append(img3)
    
    return images

def process_digit(pil_img, erode_iters, blur_sigma):
    gray = np.array(pil_img.convert('L'), dtype=np.float32)
    gray = 255.0 - gray
    
    rows = np.any(gray > 10, axis=1)
    cols = np.any(gray > 10, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return 0, 0
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    if erode_iters > 0:
        gray = ndimage.binary_erosion(gray > 10, iterations=erode_iters).astype(np.float32) * 255.0
    if blur_sigma > 0:
        gray = ndimage.gaussian_filter(gray, sigma=blur_sigma)
    
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
                
    padded = np.pad(resized, ((1, 1), (1, 1)), mode='constant', constant_values=0)
    normalized = padded / 255.0
    
    return np.mean(normalized), np.mean(normalized > 0.05)

def main():
    images = generate_thick_digits()
    target_mean = 0.1954
    target_nz = 0.3269
    
    means, nzs = [], []
    for img in images:
        m, nz = process_digit(img, 0, 0)
        means.append(m)
        nzs.append(nz)
    print(f"Baseline (no processing): Mean={np.mean(means):.4f}, NZ={np.mean(nzs):.4f}")
    
    results = []
    for erode in range(1, 15):
        for blur in np.arange(1.0, 8.0, 0.5):
            means, nzs = [], []
            for img in images:
                m, nz = process_digit(img, erode, blur)
                means.append(m)
                nzs.append(nz)
            
            avg_m = np.mean(means)
            avg_nz = np.mean(nzs)
            
            err = abs(avg_m - target_mean)/target_mean + abs(avg_nz - target_nz)/target_nz
            results.append((err, erode, blur, avg_m, avg_nz))
            
    results.sort(key=lambda x: x[0])
    for i in range(5):
        err, erode, blur, m, nz = results[i]
        print(f"Rank {i+1}: Erode={erode}, Blur={blur} -> Mean={m:.4f}, NZ={nz:.4f} (Err={err:.4f})")

if __name__ == "__main__":
    main()
