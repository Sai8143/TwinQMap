from typing import Any, Dict, List, Optional
from backend.repositories.qubit import QubitRepository
from backend.models.qubit import Qubit
from backend.services.base import BaseService
from backend.core.logging import general_logger
from backend.core.exceptions import NotFoundException

class QubitService(BaseService[Qubit, QubitRepository]):
    """
    Service class managing business logic for physical qubits,
    enforcing audit trails and soft deletes.
    """
    def __init__(self, repository: QubitRepository):
        super().__init__(repository)

    async def create_qubit(self, qubit: Qubit, user_id: Optional[str] = None) -> Qubit:
        """
        Creates a physical qubit entry and registers creation audit logs.
        """
        qubit.record_audit("Qubit Initialized", user_id)
        return await self.create(qubit)

    async def update_qubit(self, id_str: str, update_data: Dict[str, Any], user_id: Optional[str] = None) -> Qubit:
        """
        Updates qubit configurations, incrementing document version number and logging audit trails.
        """
        current = await self.get_by_id(id_str)
        
        # Prepare updates
        update_data["version"] = current.version + 1
        current.version += 1
        current.record_audit("Qubit Properties Updated", user_id)
        update_data["audit_trail"] = [a for a in current.audit_trail]
        
        return await self.update(id_str, update_data)

    async def soft_delete_qubit(self, id_str: str, user_id: Optional[str] = None) -> None:
        """
        Performs a soft delete by marking is_deleted = True and appending audit notes.
        """
        current = await self.get_by_id(id_str)
        current.version += 1
        current.record_audit("Qubit Soft Deleted", user_id)
        
        update_data = {
            "is_deleted": True,
            "version": current.version,
            "audit_trail": current.audit_trail
        }
        await self.update(id_str, update_data)
