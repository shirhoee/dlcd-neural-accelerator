export const GRID_SIZE = 28;
export const CANVAS_SIZE = 280;

/**
 * Extracts a normalized 28x28 grayscale grid (values in [0.0, 1.0])
 * from a 280x280 HTML5 canvas using 10x10 block-averaging.
 */
export function extract28x28FromCanvas(canvas: HTMLCanvasElement): number[][] {
  const ctx = canvas.getContext('2d');
  if (!ctx) return [];

  const imageData = ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE).data;
  const grid: number[][] = Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0));
  const scale = CANVAS_SIZE / GRID_SIZE; // 10

  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      let sum = 0;
      for (let y = 0; y < scale; y++) {
        for (let x = 0; x < scale; x++) {
          const px = c * scale + x;
          const py = r * scale + y;
          const idx = (py * CANVAS_SIZE + px) * 4;
          sum += imageData[idx]; // Red channel of grayscale
        }
      }
      grid[r][c] = sum / (scale * scale) / 255.0;
    }
  }

  return grid;
}
