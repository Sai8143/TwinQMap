from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.models.base import DBModel
from backend.core.exceptions import DatabaseException
from backend.core.logging import mongodb_logger

# Define a generic type bounded by DBModel
T = TypeVar("T", bound=DBModel)

class BaseRepository(Generic[T]):
    """
    Generic asynchronous Repository class implementing typical CRUD operations in MongoDB.
    """
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_type: Type[T]):
        self.db = db
        self.collection = db[collection_name]
        self.model_type = model_type

    async def get_by_id(self, id_str: str) -> Optional[T]:
        """
        Retrieves a document by its hexadecimal string representation of ObjectId.
        """
        try:
            if not ObjectId.is_valid(id_str):
                return None
            document = await self.collection.find_one({"_id": ObjectId(id_str)})
            return self.model_type.model_validate(document) if document else None
        except Exception as e:
            mongodb_logger.error(f"Error fetching document by ID in {self.collection.name}: {str(e)}")
            raise DatabaseException(f"Failed to fetch document: {str(e)}")

    async def get_all(
        self,
        filter_query: Optional[Dict[str, Any]] = None,
        sort_by: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[T]:
        """
        Retrieves a list of documents matching the specified filter query.
        """
        try:
            filter_query = filter_query or {}
            cursor = self.collection.find(filter_query).skip(skip).limit(limit)
            if sort_by:
                cursor = cursor.sort(sort_by)
            
            results = []
            async for doc in cursor:
                results.append(self.model_type.model_validate(doc))
            return results
        except Exception as e:
            mongodb_logger.error(f"Error listing documents in {self.collection.name}: {str(e)}")
            raise DatabaseException(f"Failed to list documents: {str(e)}")

    async def create(self, entity: T) -> T:
        """
        Inserts a new document model into the database.
        """
        try:
            bson_data = entity.to_bson()
            # If ID is provided, verify or discard if empty
            if "_id" in bson_data and bson_data["_id"] is None:
                del bson_data["_id"]

            result = await self.collection.insert_one(bson_data)
            entity.id = str(result.inserted_id)
            return entity
        except Exception as e:
            mongodb_logger.error(f"Error creating document in {self.collection.name}: {str(e)}")
            raise DatabaseException(f"Failed to create document: {str(e)}")

    async def update(self, id_str: str, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Updates fields of an existing document matching the specified ID.
        """
        try:
            if not ObjectId.is_valid(id_str):
                return None
            
            # Ensure timestamps update
            from datetime import datetime, timezone
            update_data["updated_at"] = datetime.now(timezone.utc)

            # Prevent overwriting _id field
            if "_id" in update_data:
                del update_data["_id"]

            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(id_str)},
                {"$set": update_data},
                return_document=True
            )
            return self.model_type.model_validate(result) if result else None
        except Exception as e:
            mongodb_logger.error(f"Error updating document in {self.collection.name}: {str(e)}")
            raise DatabaseException(f"Failed to update document: {str(e)}")

    async def delete(self, id_str: str) -> bool:
        """
        Deletes a document matching the specified ID from the database.
        """
        try:
            if not ObjectId.is_valid(id_str):
                return False
            result = await self.collection.delete_one({"_id": ObjectId(id_str)})
            return result.deleted_count > 0
        except Exception as e:
            mongodb_logger.error(f"Error deleting document in {self.collection.name}: {str(e)}")
            raise DatabaseException(f"Failed to delete document: {str(e)}")
