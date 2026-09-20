from motor.motor_asyncio import AsyncIOMotorClient
from backend.config.settings import settings
from backend.core.logging import mongodb_logger
from backend.core.exceptions import DatabaseException
from typing import Optional

class MongoDBManager:
    """
    Singleton manager for MongoDB connection lifecycle using Motor.
    """
    client: Optional[AsyncIOMotorClient] = None
    db_name: str = settings.MONGODB_DB_NAME

    @classmethod
    async def connect(cls):
        """
        Initializes the async Motor client.
        """
        if cls.client is None:
            try:
                mongodb_logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
                cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
                # Quick verification of server connection
                await cls.client.admin.command('ping')
                mongodb_logger.info("MongoDB connection established successfully.")
            except Exception as e:
                mongodb_logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise DatabaseException("Database connection failed", detail={"error": str(e)})

    @classmethod
    async def disconnect(cls):
        """
        Closes the Motor client.
        """
        if cls.client is not None:
            mongodb_logger.info("Closing MongoDB connection...")
            cls.client.close()
            cls.client = None
            mongodb_logger.info("MongoDB connection closed.")

    @classmethod
    def get_database(cls):
        """
        Returns the active MongoDB database instance.
        """
        if cls.client is None:
            raise DatabaseException("MongoDB client is not initialized. Call connect() first.")
        return cls.client[cls.db_name]

    @classmethod
    def get_database_by_qubits(cls, qubit_count: int):
        """
        Returns a specific MongoDB database instance based on qubit count configuration.
        Splits data into 'twinq_map_ibm', 'twinq_map_ionq', and 'twinq_map_mathematical'.
        """
        if cls.client is None:
            raise DatabaseException("MongoDB client is not initialized. Call connect() first.")
        if qubit_count == 133:
            db_name = "twinq_map_ibm"
        elif qubit_count in (11, 25):
            db_name = "twinq_map_ionq"
        else:
            db_name = "twinq_map_mathematical"
        return cls.client[db_name]


async def get_db():
    """
    FastAPI dependency that returns the database session.
    """
    yield MongoDBManager.get_database()
