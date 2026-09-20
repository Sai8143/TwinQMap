from typing import Any, Dict, List
from pydantic import Field
from backend.models.base import DBModel

class ExecutionHistory(DBModel):
    """
    MongoDB database model representing a physical circuit execution job result.
    """
    execution_id: str = Field(..., description="Unique job execution identifier")
    circuit_id: str = Field(..., description="Target compiled logical circuit ID")
    logical_qubits: int = Field(..., description="Number of logical qubits in circuit")
    physical_mapping: List[int] = Field(..., description="Layout mapping list from logical index to physical index")
    execution_time: float = Field(..., description="Elapsed execution run time in seconds")
    execution_result: Dict[str, Any] = Field(..., description="Output statistics counts (e.g. {'00': 500, '11': 524})")
    execution_success: bool = Field(..., description="Status flag of success execution")
    latency: float = Field(default=0.0, description="Queue and API latency overhead in seconds")
    noise: float = Field(default=0.0, description="Estimated average physical error or noise level of execution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata context")

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "job_987",
                "circuit_id": "circ_001",
                "logical_qubits": 2,
                "physical_mapping": [0, 1],
                "execution_time": 0.045,
                "execution_result": {"00": 512, "11": 512},
                "execution_success": True,
                "latency": 1.2,
                "noise": 0.015,
                "metadata": {}
            }
        }
