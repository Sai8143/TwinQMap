from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.models.feedback import FeedbackHistory
from backend.repositories.base import BaseRepository

class FeedbackRepository(BaseRepository[FeedbackHistory]):
    """
    Repository for FeedbackHistory collection management.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, DBCollections.FEEDBACK_HISTORY, FeedbackHistory)
