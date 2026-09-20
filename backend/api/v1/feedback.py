from fastapi import APIRouter, Depends, status, Query
from typing import List
from backend.schemas.feedback import FeedbackCreate, FeedbackResponse
from backend.services.feedback import FeedbackService
from backend.models.feedback import FeedbackHistory
from backend.core.dependencies import get_feedback_service, get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/quantum/feedback", tags=["ML Predictions Feedback Loop"])

@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert a new predictions vs actual observations feedback entry"
)
async def insert_feedback(
    feedback_data: FeedbackCreate,
    service: FeedbackService = Depends(get_feedback_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits a prediction error comparison log entry.
    """
    feedback = FeedbackHistory(
        predicted_values=feedback_data.predicted_values,
        observed_values=feedback_data.observed_values,
        prediction_error=feedback_data.prediction_error,
        training_status=feedback_data.training_status or "Completed"
    )
    feedback.record_audit("Feedback Entry Logged", user_id=str(current_user.id))
    return await service.create(feedback)


@router.get(
    "/history",
    response_model=List[FeedbackResponse],
    summary="Retrieve prediction feedback history list"
)
async def get_feedback_history(
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    service: FeedbackService = Depends(get_feedback_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns pagination feedback records list.
    """
    return await service.get_all(
        filter_query={"is_deleted": False},
        sort_by=[("feedback_timestamp", -1)],
        limit=limit,
        skip=skip
    )
