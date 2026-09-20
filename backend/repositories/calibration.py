from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.calibration import CalibrationHistory
from backend.repositories.base import BaseRepository

class CalibrationRepository(BaseRepository[CalibrationHistory]):
    """
    Repository for CalibrationHistory collection.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.CALIBRATION_HISTORY, CalibrationHistory)

    async def get_by_qubit_and_epoch(self, qubit_id: str, epoch_number: int) -> Optional[CalibrationHistory]:
        """
        Retrieves a calibration entry by qubit ID and epoch number.
        """
        results = await self.get_all(
            filter_query={"qubit_id": qubit_id, "epoch_number": epoch_number, "is_deleted": False}
        )
        return results[0] if results else None

    async def get_history_by_qubit(
        self, qubit_id: str, limit: int = 100, skip: int = 0
    ) -> List[CalibrationHistory]:
        """
        Retrieves calibration history for a qubit sorted by timestamp descending.
        """
        return await self.get_all(
            filter_query={"qubit_id": qubit_id, "is_deleted": False},
            sort_by=[("timestamp", -1)],
            limit=limit,
            skip=skip
        )
