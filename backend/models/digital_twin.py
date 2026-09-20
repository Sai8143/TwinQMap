from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.models.base import DBModel

class TwinVersionSnapshot(BaseModel):
    """
    Sub-model representing a snapshot commit in the Digital Twin version history.
    """
    version: int = Field(..., description="Snapshot version index")
    parent_version: Optional[int] = Field(default=None, description="Previous version number reference")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Commit timestamp")
    calibration_data: Dict[str, Any] = Field(..., description="Qubit calibration values snapshot")
    delta_from_previous: Dict[str, Any] = Field(default_factory=dict, description="Numerical deltas of calibration compared to parent")
    drift_values: Dict[str, Any] = Field(default_factory=dict, description="Computed hourly drift metrics since parent")
    change_reason: str = Field(default="Synchronization Update", description="Metadata description of update triggering this version")


class DigitalTwin(DBModel):
    """
    MongoDB database model representing a physical qubit's Digital Twin.
    Each twin handles rolling history buffers, state snapshotting, and rollbacks.
    """
    qubit_id: str = Field(..., description="Target physical qubit ID (e.g. Q0)")
    status: str = Field(default="Dormant", description="Digital twin lifecycle state")
    current_version: int = Field(default=1, description="Latest committed twin configuration version")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of last update")
    version_history: List[TwinVersionSnapshot] = Field(default_factory=list, description="Chronological commit stack for version tracking")
    history_buffer: List[Dict[str, Any]] = Field(default_factory=list, description="FIFO rolling window of recent calibrations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "qubit_id": "Q0",
                "status": "Initialized",
                "current_version": 1,
                "version_history": [],
                "history_buffer": [],
                "metadata": {}
            }
        }
