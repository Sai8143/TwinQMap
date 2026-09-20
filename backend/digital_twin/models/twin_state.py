from datetime import datetime
from pydantic import Field
from backend.models.base import DBModel

class QubitDigitalTwinState(DBModel):
    """
    State representation of a single physical Qubit's Digital Twin.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    physical_t1: float = Field(..., description="Currently tracked T1 coherence (microseconds)")
    physical_t2: float = Field(..., description="Currently tracked T2 coherence (microseconds)")
    physical_readout_error: float = Field(..., description="Currently tracked readout error rate")
    physical_gate_error_1q: float = Field(..., description="Tracked single-qubit gate error rate")
    physical_gate_error_2q: float = Field(..., description="Tracked two-qubit gate error rate")
    predicted_t1_drift: float = Field(default=0.0, description="Estimated drift rate of T1 per hour")
    predicted_t2_drift: float = Field(default=0.0, description="Estimated drift rate of T2 per hour")
    predicted_readout_drift: float = Field(default=0.0, description="Estimated drift rate of readout error per hour")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
