export const CANVAS_SIZE = 380;
export const GRID_SIZE = 28;
export const TARGET_V2_SIZE = 20;

export interface ExtractedDrawing {
  grid28: number[][]; // 28x28 normalized grayscale [0.0, 1.0]
  grid20: number[][]; // 20x20 downsampled for V2 accelerator
}

/**
 * Standard MNIST Centering & Preprocessing Pipeline:
 * 1. Bounding box extraction with aspect-ratio preservation (scaled into 20x20 box).
 * 2. Center-of-mass calculation across stroke pixels.
 * 3. Centering translation placing the center-of-mass exactly at (13.5, 13.5).
 * 4. High-fidelity bilinear resampling to generate clean 28x28 and 20x20 hardware matrices.
 */
export function extract28x28FromCanvas(canvas: HTMLCanvasElement): ExtractedDrawing {
  const ctx = canvas.getContext('2d');
  const emptyResult: ExtractedDrawing = {
    grid28: Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0)),
    grid20: Array.from({ length: TARGET_V2_SIZE }, () => Array(TARGET_V2_SIZE).fill(0)),
  };

  if (!ctx) return emptyResult;

  const width = canvas.width;
  const height = canvas.height;
  const imgData = ctx.getImageData(0, 0, width, height).data;

  // 1. Build luminance map [0.0, 1.0] from canvas
  const lum: number[][] = [];
  let minX = width;
  let maxX = -1;
  let minY = height;
  let maxY = -1;
  let totalMass = 0;

  for (let y = 0; y < height; y++) {
    const row: number[] = [];
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      // White digit on black background: use red/green/blue average
      const val = (imgData[idx] + imgData[idx + 1] + imgData[idx + 2]) / (3 * 255.0);
      row.push(val);
      if (val > 0.08) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
        totalMass += val;
      }
    }
    lum.push(row);
  }

  // If canvas is blank or virtually untouched, return empty matrices
  if (totalMass < 1.0 || minX > maxX || minY > maxY) {
    return emptyResult;
  }

  // 2. Crop to bounding box
  const bboxW = maxX - minX + 1;
  const bboxH = maxY - minY + 1;

  // 3. Scale bounding box so largest dimension fits into 20 pixels inside 28x28
  const targetBox = 20.0;
  const scale = targetBox / Math.max(bboxW, bboxH);
  const scaledW = Math.max(1, Math.round(bboxW * scale));
  const scaledH = Math.max(1, Math.round(bboxH * scale));

  // Resample cropped bbox to scaled dimensions
  const scaledCrop: number[][] = Array.from({ length: scaledH }, () => Array(scaledW).fill(0));
  for (let sy = 0; sy < scaledH; sy++) {
    for (let sx = 0; sx < scaledW; sx++) {
      const srcX = minX + sx / scale;
      const srcY = minY + sy / scale;

      const x0 = Math.floor(srcX);
      const x1 = Math.min(width - 1, x0 + 1);
      const y0 = Math.floor(srcY);
      const y1 = Math.min(height - 1, y0 + 1);

      const dx = srcX - x0;
      const dy = srcY - y0;

      const v00 = lum[y0]?.[x0] ?? 0;
      const v10 = lum[y0]?.[x1] ?? 0;
      const v01 = lum[y1]?.[x0] ?? 0;
      const v11 = lum[y1]?.[x1] ?? 0;

      const interpolated = (1 - dx) * (1 - dy) * v00 +
                           dx * (1 - dy) * v10 +
                           (1 - dx) * dy * v01 +
                           dx * dy * v11;
      scaledCrop[sy][sx] = interpolated;
    }
  }

  // 4. Calculate Center of Mass (COM) of the scaled digit
  let cropMass = 0;
  let sumX = 0;
  let sumY = 0;
  for (let sy = 0; sy < scaledH; sy++) {
    for (let sx = 0; sx < scaledW; sx++) {
      const v = scaledCrop[sy][sx];
      cropMass += v;
      sumX += sx * v;
      sumY += sy * v;
    }
  }

  const comX = cropMass > 0 ? sumX / cropMass : scaledW / 2;
  const comY = cropMass > 0 ? sumY / cropMass : scaledH / 2;

  // 5. Place scaled digit on 28x28 grid centered around COM at (13.5, 13.5)
  const grid28: number[][] = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0));
  const offsetX = 13.5 - comX;
  const offsetY = 13.5 - comY;

  for (let gy = 0; gy < GRID_SIZE; gy++) {
    for (let gx = 0; gx < GRID_SIZE; gx++) {
      const cropX = gx - offsetX;
      const cropY = gy - offsetY;

      if (cropX >= 0 && cropX < scaledW && cropY >= 0 && cropY < scaledH) {
        const cx0 = Math.floor(cropX);
        const cx1 = Math.min(scaledW - 1, cx0 + 1);
        const cy0 = Math.floor(cropY);
        const cy1 = Math.min(scaledH - 1, cy0 + 1);

        const dx = cropX - cx0;
        const dy = cropY - cy0;

        const v00 = scaledCrop[cy0][cx0];
        const v10 = scaledCrop[cy0][cx1];
        const v01 = scaledCrop[cy1][cx0];
        const v11 = scaledCrop[cy1][cx1];

        grid28[gy][gx] = Math.min(1.0, Math.max(0.0,
          (1 - dx) * (1 - dy) * v00 +
          dx * (1 - dy) * v10 +
          (1 - dx) * dy * v01 +
          dx * dy * v11
        ));
      }
    }
  }

  // 6. Bilinear downsample from 28x28 to 20x20 for V2 hardware accelerator
  const grid20: number[][] = Array.from({ length: TARGET_V2_SIZE }, () => Array(TARGET_V2_SIZE).fill(0));
  for (let y = 0; y < TARGET_V2_SIZE; y++) {
    for (let x = 0; x < TARGET_V2_SIZE; x++) {
      const srcX = (x + 0.5) * (GRID_SIZE / TARGET_V2_SIZE) - 0.5;
      const srcY = (y + 0.5) * (GRID_SIZE / TARGET_V2_SIZE) - 0.5;

      const x0 = Math.max(0, Math.floor(srcX));
      const x1 = Math.min(GRID_SIZE - 1, x0 + 1);
      const y0 = Math.max(0, Math.floor(srcY));
      const y1 = Math.min(GRID_SIZE - 1, y0 + 1);

      const dx = Math.max(0, Math.min(1, srcX - x0));
      const dy = Math.max(0, Math.min(1, srcY - y0));

      const v00 = grid28[y0][x0];
      const v10 = grid28[y0][x1];
      const v01 = grid28[y1][x0];
      const v11 = grid28[y1][x1];

      grid20[y][x] = Math.min(1.0, Math.max(0.0,
        (1 - dx) * (1 - dy) * v00 +
        dx * (1 - dy) * v10 +
        (1 - dx) * dy * v01 +
        dx * dy * v11
      ));
    }
  }

  return { grid28, grid20 };
}
