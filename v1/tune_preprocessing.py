import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as ndimage

CANVAS_SIZE = 400
STROKE_WIDTH = 24

def generate_test_images():
    images = []
    
    # 1: straight line
    img1 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d1 = ImageDraw.Draw(img1)
    d1.line([200, 50, 200, 350], fill='black', width=STROKE_WIDTH)
    images.append(img1)
    
    # 8: figure 8
    img2 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d2 = ImageDraw.Draw(img2)
    d2.ellipse([150, 80, 250, 200], outline='black', width=STROKE_WIDTH)
    d2.ellipse([140, 190, 260, 320], outline='black', width=STROKE_WIDTH)
    images.append(img2)
    
    # 2: curve and line
    img3 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d3 = ImageDraw.Draw(img3)
    d3.arc([100, 50, 300, 250], start=180, end=0, fill='black', width=STROKE_WIDTH)
    d3.line([300, 150, 100, 350], fill='black', width=STROKE_WIDTH)
    d3.line([100, 350, 300, 350], fill='black', width=STROKE_WIDTH)
    images.append(img3)
    
    # 0: circle
    img4 = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), 'white')
    d4 = ImageDraw.Draw(img4)
    d4.ellipse([100, 50, 300, 350], outline='black', width=STROKE_WIDTH)
    images.append(img4)
    
    return images

def test_preprocessing(pil_img, erode_iters, blur_sigma):
    gray = np.array(pil_img.convert('L'), dtype=np.float32)
    gray = 255.0 - gray
    
    rows = np.any(gray > 10, axis=1)
    cols = np.any(gray > 10, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return 0, 0
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    # ---------------- INSERTION ----------------
    if erode_iters > 0:
        gray = ndimage.binary_erosion(gray > 10, iterations=erode_iters).astype(np.float32) * 255.0
    if blur_sigma > 0:
        gray = ndimage.gaussian_filter(gray, sigma=blur_sigma)
    # -------------------------------------------
    
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
    images = generate_test_images()
    target_mean = 0.1954
    target_nz = 0.3269
    
    best_err = float('inf')
    best_params = (0, 0)
    best_stats = (0, 0)
    
    # Baseline
    means, nzs = [], []
    for img in images:
        m, nz = test_preprocessing(img, 0, 0)
        means.append(m)
        nzs.append(nz)
    print(f"Baseline (no processing): Mean={np.mean(means):.4f}, NZ={np.mean(nzs):.4f}")
    
    for erode in range(1, 15):
        for blur in np.arange(1.0, 10.0, 0.5):
            means, nzs = [], []
            for img in images:
                m, nz = test_preprocessing(img, erode, blur)
                means.append(m)
                nzs.append(nz)
            
            avg_m = np.mean(means)
            avg_nz = np.mean(nzs)
            
            err = abs(avg_m - target_mean) + abs(avg_nz - target_nz)
            if err < best_err:
                best_err = err
                best_params = (erode, blur)
                best_stats = (avg_m, avg_nz)
                
    print(f"\nBest parameters: Erode={best_params[0]}, Blur={best_params[1]}")
    print(f"Resulting Mean: {best_stats[0]:.4f} (Target: {target_mean:.4f})")
    print(f"Resulting NZ: {best_stats[1]:.4f} (Target: {target_nz:.4f})")

if __name__ == "__main__":
    main()
