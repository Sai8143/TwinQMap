from typing import Any, Dict, Optional
from pydantic import Field
from backend.models.base import DBModel

class Qubit(DBModel):
    """
    MongoDB database model representing a physical qubit in the quantum processor.
    """
    qubit_id: str = Field(..., description="Qubit label, e.g. 'Q0'")
    physical_qubit_number: int = Field(..., description="Index of physical qubit in coupling graph")
    logical_qubit_number: Optional[int] = Field(default=None, description="Index of current logical qubit mapped to this physical node")
    backend_name: str = Field(..., description="Name of the quantum hardware platform (e.g. 'ibm_sherbrooke')")
    backend_type: str = Field(..., description="Type of processor technology, e.g. 'superconducting', 'trapped_ion'")
    status: str = Field(default="Dormant", description="Lifecycle state of the physical node")
    frequency: float = Field(default=5.0, description="Operating frequency of the qubit (GHz)")
    temperature: float = Field(default=0.015, description="Operating temperature of the QPU (Kelvin)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary for arbitrary hardware specs")

    class Config:
        json_schema_extra = {
            "example": {
                "qubit_id": "Q0",
                "physical_qubit_number": 0,
                "logical_qubit_number": None,
                "backend_name": "TwinQ_Math_Simulator_5Q",
                "backend_type": "superconducting",
                "status": "Initialized",
                "frequency": 5.12,
                "temperature": 0.015,
                "metadata": {}
            }
        }
