---
trigger: model_decision
description: Apply these guidelines whenever working on the backend, FastAPI routes, Pydantic schemas, or simulation service logic.
---

## Backend Architecture & Patterns (FastAPI + Pydantic v2 + Icarus Verilog Orchestration)

### 1. API Design & Validation
* **Strict Pydantic Schemas:** All request and response payloads must be modeled with Pydantic v2 classes:
  ```python
  from pydantic import BaseModel, Field, field_validator

  class PredictRequest(BaseModel):
      image: list[list[float]] = Field(..., description="28x28 normalized grayscale pixel matrix")

      @field_validator("image")
      @classmethod
      def validate_dimensions(cls, v: list[list[float]]) -> list[list[float]]:
          if len(v) != 28 or any(len(row) != 28 for row in v):
              raise ValueError("Input image must be a 28x28 matrix.")
          return v
  ```
* **Consistent Error Handling:** Catch `subprocess.CalledProcessError`, `FileNotFoundError`, and parsing errors gracefully. Return standardized error payloads (`HTTP 400` or `HTTP 500` with JSON detail message).

### 2. Concurrency & Subprocess Execution
* **Asynchronous Offloading:** Never invoke synchronous `subprocess.run` directly in the async route handler. Offload hardware simulation to a worker thread:
  ```python
  result = await asyncio.to_thread(run_simulation, image_20)
  ```
  This preserves FastAPI's responsiveness under concurrent UI requests.
* **Hermetic Execution:** Always compile and execute in an isolated `tempfile.TemporaryDirectory()`. Never overwrite shared global test image files (e.g. `test_image_q7_8.txt`), preventing file-lock races.

### 3. Toolchain & Environment Portability
* **Dynamic Locator:** Locate executables dynamically using `shutil.which`:
  ```python
  def get_iverilog_path() -> str:
      path = shutil.which("iverilog")
      if path:
          return path
      win_default = r"C:\iverilog\bin\iverilog.exe"
      if os.path.exists(win_default):
          return win_default
      raise FileNotFoundError("Icarus Verilog ('iverilog') executable not found.")
  ```
* **No Machine Hardcoding:** Do not bake single-machine Windows absolute paths into the codebase without fallback.

### 4. Quantization & Math Fidelity
* **Normalization Constants:** Use exact standard MNIST parameters ($\mu = 0.1307, \sigma = 0.3081$).
* **Q7.8 Integer Conversion:** Scale with multiplier 256.0:
  $$\text{val}_{\text{q7\_8}} = \text{clamp}(\text{round}((\text{val} - 0.1307) / 0.3081 \times 256.0), -32768, 32767)$$
