from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat_with_analysis

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = chat_with_analysis(
            analysis_context=request.analysis_context,
            chat_history=request.chat_history,
            question=request.question,
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 응답 생성 중 오류 발생: {str(e)}")