from typing import Any, Dict, Generic, List, Optional, TypeVar
from backend.repositories.base import BaseRepository, T
from backend.core.logging import general_logger
from backend.core.exceptions import NotFoundException

# Define type variable representing the database model
M = TypeVar("M", bound=BaseRepository)

class BaseService(Generic[T, M]):
    """
    Generic Base Service class encapsulating common business logic and orchestrating repositories.
    """
    def __init__(self, repository: M):
        self.repository = repository

    async def get_by_id(self, id_str: str) -> T:
        """
        Retrieves a resource by ID. Raises NotFoundException if missing.
        """
        resource = await self.repository.get_by_id(id_str)
        if not resource:
            general_logger.warning(f"Resource with ID {id_str} not found in repository.")
            raise NotFoundException(f"Resource with ID {id_str} could not be found.")
        return resource

    async def get_all(
        self,
        filter_query: Optional[Dict[str, Any]] = None,
        sort_by: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[T]:
        """
        Retrieves a filtered, paginated list of resources.
        """
        return await self.repository.get_all(
            filter_query=filter_query,
            sort_by=sort_by,
            limit=limit,
            skip=skip
        )

    async def create(self, entity: T) -> T:
        """
        Creates a new resource record.
        """
        general_logger.info(f"Creating new resource entity: {entity.__class__.__name__}")
        return await self.repository.create(entity)

    async def update(self, id_str: str, update_data: Dict[str, Any]) -> T:
        """
        Updates an existing resource record. Raises NotFoundException if missing.
        """
        updated_resource = await self.repository.update(id_str, update_data)
        if not updated_resource:
            general_logger.warning(f"Failed to update. Resource with ID {id_str} not found.")
            raise NotFoundException(f"Resource with ID {id_str} could not be found to update.")
        general_logger.info(f"Resource ID {id_str} updated successfully.")
        return updated_resource

    async def delete(self, id_str: str) -> None:
        """
        Deletes a resource record. Raises NotFoundException if missing.
        """
        deleted = await self.repository.delete(id_str)
        if not deleted:
            general_logger.warning(f"Failed to delete. Resource with ID {id_str} not found.")
            raise NotFoundException(f"Resource with ID {id_str} could not be found to delete.")
        general_logger.info(f"Resource ID {id_str} deleted successfully.")
