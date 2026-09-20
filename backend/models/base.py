from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator

# Custom Pydantic type representing MongoDB BSON ObjectId as string.
PyObjectId = Annotated[
    str,
    BeforeValidator(lambda x: str(x) if isinstance(x, ObjectId) else x)
]


class DBModel(BaseModel):
    """
    Base database model for all MongoDB collections.
    Includes ID, timestamps, versioning, soft deletes, and audit trails.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    version: int = Field(default=1)
    is_deleted: bool = Field(default=False)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

    def to_bson(self) -> Dict[str, Any]:
        """
        Converts the model to a BSON-serializable dictionary for Motor driver.
        """
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        return data

    def record_audit(self, action: str, user_id: Optional[str] = None):
        """
        Appends an entry to the audit trail.
        """
        self.audit_trail.append({
            "action": action,
            "user_id": user_id or "system",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.updated_at = datetime.now(timezone.utc)
