from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.execution import ExecutionHistory
from backend.repositories.base import BaseRepository

class ExecutionRepository(BaseRepository[ExecutionHistory]):
    """
    Repository for ExecutionHistory collection management.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.EXECUTION_HISTORY, ExecutionHistory)

    async def get_by_execution_id(self, execution_id: str) -> Optional[ExecutionHistory]:
        """
        Retrieves a specific execution log by its job ID.
        """
        results = await self.get_all(filter_query={"execution_id": execution_id, "is_deleted": False})
        return results[0] if results else None
