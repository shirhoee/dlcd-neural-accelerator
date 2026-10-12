export interface Coordinate {
  x: number;
  y: number;
}

export interface PredictRequest {
  image: number[][];
}

export interface PredictResponse {
  prediction: number;
  logits: number[];
  dense1: number[];
  dense2: number[];
  input: number[][];
  mp1: number[][][]; // 4 channels x 10 rows x 10 cols
  mp2: number[][][]; // 8 channels x 5 rows x 5 cols
}

export interface FeatureGridProps {
  data: number[][];
  colorHex: string;
}
