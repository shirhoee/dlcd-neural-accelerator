export interface Coordinate {
  x: number;
  y: number;
}

export interface PredictRequest {
  image: number[][]; // 28x28 normalized grayscale [0.0, 1.0]
}

export interface PredictResponse {
  prediction: number;
  logits: number[];
  dense1: number[];
  dense2: number[];
  input: number[][]; // 20x20
  mp1: number[][][]; // 4 channels x 10 rows x 10 cols
  mp2: number[][][]; // 8 channels x 5 rows x 5 cols
}

export interface V1PredictResponse {
  prediction: number;
  logits: number[];
  layer1: number[]; // 16 activations
  layer2: number[]; // 6 activations
  input_10x10: number[][];
  cycles: number;
  accuracy_baseline: number;
}

export interface ComparePredictResponse {
  v1: V1PredictResponse;
  v2: PredictResponse;
  agreement: boolean;
}

export interface TeamMember {
  name: string;
  srn: string;
  role: string;
  avatar: string;
}

export interface CircuitPort {
  name: string;
  direction: 'input' | 'output';
  width: string;
  description: string;
}

export interface CircuitModule {
  id: string;
  name: string;
  category: 'input' | 'conv1' | 'pool1' | 'conv2' | 'pool2' | 'mlp' | 'output';
  description: string;
  verilogFile: string;
  latencyCycles: string;
  arithmeticType: string;
  ports: CircuitPort[];
  schematicSummary: string[];
  verilogSnippet: string;
  fsmName?: string;
}

export interface FsmTransition {
  from: string;
  to: string;
  condition: string;
  action?: string;
}

export interface FsmDefinition {
  id: string;
  title: string;
  module: string;
  states: { name: string; desc: string; isInitial?: boolean; isFinal?: boolean }[];
  transitions: FsmTransition[];
  cycleBudget: string;
}
