from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from schemas import PredictRequest, PredictResponse, V1PredictResponse, ComparePredictResponse
from preprocessor import downsample_28_to_20
from simulator import run_simulation_async
from v1_runner import get_v1_emulator

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
    """Run Verilog hardware simulation for a drawn 28x28 digit (V2 CNN)."""
    try:
        grid_20 = downsample_28_to_20(payload.image)
        return await run_simulation_async(grid_20)
    except RuntimeError as err:
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

@app.post("/predict/v1", response_model=V1PredictResponse)
async def predict_v1(payload: PredictRequest) -> V1PredictResponse:
    """Run bit-exact Q7.8 inference for Version 1 MLP architecture."""
    try:
        v1_emu = get_v1_emulator()
        grid_10 = await asyncio.to_thread(v1_emu.downsample_28_to_10, payload.image)
        pred, logits, l1, l2 = await asyncio.to_thread(v1_emu.forward, grid_10)
        return V1PredictResponse(
            prediction=pred,
            logits=logits,
            layer1=l1,
            layer2=l2,
            input_10x10=grid_10,
            cycles=6139,
            accuracy_baseline=93.06
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"V1 simulation failed: {err}")

@app.post("/predict/compare", response_model=ComparePredictResponse)
async def predict_compare(payload: PredictRequest) -> ComparePredictResponse:
    """Run concurrent evaluation of both Version 1 and Version 2 for side-by-side comparison."""
    try:
        # Run V2 RTL simulation and V1 Q7.8 in parallel
        v1_emu = get_v1_emulator()
        grid_10 = v1_emu.downsample_28_to_10(payload.image)
        v1_task = asyncio.to_thread(v1_emu.forward, grid_10)
        
        grid_20 = downsample_28_to_20(payload.image)
        v2_task = run_simulation_async(grid_20)

        v1_res, v2_res = await asyncio.gather(v1_task, v2_task)
        v1_pred, v1_logits, v1_l1, v1_l2 = v1_res

        v1_response = V1PredictResponse(
            prediction=v1_pred,
            logits=v1_logits,
            layer1=v1_l1,
            layer2=v1_l2,
            input_10x10=grid_10,
            cycles=6139,
            accuracy_baseline=93.06
        )

        return ComparePredictResponse(
            v1=v1_response,
            v2=v2_res,
            agreement=(v1_pred == v2_res.prediction)
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Comparison execution failed: {err}")
