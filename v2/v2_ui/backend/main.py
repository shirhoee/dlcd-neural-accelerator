from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PredictRequest, PredictResponse
from preprocessor import downsample_28_to_20
from simulator import run_simulation_async

app = FastAPI(
    title="DLCD Neural Accelerator API",
    description="Modular backend API for hardware-in-the-loop digit classification via Icarus Verilog",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint confirming API status."""
    return {"status": "ok", "service": "DLCD Neural Accelerator"}

@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest) -> PredictResponse:
    """Run Verilog hardware simulation for a drawn 28x28 digit."""
    try:
        grid_20 = downsample_28_to_20(payload.image)
        return await run_simulation_async(grid_20)
    except RuntimeError as err:
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")
