from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CsvAnalysisRequest, CsvAnalysisResponse
from app.crud import create_csv_analysis_log

router = APIRouter()

@router.post("/", response_model=CsvAnalysisResponse)
def save_csv_analysis(request: CsvAnalysisRequest, db: Session = Depends(get_db)):
    matched_rows_count = request.matched_rows_count
    summary_text = request.summary_text
    openai_analysis = request.openai_analysis
    
    log = create_csv_analysis_log(
        db=db,
        session_id=request.session_id,
        result_file_name=request.result_file_name,
        query_text=request.query_text,
        matched_rows_count=matched_rows_count,
        summary_text=summary_text,
        openai_analysis=openai_analysis
    )

    return CsvAnalysisResponse(
        id=log.id,
        session_id=log.session_id,
        result_file_name=log.result_file_name,
        query_text=log.query_text,
        matched_rows_count=log.matched_rows_count,
        summary_text=log.summary_text,
        openai_analysis=log.openai_analysis
    )