from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FeedbackRequest, FeedbackResponse
from app.crud import create_feedback, get_incident_log_by_id

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    incident = get_incident_log_by_id(db, request.incident_log_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="해당 incident_log_id에 대한 incident log가 존재하지 않습니다."
        )

    feedback = create_feedback(
        db=db,
        incident_log_id=request.incident_log_id,
        rating=request.rating,
        feedback_text=request.feedback_text,
        is_helpful=request.is_helpful
    )

    return FeedbackResponse(
        id=feedback.id,
        incident_log_id=feedback.incident_log_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        is_helpful=feedback.is_helpful
    )