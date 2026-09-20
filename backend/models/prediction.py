from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import Field
from backend.models.base import DBModel

class PredictionHistory(DBModel):
    """
    MongoDB database model representing forecasted qubit calibration predictions.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    prediction_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of forecast execution")
    prediction_horizon: int = Field(..., description="Forecast horizon in hours (e.g. 24)")
    predicted_calibration: Dict[str, Any] = Field(..., description="Forecasted T1, T2, gate, and readout errors")
    prediction_confidence: float = Field(default=1.0, description="Evaluated forecast confidence score (0.0 to 1.0)")
    prediction_model: str = Field(..., description="ML algorithm classification name")
    prediction_version: str = Field(..., description="ML model training version")

    class Config:
        json_schema_extra = {
            "example": {
                "qubit_id": "Q0",
                "prediction_time": "2026-07-02T23:54:26Z",
                "prediction_horizon": 24,
                "predicted_calibration": {
                    "t1": 115.2,
                    "t2": 82.5,
                    "readout_error": 0.016
                },
                "prediction_confidence": 0.945,
                "prediction_model": "RandomForestRegressor",
                "prediction_version": "v1.0.0"
            }
        }
