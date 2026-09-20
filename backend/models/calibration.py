from datetime import datetime, timezone
from pydantic import Field
from backend.models.base import DBModel

class CalibrationHistory(DBModel):
    """
    MongoDB database model representing a historical calibration snapshot for a qubit.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    epoch_number: int = Field(..., description="Chronological calibration epoch identifier")
    t1: float = Field(..., description="Decayed longitudinal relaxation time (T1) in microseconds")
    t2: float = Field(..., description="Decayed transverse dephasing time (T2) in microseconds")
    readout_error: float = Field(..., description="Readout measurement error rate")
    single_gate_error: float = Field(..., description="Single-qubit gate error rate")
    two_gate_error: float = Field(..., description="Two-qubit gate error rate")
    frequency: float = Field(..., description="Qubit operating frequency (GHz)")
    temperature: float = Field(..., description="QPU temperature (Kelvin)")
    noise_drift: float = Field(default=0.0, description="Evaluated noise drift from previous epoch baseline")
    drift_rate: float = Field(default=0.0, description="Calculated rate of drift per hour")
    backend_status: str = Field(default="Active", description="Backend operational status description")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time of calibration recording")
    backend_name: str = Field(..., description="Target hardware system name")

    class Config:
        json_schema_extra = {
            "example": {
                "qubit_id": "Q0",
                "epoch_number": 0,
                "t1": 100.0,
                "t2": 80.0,
                "readout_error": 0.01,
                "single_gate_error": 0.0005,
                "two_gate_error": 0.010,
                "frequency": 5.0,
                "temperature": 0.015,
                "noise_drift": 0.0,
                "drift_rate": 0.0,
                "backend_status": "Active",
                "backend_name": "TwinQ_Math_Simulator_5Q"
            }
        }
