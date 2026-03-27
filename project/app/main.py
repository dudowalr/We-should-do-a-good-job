from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import predict, feedback, csv_analysis, chat


app = FastAPI(title="Cyber Threat Prediction API")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1>서버 정상 작동!</h1>"

app.include_router(predict.router, prefix="/predict", tags=["Predict"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(csv_analysis.router, prefix="/csv-analysis", tags=["CSV Analysis"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


## 최종 코드 병합 시 지워야될 메모
# frontend, logs, output 폴더는 테스트를 위한 부분이지 백엔드가아님
# 나중에 작업하고 지우기