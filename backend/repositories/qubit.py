from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.qubit import Qubit
from backend.repositories.base import BaseRepository

class QubitRepository(BaseRepository[Qubit]):
    """
    Repository for Qubits collection management.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.QUBITS, Qubit)

    async def get_active_qubits(self) -> List[Qubit]:
        """
        Retrieves all non-deleted active status qubits.
        """
        return await self.get_all(filter_query={"is_deleted": False})

    async def get_by_qubit_id(self, qubit_id: str) -> Optional[Qubit]:
        """
        Retrieves a qubit by its label identifier (e.g. Q0).
        """
        results = await self.get_all(filter_query={"qubit_id": qubit_id, "is_deleted": False})
        return results[0] if results else None
