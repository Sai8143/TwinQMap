from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CalibrationCreate(BaseModel):
    """
    DTO schema for submitting a new qubit calibration entry.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    epoch_number: int = Field(..., description="Chronological calibration epoch")
    t1: float = Field(..., description="Longitudinal relaxation time (microseconds)")
    t2: float = Field(..., description="Transverse dephasing time (microseconds)")
    readout_error: float = Field(..., description="Readout error rate")
    single_gate_error: float = Field(..., description="Single-qubit gate error rate")
    two_gate_error: float = Field(..., description="Two-qubit gate error rate")
    frequency: float = Field(..., description="Operating frequency (GHz)")
    temperature: float = Field(..., description="Temperature (Kelvin)")
    noise_drift: Optional[float] = Field(default=0.0)
    drift_rate: Optional[float] = Field(default=0.0)
    backend_status: Optional[str] = Field(default="Active")
    backend_name: str = Field(..., description="Quantum system model")


class CalibrationResponse(BaseModel):
    """
    DTO schema for API responses representing a calibration entry.
    """
    id: str = Field(..., alias="id")
    qubit_id: str
    epoch_number: int
    t1: float
    t2: float
    readout_error: float
    single_gate_error: float
    two_gate_error: float
    frequency: float
    temperature: float
    noise_drift: float
    drift_rate: float
    backend_status: str
    timestamp: datetime
    backend_name: str
    version: int

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
