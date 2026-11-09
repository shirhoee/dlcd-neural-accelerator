# Complete Frontend UI Remapping & Interactive Hardware Studio Implementation Plan (Step 2)

## Goal Description
Remap and rebuild the entire frontend application into a responsive, high-performance **Deep-Tech Hardware Accelerator Studio**. The application structure directly mirrors the **PES University UE25CS251A Laboratory Report** format with minimal text, fluid CSS/SVG keyframe animations, rich graphs, and tactile micro-interactions.

### Key Deliverables:
1. **Persistent Header:** Displays the full official project title, PES University course metadata, and the names + SRNs of all four project members.
2. **Report-Order Navigation:** Seamless navigation across the 8 sections of the lab report:
   * **1. Problem Statement** (Specs, Q7.8 constraints, latency & throughput goals).
   * **2. Universal Circuit Diagram** (Interactive top-level datapath connecting every module; clicking any module opens an inspection modal with gate-level schematics, pinout tables, and Verilog contracts).
   * **3. FSM State Machines** (Interactive visual state transition diagrams for `conv_pe`, `window_gen`, and `mlp_head`).
   * **4. Literature Survey (V1 vs V2 Comparison)** (Direct architectural, accuracy, and hardware resource comparison between Version 1 MLP and Version 2 CNN).
   * **5. Main Verilog Code** (Tabbed, syntax-highlighted RTL source browser).
   * **6. Hardware Inference Dashboards** (Dedicated V2 Glass-Box Studio, Dedicated V1 Baseline Dashboard, and Side-by-Side Live Dual Inference).
   * **7. Waveform & Output Analysis** (GTKWave cycle-accurate timing traces, latency breakdown waterfall charts, confusion matrix).
   * **8. References** (Academic citations).
3. **Backend Support for V1 & Dual Comparison:** Add `/predict/v1` and `/predict/compare` endpoints in FastAPI so both V1 and V2 can be drawn, simulated, and compared in real time.

---

## User Review Required

> [!IMPORTANT]
> **Unified Single-Page App with Smooth Scroll and Tab Anchors:** The UI will feature a sticky top navigation bar allowing users to either click any of the 8 report sections for instant smooth scrolling, or toggle between sections.

> [!NOTE]
> **Performance Architecture:** All animations (wavefront pulses, hover glows, modal transitions) use GPU-composited CSS transforms and opacity (`will-change: transform`). Canvas heatmaps are rendered using offscreen direct pixel buffers to ensure a consistent 60 FPS without layout thrashing.

---

## Open Questions

> [!NOTE]
> None. All requirements, team SRNs, Verilog module hierarchies, and V1/V2 weights have been validated in the codebase.

---

## Proposed Changes

### 1. Backend: V1 Inference & Dual Comparison Endpoints

#### [NEW] `v2/v2_ui/backend/v1_runner.py`
* Bit-exact Python Q7.8 integer runner for the Version 1 MLP architecture ($100 \rightarrow 16 \rightarrow 6 \rightarrow 10$):
  * Loads `v1/verilog_src/e2e_w1.hex`, `e2e_w2.hex`, `e2e_w3.hex`.
  * Downsamples $28\times 28$ input to $10\times 10$ using bounding-box center-of-mass alignment.
  * Evaluates sequential fixed-point MACs matching V1 RTL.
  * Returns `prediction`, `logits`, `layer1` (16 units), `layer2` (6 units), and simulated latency (6,139 clock cycles).

#### [MODIFY] `v2/v2_ui/backend/schemas.py`
* Add schemas for `V1PredictResponse` and `ComparePredictResponse`:
```python
class V1PredictResponse(BaseModel):
    prediction: int
    logits: List[float]
    layer1: List[float]
    layer2: List[float]
    input_10x10: List[List[float]]
    cycles: int = 6139
    accuracy_baseline: float = 93.06

class ComparePredictResponse(BaseModel):
    v1: V1PredictResponse
    v2: PredictResponse
    agreement: bool
```

#### [MODIFY] `v2/v2_ui/backend/main.py`
* Add `POST /predict/v1` and `POST /predict/compare` routes.

---

### 2. Frontend: Types, Navigation, and Theme System

#### [MODIFY] `v2/v2_ui/frontend/src/types/api.ts`
* Update TypeScript definitions to include `V1PredictResponse`, `ComparePredictResponse`, and Circuit Module Inspection metadata.

#### [NEW] `v2/v2_ui/frontend/src/types/circuit.ts`
* Data structures for the Universal Circuit Diagram nodes:
```typescript
export interface CircuitModuleNode {
  id: string;
  name: string;
  category: 'frontend' | 'conv1' | 'pool1' | 'conv2' | 'pool2' | 'mlp' | 'output';
  description: string;
  verilogFile: string;
  ports: { name: string; direction: 'in' | 'out'; width: string; desc: string }[];
  fsmName?: string;
  svgSchematic?: string;
}
```

#### [MODIFY] `v2/v2_ui/frontend/src/App.module.css`
* Replace legacy styles with the **Obsidian Silicon Studio** theme (`#07090e` base, glassmorphism, glowing cyan/indigo/emerald borders, smooth animations).

---

### 3. Frontend: Top Navigation & Team Banner

#### [NEW] `v2/v2_ui/frontend/src/components/Header/TeamHeader.tsx`
* Fixed sticky top bar:
  * University Title: **PES UNIVERSITY | UE25CS251A DLCD LABORATORY**
  * Project Title: **CNN HARDWARE ACCELERATOR (Q7.8 FIXED-POINT)**
  * Four member badges with SRNs:
    * `Shreyansh Raj (PES2UG25CS516)`
    * `Sarthak Bhowmik (PES2UG25CS493)`
    * `Shaurya Singh (PES2UG25CS508)`
    * `Shreya Anand (PES2UG25CS515)`
  * Report Section Tabs:
    `[ 1. Problem ]` `[ 2. Circuit Diagram ]` `[ 3. FSM ]` `[ 4. V1 vs V2 ]` `[ 5. Verilog ]` `[ 6. Dashboards ]` `[ 7. Waveforms ]` `[ 8. References ]`

---

### 4. Frontend: Interactive Universal Circuit Diagram & Drill-Down Modal

#### [NEW] `v2/v2_ui/frontend/src/components/Circuit/UniversalCircuitDiagram.tsx`
* Interactive, zoomable SVG datapath diagram connecting all functional modules:
  * `window_gen` $\rightarrow$ `conv1_array` (4x `conv_pe`) $\rightarrow$ `pool_window_gen` $\rightarrow$ `maxpool_array` $\rightarrow$ `conv2_window_gen` $\rightarrow$ `conv2_array` (8x `conv2_pe`) $\rightarrow$ `pool2_window_gen` $\rightarrow$ `maxpool2_array` $\rightarrow$ `mlp_head` (Systolic Array) $\rightarrow$ `argmax`.
  * Bus wires animate signal flow with glowing pulses.
  * Clicking any module opens the `ModuleInspectorModal`.

#### [NEW] `v2/v2_ui/frontend/src/components/Circuit/ModuleInspectorModal.tsx`
* Detailed drill-down view showing:
  * Gate-level block diagram.
  * Interface port table with active levels and bit-widths.
  * Associated FSM diagram (if module contains state logic).
  * Direct Verilog source preview for that module.

---

### 5. Frontend: FSM State Machine Visualizer

#### [NEW] `v2/v2_ui/frontend/src/components/FSM/FsmVisualizer.tsx`
* Interactive state machine diagrams for:
  1. **`conv_pe` Modulo-9 Tap Counter:** `IDLE` $\rightarrow$ `ACCUMULATE (Taps 0..8)` $\rightarrow$ `VALID_PULSE`.
  2. **`window_gen` 3x3 Line Buffer Sequencer:** State transitions tracking 22x22 padded grid stream and output valid flags.
  3. **`mlp_head` 4-State Systolic Controller:** `IDLE` $\rightarrow$ `LOAD_WEIGHT` $\rightarrow$ `COMPUTE` $\rightarrow$ `DONE`, cycling through Dense 1 ($200\rightarrow 64$), Dense 2 ($64\rightarrow 32$), Dense 3 ($32\rightarrow 10$) with dual ping-pong RAM ping-ponging.
* Interactive state stepper button to step through clock cycles.

---

### 6. Frontend: V1 vs V2 Visual Comparison

#### [NEW] `v2/v2_ui/frontend/src/components/Comparison/V1V2Comparison.tsx`
* Comprehensive visual comparison:
  * **Interactive Metrics Cards:** Accuracy (93.06% vs 98.83%), Multiplier footprint (256 vs 256 reused), Clock Cycles (6,139 vs 9,116), Input Resolution ($10\times 10$ vs $20\times 20$).
  * **Side-by-Side Topology Visualizer:** Comparing 3-layer flat MLP against 6-layer CNN pipeline.
  * **Bar Chart Comparison:** Accuracy comparison on clean vs noisy/distorted digits.
  * **Tradeoff Breakdown:** Why convolutional filtering and fused pooling resolved the downsampling bottleneck.

---

### 7. Frontend: Inference Dashboards (V2 Studio, V1 Dashboard, Dual Compare)

#### [NEW] `v2/v2_ui/frontend/src/components/Dashboards/DashboardTabs.tsx`
* Tabbed switcher for the three operating modes:
  * **Mode A: V2 Glass-Box Studio:** Smooth Bézier canvas, 1-click digit presets `[0]` to `[9]`, 5-stage animated hardware wavefront, MaxPool1 & MaxPool2 heatmaps, Dense 1 & 2 activation grids, Q7.8 hover inspector, Softmax probability chart.
  * **Mode B: V1 Baseline Dashboard:** $10\times 10$ canvas drawing, 16-neuron Layer 1 and 6-neuron Layer 2 visual bars, 10 output logits.
  * **Mode C: Side-by-Side Live Dual Inference:** Single canvas input feeds both V1 and V2 in parallel; outputs side-by-side predictions, confidence scores, and latency readouts.

#### [NEW] `v2/v2_ui/frontend/src/components/Canvas/PresetRibbon.tsx`
* Quick-select ribbon for digits `[0]` through `[9]` triggering instantaneous hardware evaluation.

#### [NEW] `v2/v2_ui/frontend/src/components/Waveform/WaveformViewer.tsx`
* Interactive digital timing diagram showing GTKWave clock cycles: `clk`, `reset`, `start`, `mp1_valid`, `mp2_valid`, `d_valid`, `done`, `prediction`.

---

## Verification Plan

### Automated Tests
1. **Frontend Lint & Typecheck:**
   ```cmd
   cd v2\v2_ui\frontend
   npm run lint
   npx tsc --noEmit
   ```
2. **Frontend Production Build:**
   ```cmd
   cd v2\v2_ui\frontend
   npm run build
   ```
3. **Backend API Endpoints Verification:**
   ```cmd
   curl -X POST http://127.0.0.1:8000/predict/v1 ...
   curl -X POST http://127.0.0.1:8000/predict/compare ...
   ```
4. **Hardware RTL Sanity Regression:**
   ```cmd
   cd v2\regression
   python test_10.py
   ```

### Manual Verification
* Verify all 8 report navigation sections scroll and navigate smoothly.
* Click modules in the Universal Circuit Diagram and confirm the modal inspector opens with gate-level schematics and pinouts.
* Draw digits and verify the 5-stage animated wavefront sweeps across Conv1 $\rightarrow$ MP1 $\rightarrow$ Conv2 $\rightarrow$ MP2 $\rightarrow$ Dense $\rightarrow$ Argmax.
* Switch to V1 Dashboard and Side-by-Side Dual Inference mode to verify live concurrent evaluation.
