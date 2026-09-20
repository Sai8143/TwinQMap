from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from backend.repositories.calibration import CalibrationRepository
from backend.models.calibration import CalibrationHistory
from backend.services.base import BaseService

class CalibrationService(BaseService[CalibrationHistory, CalibrationRepository]):
    """
    Service class managing business logic for Calibration logs.
    """
    def __init__(self, repository: CalibrationRepository):
        super().__init__(repository)

    async def get_history_by_qubit(
        self, qubit_id: str, limit: int = 100, skip: int = 0
    ) -> List[CalibrationHistory]:
        """
        Retrieves historical calibrations for a physical qubit, sorted chronologically.
        """
        return await self.repository.get_history_by_qubit(qubit_id, limit, skip)
