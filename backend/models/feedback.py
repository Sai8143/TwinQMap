from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import Field
from backend.models.base import DBModel

class FeedbackHistory(DBModel):
    """
    MongoDB database model representing forecasting predictions vs actual calibrations feedback loop.
    """
    predicted_values: Dict[str, Any] = Field(..., description="Target calibration metrics predicted by ML model")
    observed_values: Dict[str, Any] = Field(..., description="Target calibration metrics actually observed from hardware")
    prediction_error: Dict[str, Any] = Field(..., description="Calculated error metrics (e.g. delta, MSE)")
    feedback_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time of comparison check")
    training_status: str = Field(default="Completed", description="Status showing if feedback triggered model retraining")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_values": {"t1": 95.0, "readout_error": 0.015},
                "observed_values": {"t1": 96.2, "readout_error": 0.0148},
                "prediction_error": {"t1_delta": 1.2, "readout_delta": -0.0002},
                "feedback_timestamp": "2026-07-02T23:54:26Z",
                "training_status": "Retraining_Not_Required"
            }
        }
