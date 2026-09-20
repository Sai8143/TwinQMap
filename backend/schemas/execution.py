from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ExecutionCreate(BaseModel):
    """
    DTO schema for submitting a new circuit execution log.
    """
    execution_id: str = Field(..., description="Unique hardware job ID")
    circuit_id: str = Field(..., description="Target program identifier")
    logical_qubits: int = Field(..., description="Logical width of circuit")
    physical_mapping: List[int] = Field(..., description="Mapping allocation list")
    execution_time: float = Field(..., description="Compiler run time in seconds")
    execution_result: Dict[str, Any] = Field(..., description="Readout counts payload")
    execution_success: bool = Field(..., description="Job success state")
    latency: Optional[float] = Field(default=0.0)
    noise: Optional[float] = Field(default=0.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """
    DTO schema representing an execution run log response.
    """
    id: str = Field(..., alias="id")
    execution_id: str
    circuit_id: str
    logical_qubits: int
    physical_mapping: List[int]
    execution_time: float
    execution_result: Dict[str, Any]
    execution_success: bool
    latency: float
    noise: float
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
