from backend.repositories.feedback import FeedbackRepository
from backend.models.feedback import FeedbackHistory
from backend.services.base import BaseService

class FeedbackService(BaseService[FeedbackHistory, FeedbackRepository]):
    """
    Service class managing business logic for ML Feedback histories.
    """
    def __init__(self, repository: FeedbackRepository):
        super().__init__(repository)
