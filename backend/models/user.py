from pydantic import EmailStr, Field
from backend.models.base import DBModel
from backend.config.constants import UserRoles

class User(DBModel):
    """
    MongoDB database model representing a User in TwinQ-Map.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    role: str = Field(default=UserRoles.VIEWER)
    is_active: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "quantum_dev",
                "email": "dev@twinqmap.org",
                "role": "researcher",
                "is_active": True
            }
        }
