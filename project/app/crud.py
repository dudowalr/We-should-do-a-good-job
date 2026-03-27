from sqlalchemy.orm import Session
from app.models import IncidentLog, UserFeedback, CsvAnalysisLog

def get_incident_log_by_id(db: Session, incident_log_id: int):
    return db.query(IncidentLog).filter(IncidentLog.id == incident_log_id).first()


def create_incident_log(
    db: Session,
    session_id: str | None,
    input_features_json: dict,
    predicted_label: str | None,
    confidence_score: float | None,
    kill_chain_stage: str | None = None,
    defense_mechanism: str | None = None,
    llm_recommendation: str | None = None
):
    incident = IncidentLog(
        session_id=session_id,
        input_features_json=input_features_json,
        predicted_label=predicted_label,
        confidence_score=confidence_score,
        kill_chain_stage=kill_chain_stage,
        defense_mechanism=defense_mechanism,
        llm_recommendation=llm_recommendation
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def create_feedback(
    db: Session,
    incident_log_id: int,
    rating: int | None = None,
    feedback_text: str | None = None,
    is_helpful: bool | None = None
):
    feedback = UserFeedback(
        incident_log_id=incident_log_id,
        rating=rating,
        feedback_text=feedback_text,
        is_helpful=is_helpful
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def create_csv_analysis_log(
    db: Session,
    session_id: str | None = None,
    result_file_name: str | None = None,
    query_text: str | None = None,
    matched_rows_count: int | None = None,
    summary_text: str | None = None,
    openai_analysis: str | None = None
):
    log = CsvAnalysisLog(
        session_id=session_id,
        result_file_name=result_file_name,
        query_text=query_text,
        matched_rows_count=matched_rows_count,
        summary_text=summary_text,
        openai_analysis=openai_analysis
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log