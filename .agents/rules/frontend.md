---
trigger: model_decision
description: Apply these guidelines whenever working on the frontend, UI components, styling, or client-side React/TypeScript code.
---

## Frontend Architecture & Patterns (React 19 + TypeScript + Vite)

### 1. Component Architecture & Separation of Concerns
* **Single Responsibility:** Break large components down into modular units:
  * `CanvasBoard.tsx`: Manages touch/pointer events, 280×280 HTML5 canvas, 24px round brush, clear action, and coordinate transformations.
  * `FeatureGrid.tsx`: Pure presentation component rendering 2D spatial feature map channels with custom tinting and opacity mapping.
  * `LogitChart.tsx`: Renders probability distribution bars with dynamic temperature scaling.
* **Custom Hooks:** Encapsulate stateful asynchronous logic (e.g. `usePredict.ts` managing fetch lifecycle, loading state, and error handling) away from presentational components.
* **Pure Utility Functions:** Keep mathematical transforms like image downsampling (`downsample.ts`) in pure, unit-testable TypeScript modules.

### 2. TypeScript & Type Safety
* **Strict Typing:** Always enable strict TypeScript rules. Never use `any`.
* **Explicit Interfaces:** Define interfaces for all component props and API payloads in `src/types/api.ts`:
  ```typescript
  export interface PredictResponse {
    prediction: number;
    logits: number[];
    dense1: number[];
    dense2: number[];
    input: number[][];
    mp1: number[][][];
    mp2: number[][][];
  }
  ```
* **Read-only Props:** Prefer immutable prop types where appropriate (`readonly number[]`).

### 3. Styling & User Experience
* **CSS Modules:** Use scoped CSS Modules (`App.module.css` or component-specific `*.module.css`) to prevent global style collisions.
* **Canvas Coordinate Scaling:** Always scale pointer events using `canvas.width / rect.width` and `canvas.height / rect.height` to ensure drawing tracks accurately across high-DPI displays and resized windows.
* **Interactive Feedback:** Provide clear visual states: disabled buttons during active simulation runs ("Running..."), loading spinners, and error alerts on network failure.

### 4. Code Quality & Linting
* **Linter:** Run `npm run lint` (`oxlint`) before marking changes complete.
* **Type-check:** Run `npx tsc --noEmit` to verify zero type errors.
