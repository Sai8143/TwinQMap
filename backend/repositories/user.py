from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.user import User
from backend.repositories.base import BaseRepository
from backend.core.exceptions import DatabaseException
from backend.core.logging import mongodb_logger

class UserRepository(BaseRepository[User]):
    """
    User collection repository implementing user-specific data access methods.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.USERS, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user document by their unique username.
        """
        try:
            document = await self.collection.find_one({"username": username})
            return User.model_validate(document) if document else None
        except Exception as e:
            mongodb_logger.error(f"Error fetching user by username '{username}': {str(e)}")
            raise DatabaseException(f"Failed to fetch user by username: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user document by their unique email.
        """
        try:
            document = await self.collection.find_one({"email": email})
            return User.model_validate(document) if document else None
        except Exception as e:
            mongodb_logger.error(f"Error fetching user by email '{email}': {str(e)}")
            raise DatabaseException(f"Failed to fetch user by email: {str(e)}")
