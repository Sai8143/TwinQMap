from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.digital_twin import DigitalTwin
from backend.repositories.base import BaseRepository

class DigitalTwinRepository(BaseRepository[DigitalTwin]):
    """
    Repository for DigitalTwins collection management.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.DIGITAL_TWINS, DigitalTwin)

    async def get_by_qubit_id(self, qubit_id: str) -> Optional[DigitalTwin]:
        """
        Retrieves the active (non-deleted) digital twin configuration of a physical qubit.
        """
        results = await self.get_all(filter_query={"qubit_id": qubit_id, "is_deleted": False})
        return results[0] if results else None
