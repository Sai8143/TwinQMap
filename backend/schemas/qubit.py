from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class QubitCreate(BaseModel):
    """
    DTO schema for registering a physical qubit.
    """
    qubit_id: str = Field(..., description="Unique physical label, e.g. 'Q0'")
    physical_qubit_number: int = Field(..., description="Physical node ID index")
    logical_qubit_number: Optional[int] = Field(default=None, description="Logical qubit index map")
    backend_name: str = Field(..., description="Quantum system platform")
    backend_type: str = Field(..., description="Hardware technology classification")
    status: Optional[str] = Field(default="Dormant", description="Status code")
    frequency: Optional[float] = Field(default=5.0)
    temperature: Optional[float] = Field(default=0.015)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class QubitUpdate(BaseModel):
    """
    DTO schema for updating physical qubit attributes.
    """
    logical_qubit_number: Optional[int] = None
    status: Optional[str] = None
    frequency: Optional[float] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class QubitResponse(BaseModel):
    """
    DTO schema for API responses representing a Qubit.
    """
    id: str = Field(..., alias="id")
    qubit_id: str
    physical_qubit_number: int
    logical_qubit_number: Optional[int]
    backend_name: str
    backend_type: str
    status: str
    frequency: float
    temperature: float
    metadata: Dict[str, Any]
    version: int
    is_deleted: bool

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
