from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TwinCreate(BaseModel):
    """
    DTO schema for initializing a new Qubit Digital Twin.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    status: Optional[str] = Field(default="Dormant", description="Initial lifecycle state")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TwinUpdate(BaseModel):
    """
    DTO schema for updating Digital Twin fields manually.
    """
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TwinVersionResponse(BaseModel):
    """
    DTO schema representing a twin version history entry.
    """
    version: int
    parent_version: Optional[int]
    timestamp: datetime
    calibration_data: Dict[str, Any]
    delta_from_previous: Dict[str, Any]
    drift_values: Dict[str, Any]
    change_reason: str


class DigitalTwinResponse(BaseModel):
    """
    DTO schema for returning the current state of a Digital Twin.
    """
    id: str = Field(..., alias="id")
    qubit_id: str
    status: str
    current_version: int
    last_updated: datetime
    version_history: List[TwinVersionResponse]
    history_buffer: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    version: int
    is_deleted: bool

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }
