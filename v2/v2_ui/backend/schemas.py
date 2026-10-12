from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class PredictRequest(BaseModel):
    image: List[List[float]] = Field(
        ...,
        description="28x28 normalized grayscale pixel matrix with values in range [0.0, 1.0]"
    )

    @field_validator("image")
    @classmethod
    def validate_dimensions(cls, v: List[List[float]]) -> List[List[float]]:
        if len(v) != 28:
            raise ValueError(f"Input image must have exactly 28 rows, got {len(v)}.")
        for row_idx, row in enumerate(v):
            if len(row) != 28:
                raise ValueError(f"Row {row_idx} must have exactly 28 columns, got {len(row)}.")
        return v

class PredictResponse(BaseModel):
    prediction: int = Field(..., description="Predicted digit (0-9)")
    logits: List[float] = Field(..., description="Raw output logits before argmax")
    dense1: List[float] = Field(default_factory=list, description="Intermediate activations of Dense 1 (64 units)")
    dense2: List[float] = Field(default_factory=list, description="Intermediate activations of Dense 2 (32 units)")
    input: List[List[float]] = Field(..., description="Downsampled 20x20 input image sent to hardware")
    mp1: List[List[List[float]]] = Field(..., description="MaxPool1 4x10x10 feature maps")
    mp2: List[List[List[float]]] = Field(..., description="MaxPool2 8x5x5 feature maps")
