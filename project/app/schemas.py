from typing import Optional, Dict, Any, List
from pydantic import BaseModel

# Predict
class PredictRequest(BaseModel):
    session_id: Optional[str] = None
    input_features_json: Dict[str, Any]

class PredictResponse(BaseModel):
    id: int
    predicted_label: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None
    anomaly_summary: Optional[str] = None
    # kill_chain_stage: Optional[str] = None
    defense_mechanism: Optional[str] = None
    llm_recommendation: Optional[str] = None


# Feedback
class FeedbackRequest(BaseModel):
    incident_log_id: int
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    is_helpful: Optional[bool] = None

class FeedbackResponse(BaseModel):
    id: int
    incident_log_id: int
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    is_helpful: Optional[bool] = None


# csv_analysis
class CsvAnalysisRequest(BaseModel):
    session_id: Optional[str] = None
    result_file_name: Optional[str] = None
    query_text: Optional[str] = None
    matched_rows_count: Optional[int] = None
    summary_text: Optional[str] = None
    openai_analysis: Optional[str] = None


class CsvAnalysisResponse(BaseModel):
    id: int
    session_id: Optional[str] = None
    result_file_name: Optional[str] = None
    query_text: Optional[str] = None
    matched_rows_count: Optional[int] = None
    summary_text: Optional[str] = None
    openai_analysis: Optional[str] = None


# chat
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    analysis_context: str
    chat_history: List[ChatMessage]
    question: str


class ChatResponse(BaseModel):
    answer: str
