from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    """
    DTO schema for submitting comparing prediction feedback details.
    """
    predicted_values: Dict[str, Any] = Field(..., description="Predicted calibration parameters")
    observed_values: Dict[str, Any] = Field(..., description="Actual calibration values observed")
    prediction_error: Dict[str, Any] = Field(..., description="Numerical discrepancies evaluation")
    training_status: Optional[str] = Field(default="Completed")


class FeedbackResponse(BaseModel):
    """
    DTO schema representing forecasting feedback results.
    """
    id: str = Field(..., alias="id")
    predicted_values: Dict[str, Any]
    observed_values: Dict[str, Any]
    prediction_error: Dict[str, Any]
    feedback_timestamp: datetime
    training_status: str

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
