from typing import List, Optional
from backend.repositories.execution import ExecutionRepository
from backend.models.execution import ExecutionHistory
from backend.services.base import BaseService

class ExecutionService(BaseService[ExecutionHistory, ExecutionRepository]):
    """
    Service class managing business logic for Execution records.
    """
    def __init__(self, repository: ExecutionRepository):
        super().__init__(repository)

    async def get_by_execution_id(self, execution_id: str) -> Optional[ExecutionHistory]:
        """
        Retrieves a job execution by ID.
        """
        return await self.repository.get_by_execution_id(execution_id)
