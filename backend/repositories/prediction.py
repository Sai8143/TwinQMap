from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.prediction import PredictionHistory
from backend.repositories.base import BaseRepository

class PredictionRepository(BaseRepository[PredictionHistory]):
    """
    Repository for PredictionHistory collection management.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.PREDICTION_HISTORY, PredictionHistory)
